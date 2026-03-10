import json
import streamlit as st

st.set_page_config(
    page_title="Indiana District Lookup",
    page_icon="🏛️",
    layout="centered",
)

# ── Load data ────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    with open("district_data.json", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# ── Header ───────────────────────────────────────────────────────────

st.title("🏛️ Indiana District Lookup Tool")
st.caption("Find which House, Senate, and Congressional districts overlap for any Indiana county or district.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Counties", len(data["all_counties"]))
col2.metric("House Districts", len(data["hd_to_counties"]))
col3.metric("Senate Districts", len(data["sd_to_counties"]))
col4.metric("Congressional Districts", len(data["cd_to_counties"]))

st.divider()

# ── Tab layout ───────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📍 Lookup by County", "🔢 Lookup by District"])

# ── Tab 1: County → Districts ────────────────────────────────────────

with tab1:
    st.subheader("Find Districts for a County")

    county = st.selectbox(
        "Select a county",
        options=[""] + data["all_counties"],
        index=0,
    )

    if county:
        hds = sorted(data["county_to_hds"].get(county, []))
        sds = sorted(data["county_to_sds"].get(county, []))
        cds = sorted(data["county_to_cds"].get(county, []))

        st.markdown(f"### 📍 {county} County")

        r1, r2, r3 = st.columns(3)

        with r1:
            st.markdown("**House Districts**")
            if hds:
                for d in hds:
                    st.success(f"HD {d}")
            else:
                st.info("None found")

        with r2:
            st.markdown("**Senate Districts**")
            if sds:
                for d in sds:
                    st.warning(f"SD {d}")
            else:
                st.info("None found")

        with r3:
            st.markdown("**Congressional Districts**")
            if cds:
                for d in cds:
                    st.error(f"CD {d}")
            else:
                st.info("None found")

# ── Tab 2: District → Counties + Overlapping districts ───────────────

with tab2:
    st.subheader("Find Counties & Overlapping Districts")
    st.caption("Enter one or more district numbers to find the counties they cover and all overlapping districts.")

    c1, c2, c3 = st.columns(3)
    with c1:
        hd_input = st.text_input("House District (HD)", placeholder="e.g. 62")
    with c2:
        sd_input = st.text_input("Senate District (SD)", placeholder="e.g. 44")
    with c3:
        cd_input = st.text_input("Congressional District (CD)", placeholder="e.g. 9")

    search = st.button("Find Counties & Related Districts", type="primary")

    if search or hd_input or sd_input or cd_input:
        hd = hd_input.strip()
        sd = sd_input.strip()
        cd = cd_input.strip()

        if not hd and not sd and not cd:
            st.warning("Please enter at least one district number.")
        else:
            errors = []

            # Validate inputs
            if hd and hd not in data["hd_to_counties"]:
                errors.append(f"House District {hd} not found in data.")
            if sd and sd not in data["sd_to_counties"]:
                errors.append(f"Senate District {sd} not found in data.")
            if cd and cd not in data["cd_to_counties"]:
                errors.append(f"Congressional District {cd} not found in data.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Build the county set (intersection when multiple entered)
                known_counties = set()

                if hd:
                    hd_counties = set(data["hd_to_counties"][hd])
                    known_counties = hd_counties if not known_counties else known_counties & hd_counties
                    if not known_counties:
                        known_counties = hd_counties

                if sd:
                    sd_counties = set(data["sd_to_counties"][sd])
                    if known_counties:
                        intersect = known_counties & sd_counties
                        known_counties = intersect if intersect else known_counties | sd_counties
                    else:
                        known_counties = sd_counties

                if cd:
                    cd_counties = set(data["cd_to_counties"][cd])
                    if known_counties:
                        intersect = known_counties & cd_counties
                        known_counties = intersect if intersect else known_counties | cd_counties
                    else:
                        known_counties = cd_counties

                # ── Input summary ────────────────────────────────────
                st.markdown("**You searched for:**")
                badges = []
                if hd:
                    badges.append(f"`HD {hd}`")
                if sd:
                    badges.append(f"`SD {sd}`")
                if cd:
                    badges.append(f"`CD {cd}`")
                st.markdown("  ".join(badges))

                # ── Counties covered ─────────────────────────────────
                if known_counties:
                    st.markdown("---")
                    st.markdown(f"**📍 Counties Covered ({len(known_counties)})**")
                    county_cols = st.columns(min(len(known_counties), 4))
                    for i, c in enumerate(sorted(known_counties)):
                        county_cols[i % len(county_cols)].info(c)

                # ── Overlapping districts from county data ────────────
                possible_hds = set()
                possible_sds = set()
                possible_cds = set()

                for c in known_counties:
                    for d in data["county_to_hds"].get(c, []):
                        possible_hds.add(d)
                    for d in data["county_to_sds"].get(c, []):
                        possible_sds.add(d)
                    for d in data["county_to_cds"].get(c, []):
                        possible_cds.add(d)

                # If a CD was entered, prefer the geometry-based direct lookup
                if cd and "cd_to_hds" in data and cd in data["cd_to_hds"]:
                    possible_hds = set(data["cd_to_hds"][cd])
                    possible_sds = set(data["cd_to_sds"][cd])
                    st.caption("ℹ️ HD/SD results use geometry-based polygon intersection for this CD.")

                st.markdown("---")
                st.markdown("**🔗 All Overlapping Districts**")

                ov1, ov2, ov3 = st.columns(3)

                with ov1:
                    st.markdown(f"**House Districts ({len(possible_hds)})**")
                    for d in sorted(possible_hds):
                        label = f"HD {d}"
                        if str(d) == hd:
                            st.success(f"**{label}** ✓")
                        else:
                            st.success(label)

                with ov2:
                    st.markdown(f"**Senate Districts ({len(possible_sds)})**")
                    for d in sorted(possible_sds):
                        label = f"SD {d}"
                        if str(d) == sd:
                            st.warning(f"**{label}** ✓")
                        else:
                            st.warning(label)

                with ov3:
                    st.markdown(f"**Congressional Districts ({len(possible_cds)})**")
                    for d in sorted(possible_cds):
                        label = f"CD {d}"
                        if str(d) == cd:
                            st.error(f"**{label}** ✓")
                        else:
                            st.error(label)
