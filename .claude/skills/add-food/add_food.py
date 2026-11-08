#!/usr/bin/env python3
"""Safely add one or more foods to vault/<pin>/shared/foods (the "My Food" library).

Field-level REST PATCH with updateMask=foods.<id> — it only ADDS new ids and never
touches or removes existing foods. Backs up before/after and verifies that every
existing food is byte-for-byte unchanged and the count rose by exactly the number added.

The PIN is a secret (see CLAUDE.local.md) and is NOT stored here — pass it with --pin.

Usage:
  python3 -I add_food.py --pin <PIN> --json '[{"name":"ไก่ย่าง","p":27,"c":0,"f":8,"kcal":188,"unit":"ชิ้น","amt":1,"g":100}]'
Options:
  --pin      REQUIRED, Firestore path secret (read it from CLAUDE.local.md; never commit it)
  --project  (default tdee-521a9 — this is public, in firebase-config.js)
  --out      backup dir (default backups)
  --force    allow adding a food whose name already exists
  --dry-run  show what would be written, write nothing

Each food object: name,p,c,f,kcal required; unit (default "หน่วย"), amt (default 1),
g (grams/serving, optional), barcode (optional), serving (optional, default "<amt> <unit>").
p/c/f/kcal are PER SERVING (per "<amt> <unit>").
"""
import argparse, datetime, json, os, sys, urllib.request, urllib.parse

BASE = "https://firestore.googleapis.com/v1/projects/{p}/databases/(default)/documents/{path}"

def url(project, pin):
    return BASE.format(p=project, path=f"vault/{pin}/shared/foods")

def fetch(project, pin):
    with urllib.request.urlopen(url(project, pin)) as r:
        return json.load(r)

def patch(project, pin, field_path, body):
    u = url(project, pin) + "?updateMask.fieldPaths=" + urllib.parse.quote(field_path, safe="")
    req = urllib.request.Request(u, data=json.dumps(body).encode(), method="PATCH",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def gen_id(existing):
    import random, string
    alpha = string.digits + string.ascii_lowercase
    while True:
        i = "".join(random.choice(alpha) for _ in range(7))
        if i not in existing:
            return i

def num(x):
    return float(x)

def typed_food(f):
    """Build Firestore typed mapValue fields for one food object."""
    name = str(f["name"]).strip()
    p, c, ff, kcal = num(f["p"]), num(f["c"]), num(f["f"]), num(f["kcal"])
    unit = str(f.get("unit") or "หน่วย").strip()
    amt = f.get("amt", 1)
    g = f.get("g", None)
    barcode = f.get("barcode", None)
    serving = f.get("serving") or f"{amt:g} {unit}"
    fields = {
        "name": {"stringValue": name},
        "p": {"doubleValue": p},
        "c": {"doubleValue": c},
        "f": {"doubleValue": ff},
        "kcal": {"integerValue": str(int(round(kcal)))},
        "amt": {"integerValue": str(int(amt))},
        "unit": {"stringValue": unit},
        "serving": {"stringValue": serving},
        "units": {"arrayValue": {"values": []}},
        "barcode": {"nullValue": None} if barcode in (None, "") else {"stringValue": str(barcode)},
        "g": {"nullValue": None} if g in (None, "") else {"integerValue": str(int(round(num(g))))},
        "created": {"integerValue": str(int(datetime.datetime.now().timestamp() * 1000))},
    }
    return name, {"mapValue": {"fields": fields}}

def foods_of(doc):
    return (doc.get("fields", {}).get("foods", {}).get("mapValue", {}) or {}).get("fields", {}) or {}

def save(outdir, tag, data):
    os.makedirs(outdir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(outdir, f"addfood-{ts}-{tag}.json")
    with open(path, "w") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    return path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pin", required=True)
    ap.add_argument("--project", default="tdee-521a9")
    ap.add_argument("--out", default="backups")
    ap.add_argument("--json", required=True, help="JSON array of food objects")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    try:
        items = json.loads(a.json)
    except Exception as e:
        sys.exit(f"ERROR: --json is not valid JSON: {e}")
    if isinstance(items, dict):
        items = [items]
    if not items:
        sys.exit("ERROR: no foods given")

    before = fetch(a.project, a.pin)
    existing = foods_of(before)
    existing_names = {existing[i]["mapValue"]["fields"]["name"]["stringValue"].strip().lower()
                      for i in existing if "name" in existing[i].get("mapValue", {}).get("fields", {})}
    n0 = len(existing)
    print(f"My Food ก่อนเพิ่ม: {n0} รายการ")

    planned = []
    used = set(existing.keys())
    for f in items:
        name, val = typed_food(f)
        warn = ""
        kc = num(f["kcal"]); est = 4*num(f["p"]) + 4*num(f["c"]) + 9*num(f["f"])
        if est > 0 and abs(kc - est) / est > 0.15:
            warn += f"  ⚠ kcal {kc:g} ต่างจาก 4·P+4·C+9·F={est:.0f} เกิน 15%"
        if name.strip().lower() in existing_names and not a.force:
            print(f"ข้าม (ชื่อซ้ำ ใช้ --force ถ้าต้องการเพิ่มซ้ำ): {name}")
            continue
        nid = gen_id(used); used.add(nid)
        planned.append((nid, name, val, f))
        print(f"เตรียมเพิ่ม: {nid}  {name}  "
              f"P{num(f['p']):g}/C{num(f['c']):g}/F{num(f['f']):g} {int(round(kc))}kcal{warn}")

    if not planned:
        sys.exit("ไม่มีรายการให้เพิ่ม")
    if a.dry_run:
        print("DRY-RUN: ไม่ได้เขียนข้อมูล")
        return

    bpath = save(a.out, "before", before)
    for nid, name, val, _ in planned:
        body = {"fields": {"foods": {"mapValue": {"fields": {nid: val}}}}}
        patch(a.project, a.pin, f"foods.{nid}", body)

    after = fetch(a.project, a.pin)
    apath = save(a.out, "after", after)
    now = foods_of(after)
    added = {nid for nid, *_ in planned}

    # SAFETY: every existing food unchanged, nothing removed, count delta exact.
    removed = set(existing.keys()) - set(now.keys())
    changed = [i for i in existing if i in now and json.dumps(now[i], sort_keys=True) != json.dumps(existing[i], sort_keys=True)]
    missing = [nid for nid in added if nid not in now]
    ok = not removed and not changed and not missing and len(now) == n0 + len(planned)

    print(f"My Food หลังเพิ่ม: {len(now)} รายการ (ควรได้ {n0 + len(planned)})")
    print(f"backup: {bpath}  →  {apath}")
    if removed: print(f"‼ หายไป: {sorted(removed)}")
    if changed: print(f"‼ ของเดิมถูกแก้: {changed}")
    if missing: print(f"‼ เพิ่มไม่สำเร็จ: {missing}")
    print("RESULT:", "OK ✅" if ok else "FAIL ‼ (ตรวจ backup ด้านบน)")
    if ok:
        for nid, name, *_ in planned:
            print(f"  + {nid}  {name}")
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
