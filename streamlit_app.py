import streamlit as st

st.set_page_config(page_title="Rate Calculator", layout="wide")

st.title("Hotel Rate Calculator")

st.markdown("Use this tool to calculate rates or reverse-engineer totals based on taxes and nights.")

# Default tax values
default_state_tax = 6.875
default_city_tax = 0.5
default_lodging_tax = 5.125

st.sidebar.header("Advanced Tax Settings")
state_tax = st.sidebar.number_input("State Tax %", value=default_state_tax, step=0.001)
city_tax = st.sidebar.number_input("City Tax %", value=default_city_tax, step=0.001)
lodging_tax = st.sidebar.number_input("Lodging Tax %", value=default_lodging_tax, step=0.001)

total_tax_percent = state_tax + city_tax + lodging_tax
tax_multiplier = 1 + (total_tax_percent / 100)

# ---- Reverse Rate Section ----
st.header("Reverse Rate Calculator")
st.markdown("Enter a total amount and number of nights to calculate the base rate before tax.")

with st.form("reverse_form"):
    total_input = st.number_input("Total Charge (with tax)", min_value=0.0, step=0.01)
    nights_reverse = st.number_input("Number of Nights", min_value=1, step=1)
    submitted_reverse = st.form_submit_button("Calculate Base Rate")

    if submitted_reverse:
        base_rate = total_input / tax_multiplier / nights_reverse
        st.success(f"Base Rate per Night: ${base_rate:.2f}")

# ---- Special Rate Section ----
st.header("Special Rate Quote")
st.markdown("Calculate a custom total based on optional discount and tax exclusions.")

with st.form("special_form"):
    col1, col2 = st.columns(2)
    with col1:
        rate = st.number_input("Base Rate", min_value=0.0, step=0.01)
        nights = st.number_input("Number of Nights", min_value=1, step=1)
        discount_toggle = st.checkbox("Apply Discount")
        discount_percent = st.number_input("Discount %", min_value=0.0, max_value=100.0, step=0.1) if discount_toggle else 0.0

    with col2:
        tax_exclusion_toggle = st.checkbox("Exclude Specific Taxes")
        exclude_state = st.checkbox("Exclude State Tax") if tax_exclusion_toggle else False
        exclude_city = st.checkbox("Exclude City Tax") if tax_exclusion_toggle else False
        exclude_lodging = st.checkbox("Exclude Lodging Tax") if tax_exclusion_toggle else False

    submitted_special = st.form_submit_button("Calculate Total")

    if submitted_special:
        effective_rate = rate * (1 - discount_percent / 100)

        applied_tax = 0.0
        if not exclude_state:
            applied_tax += state_tax
        if not exclude_city:
            applied_tax += city_tax
        if not exclude_lodging:
            applied_tax += lodging_tax

        applied_multiplier = 1 + (applied_tax / 100)
        total = effective_rate * applied_multiplier * nights
        average_rate = total / nights

        st.success(f"Total Charge: ${total:.2f}")
        st.info(f"Average Nightly Rate (with tax): ${average_rate:.2f}")
