#!/usr/bin/env python3
"""
Update district_data.json using authoritative precinct-level data from the
Office of Census Data shapefile (2026_Precincts_JAN_21_2026.xlsx).

Each row in the Excel file represents one precinct and records its
Congressional (C), Senate (S), and House (H) district assignments.

This replaces the KML vertex-sampling approximations for:
  - cd_to_hds  : which HDs fall (even partially) within each CD
  - cd_to_sds  : which SDs fall (even partially) within each CD
  - hd_to_cd   : the dominant CD for each HD (by precinct count)
  - sd_to_cd   : the dominant CD for each SD (by precinct count)
"""

import json
import openpyxl
from collections import defaultdict, Counter


def main():
    xlsx_path = "2026_Precincts_JAN_21_2026.xlsx"
    json_path  = "district_data.json"

    print(f"Reading {xlsx_path}...")
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active

    # Authoritative sets: which HDs/SDs touch each CD
    cd_to_hds: dict[int, set] = defaultdict(set)
    cd_to_sds: dict[int, set] = defaultdict(set)

    # Direct SD↔HD overlap from precinct data
    sd_to_hds: dict[int, set] = defaultdict(set)
    hd_to_sds: dict[int, set] = defaultdict(set)

    # Precinct counts per district, used to assign dominant CD
    hd_cd_counts: dict[int, Counter] = defaultdict(Counter)
    sd_cd_counts: dict[int, Counter] = defaultdict(Counter)

    rows_read = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        county, county_name, c, s, h = row
        if c is None or s is None or h is None:
            continue
        c, s, h = int(c), int(s), int(h)
        rows_read += 1

        cd_to_hds[c].add(h)
        cd_to_sds[c].add(s)
        sd_to_hds[s].add(h)
        hd_to_sds[h].add(s)
        hd_cd_counts[h][c] += 1
        sd_cd_counts[s][c] += 1

    print(f"  Processed {rows_read} precinct rows")
    print(f"  CDs found : {sorted(cd_to_hds.keys())}")

    # Dominant CD per HD/SD (most precincts)
    hd_to_cd = {str(h): max(cds, key=cds.get)
                for h, cds in hd_cd_counts.items()}
    sd_to_cd = {str(s): max(cds, key=cds.get)
                for s, cds in sd_cd_counts.items()}

    # Sort for clean JSON output
    cd_to_hds_out = {str(cd): sorted(hds)
                     for cd, hds in sorted(cd_to_hds.items())}
    cd_to_sds_out = {str(cd): sorted(sds)
                     for cd, sds in sorted(cd_to_sds.items())}
    sd_to_hds_out = {str(sd): sorted(hds)
                     for sd, hds in sorted(sd_to_hds.items())}
    hd_to_sds_out = {str(hd): sorted(sds)
                     for hd, sds in sorted(hd_to_sds.items())}

    # Load existing data (preserves county-level fields we are not changing)
    print(f"Reading {json_path}...")
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Show what changed before updating
    old_cd_to_hds = data.get("cd_to_hds", {})
    old_cd_to_sds = data.get("cd_to_sds", {})
    old_hd_to_cd  = data.get("hd_to_cd", {})
    old_sd_to_cd  = data.get("sd_to_cd", {})

    print("\n=== cd_to_hds changes ===")
    for cd in sorted(set(list(cd_to_hds_out) + list(old_cd_to_hds)), key=int):
        new = set(cd_to_hds_out.get(cd, []))
        old = set(old_cd_to_hds.get(cd, []))
        added   = sorted(new - old)
        removed = sorted(old - new)
        if added or removed:
            print(f"  CD {cd}: +{added}  -{removed}")
        else:
            print(f"  CD {cd}: no change ({len(new)} HDs)")

    print("\n=== cd_to_sds changes ===")
    for cd in sorted(set(list(cd_to_sds_out) + list(old_cd_to_sds)), key=int):
        new = set(cd_to_sds_out.get(cd, []))
        old = set(old_cd_to_sds.get(cd, []))
        added   = sorted(new - old)
        removed = sorted(old - new)
        if added or removed:
            print(f"  CD {cd}: +{added}  -{removed}")
        else:
            print(f"  CD {cd}: no change ({len(new)} SDs)")

    print("\n=== hd_to_cd changes ===")
    changed = 0
    for hd in sorted(set(list(hd_to_cd) + list(old_hd_to_cd)), key=int):
        n = hd_to_cd.get(hd)
        o = old_hd_to_cd.get(hd)
        if n != o:
            print(f"  HD {hd}: {o} → {n}")
            changed += 1
    print(f"  {changed} HD→CD assignments changed")

    print("\n=== sd_to_cd changes ===")
    changed = 0
    for sd in sorted(set(list(sd_to_cd) + list(old_sd_to_cd)), key=int):
        n = sd_to_cd.get(sd)
        o = old_sd_to_cd.get(sd)
        if n != o:
            print(f"  SD {sd}: {o} → {n}")
            changed += 1
    print(f"  {changed} SD→CD assignments changed")

    # Apply updates
    data["cd_to_hds"] = cd_to_hds_out
    data["cd_to_sds"] = cd_to_sds_out
    data["sd_to_hds"] = sd_to_hds_out
    data["hd_to_sds"] = hd_to_sds_out
    data["hd_to_cd"]  = hd_to_cd
    data["sd_to_cd"]  = sd_to_cd

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\nUpdated {json_path}")
    for cd in sorted(cd_to_hds_out, key=int):
        print(f"  CD {cd}: {len(cd_to_hds_out[cd])} HDs, "
              f"{len(cd_to_sds_out[cd])} SDs")


if __name__ == "__main__":
    main()
