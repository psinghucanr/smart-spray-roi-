import streamlit as st

st.set_page_config(page_title="Smart Spray ROI Calculator", layout="centered")

st.title("Smart Spray ROI Calculator")
st.caption("Scenario tool to compare conventional broadcast spraying vs smart spraying.")

st.header("Inputs")

acres = st.number_input("Total acres sprayed per year", min_value=0.0, value=1000.0, step=10.0)
apps_per_year = st.number_input("Number of applications per year", min_value=0.0, value=2.0, step=1.0)

chem_cost_per_ac = st.number_input("Chemical cost per acre (conventional)", min_value=0.0, value=25.0, step=1.0)
weed_coverage_pct = st.slider("Estimated weed coverage (%)", 0.0, 100.0, 20.0, 1.0)
rate_reduction_pct = st.slider("Rate reduction on weeds (%)", 0.0, 100.0, 0.0, 1.0)

labor_cost_hr = st.number_input("Labor cost ($/hour, fully loaded)", min_value=0.0, value=30.0, step=1.0)
conv_speed = st.number_input("Conventional sprayer speed (ac/hr)", min_value=0.01, value=40.0, step=1.0)
smart_speed = st.number_input("Smart sprayer speed (ac/hr)", min_value=0.01, value=30.0, step=1.0)

system_cost = st.number_input("Smart sprayer purchase cost ($)", min_value=0.0, value=120000.0, step=1000.0)
annual_service_per_ac = st.number_input("Annual software/service cost ($/acre)", min_value=0.0, value=2.0, step=0.5)

include_depr = st.checkbox("Include depreciation (annual ownership cost)", value=True)
life_years = st.number_input("Expected machine life (years)", min_value=1.0, value=7.0, step=1.0) if include_depr else None

st.header("Results")

total_acres_treated = acres * apps_per_year

# Conventional costs
conv_chem_total = total_acres_treated * chem_cost_per_ac
conv_hours = total_acres_treated / conv_speed
conv_labor_total = conv_hours * labor_cost_hr
conv_total = conv_chem_total + conv_labor_total

# Smart chemical cost factor
weed_factor = weed_coverage_pct / 100.0
rate_factor = 1.0 - (rate_reduction_pct / 100.0)
smart_chem_total = conv_chem_total * weed_factor * rate_factor

smart_hours = total_acres_treated / smart_speed
smart_labor_total = smart_hours * labor_cost_hr

smart_service_total = total_acres_treated * annual_service_per_ac

smart_depr_annual = (system_cost / life_years) if include_depr else 0.0

smart_total = smart_chem_total + smart_labor_total + smart_service_total + smart_depr_annual

annual_savings = conv_total - smart_total
payback_years = (system_cost / annual_savings) if annual_savings > 0 else None
roi_pct = (annual_savings / system_cost * 100.0) if system_cost > 0 else None

col1, col2, col3 = st.columns(3)
col1.metric("Annual savings ($)", f"{annual_savings:,.0f}")
col2.metric("ROI (%)", f"{roi_pct:,.1f}" if roi_pct is not None else "—")
col3.metric("Payback (years)", f"{payback_years:,.2f}" if payback_years is not None else "—")

with st.expander("Cost breakdown"):
    st.write(f"Total acres treated annually: **{total_acres_treated:,.0f} ac**")
    st.write("### Conventional")
    st.write(f"- Chemical: ${conv_chem_total:,.0f}")
    st.write(f"- Labor: ${conv_labor_total:,.0f} ({conv_hours:,.1f} hours)")
    st.write(f"- Total: **${conv_total:,.0f}**")

    st.write("### Smart")
    st.write(f"- Chemical: ${smart_chem_total:,.0f}")
    st.write(f"- Labor: ${smart_labor_total:,.0f} ({smart_hours:,.1f} hours)")
    st.write(f"- Software/service: ${smart_service_total:,.0f}")
    st.write(f"- Depreciation (annual): ${smart_depr_annual:,.0f}")
    st.write(f"- Total: **${smart_total:,.0f}**")

st.info("Tip: Run low/typical/high weed coverage scenarios to see how sensitive results are.")
