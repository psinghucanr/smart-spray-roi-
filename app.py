import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


st.set_page_config(page_title="Smart Spray ROI Calculator", layout="centered")
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Smart Spray ROI Calculator")
st.caption("Scenario tool to compare conventional broadcast spraying vs smart spraying.")



st.header("Inputs")

# 1–2) Farm area: integer, renamed
acres = st.number_input(
    "Farm Area (acres)",
    min_value=0,
    value=1000,
    step=10,
    format="%d",
)

# 3–4) Applications per year: integer, renamed
apps_per_year = st.number_input(
    "Number of spray application per year",
    min_value=0,
    value=2,
    step=1,
    format="%d",
)

# 5) Chemical cost + GPA: one decimal
chem_cost_per_ac = st.number_input(
    "Chemical cost per acre (conventional)",
    min_value=0.0,
    value=25.0,
    step=0.1,
    format="%.1f",
)
gpa = st.number_input(
    "Chemical application rate (GPA)",
    min_value=0.0,
    value=10.0,
    step=0.1,
    format="%.1f",
)

# Weed assumptions
weed_coverage_pct = st.slider("Estimated weed coverage (%)", 0.0, 100.0, 20.0, 1.0)

# 6) Rate reduction: no decimal
rate_reduction_pct = st.slider(
    "Rate reduction on weeds (%)",
    0,
    100,
    0,
    1,
    help="How much lower the application rate is on detected weeds. Use 0% if the same rate as conventional is applied.",
)

# 9) Labor cost label change; 7) no decimals
labor_cost_hr = st.number_input(
    "Labor cost ($/hour)",
    min_value=0,
    value=30,
    step=1,
    format="%d",
)

# 8) Speeds: one decimal
conv_speed = st.number_input(
    "Conventional sprayer speed (ac/hr)",
    min_value=0.1,
    value=40.0,
    step=0.1,
    format="%.1f",
)
smart_speed = st.number_input(
    "Smart sprayer speed (ac/hr)",
    min_value=0.1,
    value=30.0,
    step=0.1,
    format="%.1f",
)

# 7) Purchase + service: no decimals
system_cost = st.number_input(
    "Smart sprayer purchase cost ($)",
    min_value=0,
    value=120000,
    step=1000,
    format="%d",
)
annual_service_per_ac = st.number_input(
    "Annual software/service cost ($/acre)",
    min_value=0,
    value=2,
    step=1,
    format="%d",
    help="Annual per-acre subscription fee for software, data services, or ongoing support.",
)

# Depreciation toggle (life years can stay integer)
include_depr = st.checkbox("Include depreciation (annual ownership cost)", value=True)
life_years = (
    st.number_input("Expected machine life (years)", min_value=1, value=7, step=1, format="%d")
    if include_depr
    else None
)

st.header("Results")

# Core annual treated area
total_acres_treated = acres * apps_per_year

# Factors for smart spraying
weed_factor = weed_coverage_pct / 100.0
rate_factor = 1.0 - (rate_reduction_pct / 100.0)
overall_use_factor = weed_factor * rate_factor  # proportion of conventional used by smart
st.subheader("Field visualization (weed coverage)")

# Controls for the visualization (optional but helpful)
base_weeds = st.slider("Weed density (visual only)", 100, 1200, 600, 50)
seed = st.number_input("Random pattern seed (visual only)", min_value=0, value=1, step=1)

# Convert weed coverage (%) into number of weeds drawn
weed_count = int(base_weeds * (weed_coverage_pct / 100.0))

# Make random weed locations (same seed = stable layout)
rng = np.random.default_rng(seed)
x = rng.random(weed_count)
y = rng.random(weed_count)

# Draw field
fig, ax = plt.subplots(figsize=(7, 4))
ax.set_facecolor("#f4f0c3")  # pale yellow field background

# Field boundary
ax.add_patch(plt.Rectangle((0, 0), 1, 1, fill=False, linewidth=2))

# Weeds (blue dots)
ax.scatter(x, y, s=18, alpha=0.9)

# Clean look
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title(f"Weed coverage: {int(weed_coverage_pct)}%  |  Visual weeds: {weed_count}")

st.pyplot(fig)

# Spray volume (gallons)
conv_gallons = total_acres_treated * gpa
smart_gallons = conv_gallons * overall_use_factor

# Conventional costs
conv_chem_total = total_acres_treated * chem_cost_per_ac
conv_hours = total_acres_treated / conv_speed
conv_labor_total = conv_hours * labor_cost_hr
conv_total = conv_chem_total + conv_labor_total

# Smart costs
smart_chem_total = conv_chem_total * overall_use_factor
smart_hours = total_acres_treated / smart_speed
smart_labor_total = smart_hours * labor_cost_hr
smart_service_total = total_acres_treated * annual_service_per_ac
smart_depr_annual = (system_cost / life_years) if include_depr else 0.0

smart_total = smart_chem_total + smart_labor_total + smart_service_total + smart_depr_annual

# Outputs
annual_savings = conv_total - smart_total
payback_years = (system_cost / annual_savings) if annual_savings > 0 else None
roi_pct = (annual_savings / system_cost * 100.0) if system_cost > 0 else None

col1, col2, col3 = st.columns(3)
col1.metric("Annual savings ($)", f"{annual_savings:,.0f}")
col2.metric("ROI (%)", f"{roi_pct:,.1f}" if roi_pct is not None else "—")
col3.metric("Payback (years)", f"{payback_years:,.2f}" if payback_years is not None else "—")

col4, col5 = st.columns(2)
col4.metric("Conventional spray volume (gal/yr)", f"{conv_gallons:,.0f}")
col5.metric("Smart spray volume (gal/yr)", f"{smart_gallons:,.0f}")

with st.expander("Cost breakdown"):
    st.write(f"Total acres treated annually: **{total_acres_treated:,.0f} ac**")
    st.write(f"Application rate: **{gpa:,.1f} GPA**")

    st.write("### Conventional")
    st.write(f"- Chemical: ${conv_chem_total:,.0f}")
    st.write(f"- Spray volume: {conv_gallons:,.0f} gal/year")
    st.write(f"- Labor: ${conv_labor_total:,.0f} ({conv_hours:,.1f} hours)")
    st.write(f"- Total: **${conv_total:,.0f}**")

    st.write("### Smart")
    st.write(f"- Chemical: ${smart_chem_total:,.0f}")
    st.write(f"- Spray volume: {smart_gallons:,.0f} gal/year")
    st.write(f"- Labor: ${smart_labor_total:,.0f} ({smart_hours:,.1f} hours)")
    st.write(f"- Software/service: ${smart_service_total:,.0f}")
    st.write(f"- Depreciation (annual): ${smart_depr_annual:,.0f}")
    st.write(f"- Total: **${smart_total:,.0f}**")

st.info("Tip: Run low/typical/high weed coverage scenarios to see how sensitive results are.")

st.caption(
    "Acknowledgement: This calculator is inspired by the MSU Extension "
    "Smart Spray Annual ROI Calculator "
    "(https://agresearch.montana.edu/narc/Programs_and_projects/narc-precisionag/smart-spray.html)."
)

