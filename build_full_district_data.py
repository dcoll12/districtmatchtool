#!/usr/bin/env python3
"""
Build a complete district_data.json for all 92 Indiana counties.

Since we cannot fetch county boundary polygons from the network, this
script uses hardcoded county centroids for all 92 Indiana counties and
samples a 5x5 grid of points within each county's approximate area.
Each sample point is tested against every HD/SD/CD polygon via
ray-casting point-in-polygon (mirrors find_cd9_districts.py).

The union of all matched districts for each county is stored in the JSON.

Run:
    python build_full_district_data.py
"""

import json
import re
import sys


# ── All 92 Indiana counties: (name, lat, lon, half-span-degrees) ──────
# half-span controls the 5x5 sampling grid around the centroid.
# Smaller counties get a tighter span to avoid sampling into neighbors.

INDIANA_COUNTIES = [
    ("Adams",        40.745, -84.940, 0.12),
    ("Allen",        41.085, -85.065, 0.18),
    ("Bartholomew",  39.205, -85.895, 0.13),
    ("Benton",       40.600, -87.300, 0.14),
    ("Blackford",    40.470, -85.320, 0.08),
    ("Boone",        40.050, -86.470, 0.14),
    ("Brown",        39.205, -86.230, 0.11),
    ("Carroll",      40.580, -86.560, 0.13),
    ("Cass",         40.770, -86.340, 0.13),
    ("Clark",        38.480, -85.720, 0.12),
    ("Clay",         39.380, -87.115, 0.12),
    ("Clinton",      40.300, -86.470, 0.13),
    ("Crawford",     38.295, -86.445, 0.11),
    ("Daviess",      38.695, -87.070, 0.13),
    ("Dearborn",     39.125, -84.975, 0.10),
    ("Decatur",      39.320, -85.495, 0.13),
    ("DeKalb",       41.400, -84.800, 0.13),
    ("Delaware",     40.230, -85.395, 0.13),
    ("Dubois",       38.370, -86.870, 0.13),
    ("Elkhart",      41.600, -85.850, 0.14),
    ("Fayette",      39.635, -85.160, 0.09),
    ("Floyd",        38.320, -85.900, 0.09),
    ("Fountain",     40.115, -87.245, 0.11),
    ("Franklin",     39.415, -85.065, 0.13),
    ("Fulton",       41.055, -86.265, 0.12),
    ("Gibson",       38.305, -87.585, 0.14),
    ("Grant",        40.515, -85.650, 0.13),
    ("Greene",       38.980, -86.965, 0.15),
    ("Hamilton",     40.055, -86.045, 0.14),
    ("Hancock",      39.830, -85.770, 0.12),
    ("Harrison",     38.190, -86.105, 0.13),
    ("Hendricks",    39.770, -86.505, 0.13),
    ("Henry",        39.930, -85.380, 0.13),
    ("Howard",       40.485, -86.115, 0.12),
    ("Huntington",   40.825, -85.500, 0.12),
    ("Jackson",      38.920, -86.040, 0.14),
    ("Jasper",       41.010, -87.115, 0.15),
    ("Jay",          40.440, -85.000, 0.13),
    ("Jefferson",    38.780, -85.430, 0.11),
    ("Jennings",     39.020, -85.620, 0.11),
    ("Johnson",      39.535, -86.095, 0.13),
    ("Knox",         38.695, -87.415, 0.15),
    ("Kosciusko",    41.245, -85.865, 0.16),
    ("LaGrange",     41.645, -85.425, 0.12),
    ("Lake",         41.480, -87.330, 0.14),
    ("LaPorte",      41.545, -86.735, 0.16),
    ("Lawrence",     38.845, -86.490, 0.14),
    ("Madison",      40.165, -85.720, 0.14),
    ("Marion",       39.790, -86.150, 0.17),
    ("Marshall",     41.325, -86.275, 0.13),
    ("Martin",       38.695, -86.800, 0.11),
    ("Miami",        40.790, -85.995, 0.12),
    ("Monroe",       39.165, -86.525, 0.14),
    ("Montgomery",   40.055, -86.875, 0.13),
    ("Morgan",       39.480, -86.440, 0.13),
    ("Newton",       41.070, -87.440, 0.14),
    ("Noble",        41.400, -85.420, 0.13),
    ("Ohio",         38.945, -84.970, 0.06),
    ("Orange",       38.545, -86.495, 0.12),
    ("Owen",         39.310, -86.840, 0.12),
    ("Parke",        39.790, -87.195, 0.14),
    ("Perry",        38.080, -86.630, 0.12),
    ("Pike",         38.400, -87.215, 0.11),
    ("Porter",       41.530, -87.070, 0.12),
    ("Posey",        37.965, -87.905, 0.12),
    ("Pulaski",      41.040, -86.695, 0.14),
    ("Putnam",       39.665, -86.885, 0.14),
    ("Randolph",     40.155, -85.000, 0.14),
    ("Ripley",       39.105, -85.270, 0.13),
    ("Rush",         39.625, -85.445, 0.12),
    ("St. Joseph",   41.615, -86.285, 0.15),
    ("Scott",        38.690, -85.750, 0.09),
    ("Shelby",       39.530, -85.785, 0.14),
    ("Spencer",      38.020, -87.000, 0.13),
    ("Starke",       41.285, -86.630, 0.12),
    ("Steuben",      41.645, -85.010, 0.11),
    ("Sullivan",     39.090, -87.415, 0.12),
    ("Switzerland",  38.835, -85.020, 0.09),
    ("Tippecanoe",   40.395, -86.870, 0.15),
    ("Tipton",       40.295, -86.035, 0.10),
    ("Union",        39.625, -84.920, 0.07),
    ("Vanderburgh",  37.975, -87.565, 0.12),
    ("Vermillion",   39.840, -87.445, 0.10),
    ("Vigo",         39.505, -87.395, 0.13),
    ("Wabash",       40.800, -85.790, 0.13),
    ("Warren",       40.350, -87.365, 0.12),
    ("Warrick",      38.100, -87.275, 0.12),
    ("Washington",   38.600, -86.130, 0.14),
    ("Wayne",        39.855, -84.985, 0.14),
    ("Wells",        40.740, -85.225, 0.12),
    ("White",        40.745, -86.870, 0.14),
    ("Whitley",      41.135, -85.505, 0.12),
]

assert len(INDIANA_COUNTIES) == 92, f"Expected 92 counties, got {len(INDIANA_COUNTIES)}"


def county_sample_points(lat, lon, span, grid=5):
    """
    Return a grid×grid list of (lon, lat) sample points centered on
    (lat, lon) with ±span degrees in each direction.
    """
    step = (2 * span) / (grid - 1) if grid > 1 else 0
    pts = []
    for i in range(grid):
        for j in range(grid):
            slat = lat - span + i * step
            slon = lon - span + j * step
            pts.append((slon, slat))
    return pts


# ── KML parsing ───────────────────────────────────────────────────────

def parse_kml_districts(path):
    """Return dict: district_name -> list of rings [(lon,lat),...]."""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    districts = {}
    placemarks = re.findall(r'<Placemark>(.*?)</Placemark>', text, re.DOTALL)

    for pm in placemarks:
        m = re.search(r'<name>(.*?)</name>', pm)
        if not m:
            continue
        name = m.group(1).strip()

        coord_blocks = re.findall(
            r'<coordinates>(.*?)</coordinates>', pm, re.DOTALL)
        rings = []
        for block in coord_blocks:
            pts = []
            for token in block.split():
                parts = token.split(',')
                if len(parts) >= 2:
                    try:
                        pts.append((float(parts[0]), float(parts[1])))
                    except ValueError:
                        pass
            if len(pts) >= 3:
                rings.append(pts)

        if rings:
            if name in districts:
                districts[name].extend(rings)
            else:
                districts[name] = rings

    return districts


# ── Geometry helpers ──────────────────────────────────────────────────

def _point_in_ring(px, py, ring):
    n = len(ring)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if ((yi > py) != (yj > py)) and (
                px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def point_in_district(px, py, rings):
    """Ray-casting PIP respecting holes."""
    if not rings:
        return False
    if not _point_in_ring(px, py, rings[0]):
        return False
    for hole in rings[1:]:
        if _point_in_ring(px, py, hole):
            return False
    return True


def county_matches_district(sample_pts, dist_rings):
    """Return True if any sample point falls inside the district polygon."""
    for px, py in sample_pts:
        if point_in_district(px, py, dist_rings):
            return True
    return False


# ── Main ──────────────────────────────────────────────────────────────

def main():
    hd_file = "Indiana_House_Districts_2024.kml"
    sd_file = "Indiana_Senate_Districts_2024.kml"
    cd_file = "Indiana_Congressional_Districts_119th.kml"
    out_file = "district_data.json"

    print("Parsing KML files...")
    hds = parse_kml_districts(hd_file)
    sds = parse_kml_districts(sd_file)
    cds = parse_kml_districts(cd_file)
    print(f"  House districts        : {len(hds)}")
    print(f"  Senate districts       : {len(sds)}")
    print(f"  Congressional districts: {len(cds)}")
    print()

    print(f"Processing {len(INDIANA_COUNTIES)} counties...")
    county_to_hds = {}
    county_to_sds = {}
    county_to_cds = {}
    hd_to_counties = {k: [] for k in hds}
    sd_to_counties = {k: [] for k in sds}
    cd_to_counties = {k: [] for k in cds}

    for county_name, lat, lon, span in INDIANA_COUNTIES:
        pts = county_sample_points(lat, lon, span, grid=5)

        matched_hds = sorted(
            int(k) for k, rings in hds.items()
            if county_matches_district(pts, rings)
        )
        matched_sds = sorted(
            int(k) for k, rings in sds.items()
            if county_matches_district(pts, rings)
        )
        matched_cds = sorted(
            int(k) for k, rings in cds.items()
            if county_matches_district(pts, rings)
        )

        county_to_hds[county_name] = matched_hds
        county_to_sds[county_name] = matched_sds
        county_to_cds[county_name] = matched_cds

        for k in hds:
            if int(k) in matched_hds:
                hd_to_counties[k].append(county_name)
        for k in sds:
            if int(k) in matched_sds:
                sd_to_counties[k].append(county_name)
        for k in cds:
            if int(k) in matched_cds:
                cd_to_counties[k].append(county_name)

        print(f"  {county_name:<20}  HDs={matched_hds}  "
              f"SDs={matched_sds}  CDs={matched_cds}")

    print()

    # CD → HD/SD geometry-based overlap maps (same vertex-sampling as
    # find_cd9_districts.py but for all CDs)
    print("Computing CD → HD/SD overlap maps...")

    def districts_intersect(rings_a, rings_b, step=5):
        for ring in rings_a:
            for pt in ring[::step]:
                if point_in_district(pt[0], pt[1], rings_b):
                    return True
        for ring in rings_b:
            for pt in ring[::step]:
                if point_in_district(pt[0], pt[1], rings_a):
                    return True
        return False

    cd_to_hds = {}
    cd_to_sds = {}
    for cd_name, cd_rings in cds.items():
        cd_to_hds[cd_name] = sorted(
            int(k) for k, hd_rings in hds.items()
            if districts_intersect(cd_rings, hd_rings)
        )
        cd_to_sds[cd_name] = sorted(
            int(k) for k, sd_rings in sds.items()
            if districts_intersect(cd_rings, sd_rings)
        )
        print(f"  CD {cd_name}: {len(cd_to_hds[cd_name])} HDs, "
              f"{len(cd_to_sds[cd_name])} SDs")

    print()

    data = {
        "hd_to_counties": {str(k): v for k, v in hd_to_counties.items()},
        "sd_to_counties": {str(k): v for k, v in sd_to_counties.items()},
        "cd_to_counties": {str(k): v for k, v in cd_to_counties.items()},
        "county_to_hds":  county_to_hds,
        "county_to_sds":  county_to_sds,
        "county_to_cds":  county_to_cds,
        "all_counties":   sorted(c[0] for c in INDIANA_COUNTIES),
        "cd_to_hds":      cd_to_hds,
        "cd_to_sds":      cd_to_sds,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Written to {out_file}")
    print(f"  Counties        : {len(INDIANA_COUNTIES)}")
    print(f"  House districts : {len(hds)}")
    print(f"  Senate districts: {len(sds)}")
    print(f"  Cong. districts : {len(cds)}")


if __name__ == "__main__":
    sys.setrecursionlimit(5000)
    main()
