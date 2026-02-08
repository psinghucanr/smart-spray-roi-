import streamlit as st
from io import BytesIO
from datetime import datetime

import streamlit.components.v1 as components


from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import textwrap



st.set_page_config(page_title="Smart Spray ROI Calculator", layout="centered")



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
    help="Total farm acreage treated per spray application."
)

# 3–4) Applications per year: integer, renamed
apps_per_year = st.number_input(
    "Number of spray application per year",
    min_value=0,
    value=2,
    step=1,
    format="%d",
    help="How many times you spray this acreage each year."
)

# 5) Chemical cost + GPA: one decimal
chem_cost_per_ac = st.number_input(
    "Chemical cost per acre (conventional)",
    min_value=0.0,
    value=25.0,
    step=0.1,
    format="%.1f",
    help="Cost of herbicide per acre when spraying the full field (broadcast)."
)
gpa = st.number_input(
    "Chemical application rate (GPA)",
    min_value=0.0,
    value=10.0,
    step=0.1,
    format="%.1f",
    help="Gallons of spray mix applied per acre under conventional broadcast spraying."
)

# Weed assumptions
weed_coverage_pct = st.slider(
    "Estimated weed coverage (%)",
    min_value=0.0,
    max_value=100.0,
    value=20.0,
    step=0.1,
    format="%.1f",
    help="Percent of the field area where weeds are present. Smart spraying targets these zones."
)


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
    help="Hourly cost of the operator’s time (wage + benefits)."
)

# 8) Speeds: one decimal
conv_speed = st.number_input(
    "Conventional sprayer speed (ac/hr)",
    min_value=0.1,
    value=40.0,
    step=0.1,
    format="%.1f",
    help="How many acres per hour your conventional sprayer can cover."
)
smart_speed = st.number_input(
    "Smart sprayer speed (ac/hr)",
    min_value=0.1,
    value=30.0,
    step=0.1,
    format="%.1f",
    help="How many acres per hour the smart sprayer can cover (often slower than conventional)."
)

# 7) Purchase + service: no decimals
system_cost = st.number_input(
    "Smart sprayer purchase cost ($)",
    min_value=0,
    value=120000,
    step=1000,
    format="%d",
    help="Upfront purchase cost of the smart spray equipment."
)

st.caption(f"Formatted: **${system_cost:,}**")

annual_service_per_ac = st.number_input(
    "Annual software/service cost ($/acre)",
    min_value=0,
    value=2,
    step=1,
    format="%d",
    help="Annual per-acre subscription fee for software, data services, or ongoing support.",
)

# Depreciation toggle (life years can stay integer)
include_depr = st.checkbox("Include depreciation (annual ownership cost)", value=True,
 help="If checked, the calculator spreads the equipment purchase cost over its expected life as an annual cost.")
life_years = (
    st.number_input("Expected machine life (years)", min_value=1, value=7, step=1, format="%d",
    help="How many years you expect to use the machine before replacing it."
)
    if include_depr
    else None
)

def build_pdf_report(inputs: dict, results: dict) -> bytes:
    """
    Creates a simple 1–2 page PDF report and returns it as bytes.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Layout helpers
    x_left = 0.75 * inch
    y = height - 0.9 * inch
    line = 0.22 * inch

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_left, y, "Smart Spray ROI Calculator – Scenario Report")
    y -= 0.35 * inch

    c.setFont("Helvetica", 10)
    c.drawString(x_left, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 0.35 * inch

    # Results summary (top)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_left, y, "Results Summary")
    y -= 0.25 * inch

    c.setFont("Helvetica", 11)
    for label, value in results.items():
        c.drawString(x_left, y, f"{label}: {value}")
        y -= line

    y -= 0.15 * inch

    # Inputs
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_left, y, "Inputs Used")
    y -= 0.25 * inch

    c.setFont("Helvetica", 11)
    for label, value in inputs.items():
        # Create new page if needed
        if y < 1.0 * inch:
            c.showPage()
            y = height - 0.9 * inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_left, y, "Inputs Used (continued)")
            y -= 0.35 * inch
            c.setFont("Helvetica", 11)

        c.drawString(x_left, y, f"{label}: {value}")
        y -= line

    # Disclaimer footer
    y -= 0.2 * inch
    if y < 1.2 * inch:
        c.showPage()
        y = height - 0.9 * inch

    c.setFont("Helvetica-Bold", 10)
    c.drawString(x_left, y, "Disclaimer")
    y -= 0.18 * inch
    c.setFont("Helvetica", 9)
    c.drawString(
        x_left,
        y,
        "Educational use only. Estimates depend on user inputs. Not financial or investment advice."
    )

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# --- your metrics here ---


# Core annual treated area
total_acres_treated = acres * apps_per_year

# Factors for smart spraying
weed_factor = weed_coverage_pct / 100.0
rate_factor = 1.0 - (rate_reduction_pct / 100.0)
overall_use_factor = weed_factor * rate_factor  # proportion of conventional used by smart

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

overall_chem_reduction = (1 - overall_use_factor) * 100

roi_text = f"{roi_pct:,.1f}" if roi_pct is not None else "—"
payback_text = f"{payback_years:,.1f}" if payback_years is not None else "—"

roi_text = f"{roi_pct:,.1f}" if roi_pct is not None else "—"
payback_text = f"{payback_years:,.1f}" if payback_years is not None else "—"

results_html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }}

    .results-box {{
      background-color: #fbf2d6;
      border-radius: 12px;
      padding: 10px;
      border: 1px solid rgba(0,0,0,0.06);
      margin-bottom: 16px;
    }}

    .results-title {{
      font-size: 1.2rem;
      font-weight: 700;
      margin: 0 0 12px 0;
      color: #222;
    }}

    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
    }}

    .metric-card {{
      background: rgba(255,255,255,0.9);
      border-radius: 10px;
      padding: 14px;
      border: 1px solid rgba(0,0,0,0.05);
    }}

    .metric-label {{
      font-size: 0.9rem;
      color: #555;
      margin-bottom: 1px;
    }}

    .metric-value {{
      font-size: 1.8rem;
      font-weight: 700;
      color: #111;
      line-height: 1.1;
    }}
  </style>
</head>


<body>
  <div class="results-box">
    <div class="results-title">Summary Results</div>

    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-label">Annual Savings</div>
        <div class="metric-value">${annual_savings:,.0f}</div>
      </div>

      <div class="metric-card">
        <div class="metric-label">ROI (%)</div>
        <div class="metric-value">{roi_text}</div>
      </div>

      <div class="metric-card">
        <div class="metric-label">Payback Period (Years)</div>
        <div class="metric-value">{payback_text}</div>
      </div>

      <div class="metric-card">
        <div class="metric-label">Overall Chemical Reduction (%)</div>
        <div class="metric-value">{overall_chem_reduction:,.1f}</div>
      </div>
    </div>
  </div>
</body>
</html>
"""

components.html(results_html, height=240, scrolling=False)




# --- Prepare report content for PDF download ---
inputs_for_pdf = {
    "Farm Area (acres)": f"{acres:,}",
    "Number of spray applications per year": f"{apps_per_year:,}",
    "Chemical cost per acre (conventional)": f"${chem_cost_per_ac:,.1f}",
    "Chemical application rate (GPA)": f"{gpa:,.1f}",
    "Estimated weed coverage (%)": f"{weed_coverage_pct:.1f}%",
    "Rate reduction on weeds (%)": f"{rate_reduction_pct:,.0f}%",
    "Labor cost ($/hour)": f"${labor_cost_hr:,}",
    "Conventional sprayer speed (ac/hr)": f"{conv_speed:,.1f}",
    "Smart sprayer speed (ac/hr)": f"{smart_speed:,.1f}",
    "Smart sprayer purchase cost ($)": f"${system_cost:,}",
    "Annual software/service cost ($/acre)": f"${annual_service_per_ac:,}",
    "Include depreciation": "Yes" if include_depr else "No",
    "Expected machine life (years)": f"{life_years}" if include_depr else "—",
}

results_for_pdf = {
    "Annual savings ($)": f"${annual_savings:,.0f}",
    "ROI (%)": f"{roi_pct:,.1f}" if roi_pct is not None else "—",
    "Payback (years)": f"{payback_years:,.2f}" if payback_years is not None else "—",
    "Conventional spray volume (gal/yr)": f"{conv_gallons:,.0f}",
    "Smart spray volume (gal/yr)": f"{smart_gallons:,.0f}",
}


pdf_bytes = build_pdf_report(inputs_for_pdf, results_for_pdf)

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
with st.expander("What do these results mean?"):
    st.write("**Annual Savings:** Estimated yearly difference in total cost between conventional and smart spraying (chemical + labor + software/service + optional depreciation).")
    st.write("**ROI (%):** Annual Savings ÷ Smart sprayer purchase cost × 100. (Simple annual return estimate.)")
    st.write("**Payback Period (Years):** Smart sprayer purchase cost ÷ Annual Savings. If savings are ≤ 0, payback is not shown.")
    st.write("**Overall Chemical Reduction (%):** Percent reduction in chemical use compared to broadcast spraying, based on weed coverage and rate reduction.")

# --- small global CSS to style the download button green ---
st.markdown(
    """
    <style>
    /* Target Streamlit's download button wrappers (covers several Streamlit versions) */
    div.stDownloadButton > button,
    div[data-testid="stDownloadButton"] button,
    button[kind="primary"][title^="Download"] {
        background-color: #2ecc71 !important;   /* green */
        border-color: #27ae60 !important;
        color: white !important;
        box-shadow: none !important;
    }
    /* hover */
    div.stDownloadButton > button:hover,
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #27ae60 !important;
        border-color: #219150 !important;
    }

    /* optional: make button text bold and larger */
    div.stDownloadButton > button > div,
    div[data-testid="stDownloadButton"] button > div {
        font-weight: 700;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

    
st.download_button(
    label="Download PDF report for this scenario",
    data=pdf_bytes,
    file_name="smart_spray_roi_scenario_report.pdf",
    mime="application/pdf",
)

st.info("Tip: Run low/typical/high weed coverage scenarios to see how sensitive results are.")

st.markdown("---")
with st.expander("How calculations work"):
    st.write(
        "The calculator compares conventional broadcast spraying with smart (targeted) spraying. "
        "It first estimates how many acres are treated each year based on farm area and number of applications. "
        "Chemical costs for conventional spraying are calculated using cost per acre. "
        "For smart spraying, chemical use is reduced based on estimated weed coverage and any rate reduction on weeds. "
        "Labor costs are estimated using sprayer speed (ac/hr) and labor cost per hour. "
        "Optional depreciation spreads the smart sprayer purchase cost over its expected life. "
        "Annual savings are the difference between conventional and smart total costs, "
        "which are then used to estimate ROI and payback."
    )


st.caption(
    "For details on how calculations are performed, see the calculation documentation below."
)

st.caption(
    "Calculation Documentation: "
    "[Download PDF](https://raw.githubusercontent.com/psinghucanr/smart-spray-roi-/main/"
    "Smart_Spray_ROI_Calculation_Documentation_Detailed.pdf)"
)
st.markdown("---")
st.caption(
    "© 2026 University of California Cooperative Extension. All rights reserved.  \n"
    "Developed by Paramveer Singh, UCCE Monterey County.  \n"
    "Address: 1432 Abbott Street, Salinas, CA 93901."
)
st.markdown("---")
st.caption(
    "Acknowledgement: This tool is inspired by the MSU Extension Smart Spray Annual ROI Calculator "
    "(https://agresearch.montana.edu/narc/Programs_and_projects/narc-precisionag/smart-spray.html), "
    "developed by the Northern Agricultural Research Center (NARC) Precision Agriculture Lab."
)


st.caption(
    "This calculator is intended for educational purposes only and provides estimates "
    "based on user-supplied inputs. Results should not be relied upon as financial, legal, "
    "or investment advice. Users are encouraged to consult qualified financial advisors, "
    "equipment dealers, and Extension specialists before making investment decisions."
)
