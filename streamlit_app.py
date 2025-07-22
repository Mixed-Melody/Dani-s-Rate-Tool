import streamlit as st

st.set_page_config(page_title="Rate Calculator", layout="centered")
st.title("🏨 Hotel Rate Calculator")

# --- Tax Rates ---
STATE_TAX = 4.5
CITY_TAX = 3.0
LODGING_TAX = 5.0

# --- Tax Component Toggle ---
with st.sidebar:
    st.markdown("### ⚙️ Advanced Tax Settings")
    show_advanced = st.checkbox("Manually Adjust Tax Components")

    if show_advanced:
        state_tax = st.number_input("State Tax (%)", min_value=0.0, max_value=100.0, value=6.875, step=0.1)
        city_tax = st.number_input("City Tax (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1)
        lodging_tax = st.number_input("Lodging Tax (%)", min_value=0.0, max_value=100.0, value=2.7564, step=0.1)
    else:
        # Default values if advanced is off
        state_tax = 6.875
        city_tax = 3.0
        lodging_tax = 2.7564

    active_tax = state_tax + city_tax + lodging_tax
    st.caption(f"Current Tax Rate: **{active_tax:.2f}%**")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Reverse: Total → Rate", "Forward: Rate → Total", "Special Rate"])

# --- Reverse Calculator ---
with tab1:
    st.subheader("Reverse Calculator – Total to Rate")
    st.markdown("**Used when the total amount is slightly off from the sum of nightly rates.**\n\nSometimes platforms like Booking VCC are off by $0.01 to $1, even though the nightly rates are correct. This tool helps you reverse-engineer and adjust the rate to match the given total.")
    total_amount = st.number_input("Total Amount ($)", min_value=0.0, format="%.2f")
    nights = st.number_input("Number of Nights", min_value=1, value=1)

    if st.button("Calculate Rate", key="reverse"):
        base_rate = total_amount / ((1 + (active_tax / 100)) * nights)
        result = f"{base_rate:.2f}"
        st.success(f"Base Nightly Rate: ${result}")
        st.text_input("Copy result:", value=result, label_visibility="collapsed")

# --- Forward Calculator ---
with tab2:
    st.subheader("Forward Calculator – Rate to Total")
    base_rate_fwd = st.number_input("Nightly Rate ($)", min_value=0.0, format="%.2f")
    nights_fwd = st.number_input("Number of Nights", min_value=1, value=1, key="fwd_nights")

    if st.button("Calculate Total", key="forward"):
        total = base_rate_fwd * nights_fwd * (1 + (active_tax / 100))
        result = f"{total:.2f}"
        st.success(f"Total Cost with Tax: ${result}")
        st.text_input("Copy result:", value=result, label_visibility="collapsed")

# --- Special Rate Calculator ---
with tab3:
    st.header("Special Rate Calculator")

    nightly_rate = st.number_input("Nightly Rate", min_value=0.0, value=100.0, key="special_nightly_rate")
    nights = st.number_input("Number of Nights", min_value=1, value=1, key="special_nights")

    discount_percent = st.slider("Discount (%)", 0, 100, 0)

    st.markdown("#### Tax Exemptions (optional)")
    exclude_state = st.checkbox("Exclude State Tax")
    exclude_city = st.checkbox("Exclude City Tax")
    exclude_lodging = st.checkbox("Exclude Lodging Tax")

    # Apply discount
    discounted_rate = nightly_rate * (1 - discount_percent / 100)

    # Build tax total based on what's *not* excluded
    final_tax = 0
    if not exclude_state:
        final_tax += state_tax
    if not exclude_city:
        final_tax += city_tax
    if not exclude_lodging:
        final_tax += lodging_tax

    subtotal = discounted_rate * nights
    total_tax_amount = subtotal * (final_tax / 100)
    total_cost = subtotal + total_tax_amount
    average_rate = total_cost / nights

    st.markdown(f"**Total Cost:** ${total_cost:.2f}")
    st.markdown(f"**Average Rate (with tax):** ${average_rate:.2f}")

