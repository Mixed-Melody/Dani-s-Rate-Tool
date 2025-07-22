import streamlit as st

st.set_page_config(page_title="Rate Calculator", layout="centered")
st.title("Hotel Rate Calculator")

# --- Tax Rates ---
STATE_TAX = 6.875
CITY_TAX = 0.88
LODGING_TAX = 5.245

# --- Tax Component Toggle ---
with st.sidebar:
    st.markdown("### ⚙️ Advanced Tax Settings")
    show_advanced = st.checkbox("Manually Adjust Tax Components")

    if show_advanced:
        state_tax = st.number_input("State Tax (%)", min_value=0.0, max_value=100.0, value=6.875, step=0.0001, format="%.4f")
        city_tax = st.number_input("City Tax (%)", min_value=0.0, max_value=100.0, value=0.88, step=0.0001, format="%.4f")
        lodging_tax = st.number_input("Lodging Tax (%)", min_value=0.0, max_value=100.0, value=5.245, step=0.0001, format="%.4f")
    else:
        # Default values if advanced is off
        state_tax = STATE_TAX
        city_tax = CITY_TAX
        lodging_tax = LODGING_TAX

    active_tax = state_tax + city_tax + lodging_tax
    st.caption(f"Current Tax Rate: **{active_tax:.4f}%**")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Reverse: Total → Rate", "Forward: Rate → Total", "Special Rate"])

# --- Reverse Calculator ---
with tab1:
    st.subheader("Reverse Calculator – Total to Rate")
    st.markdown(
        "**Used when the total amount is slightly off from the sum of nightly rates.**\n\n"
        "Sometimes platforms like Booking VCC are off by up to one dollar, even though the nightly rates "
        "are correct. This tool helps you reverse-engineer and adjust the rate to match the given total."
    )
    total_amount = st.number_input("Total Amount ($)", min_value=0.0, format="%.2f", key="rev_total")
    nights = st.number_input("Number of Nights", min_value=1, value=1, key="rev_nights")

    # auto‑calculate
    nightly_total = round(total_amount / nights, 2)
    base_rate = nightly_total / (1 + active_tax / 100)
    display_rate = f"{base_rate:.2f}"

    # two columns: label on left, copyable code on right
    col1, col2 = st.columns([1, 1])
    with col1:
        st.success(f"Base Nightly Rate:")
    with col2:
        st.code(display_rate, language="plaintext")


# --- Forward Calculator ---
with tab2:
    st.subheader("Forward Calculator – Rate to Total")
    st.markdown(
        "**Basic nightly rate calculator.**\n\n"
        "Use this if you just want to calculate the total amount from a rate "
        "and number of nights. Simple and quick."
    )
    base_rate_fwd = st.number_input(
        "Nightly Rate ($)", min_value=0.0, format="%.2f", key="fwd_rate"
    )
    nights_fwd = st.number_input(
        "Number of Nights", min_value=1, value=1, key="fwd_nights2"
    )

    # calculate nightly cost with tax, rounded per night
    nightly_with_tax = round(base_rate_fwd * (1 + active_tax / 100), 2)

    # total is per-night rounded cost × nights
    total = nightly_with_tax * nights_fwd
    display_total = f"{total:.2f}"

    col1, col2 = st.columns([1, 1])
    with col1:
        st.success(f"Total Cost:")
    with col2:
        st.code(display_total, language="plaintext")

# --- Special Rate Calculator ---
with tab3:
    st.subheader("Special Rate Calculator")
    st.markdown("**For handling special cases like VCCs with tax exemptions or discounts.**\n\nThis is especially useful for Expedia VCCs that are exempt from certain taxes like state tax. You can toggle exclusions and apply a discount if needed.")
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
    included = [
        state_tax if not exclude_state else 0,
        city_tax if not exclude_city else 0,
        lodging_tax if not exclude_lodging else 0,
    ]
    effective_tax = sum(included)

    nightly_with_tax = round(discounted_rate * (1 + effective_tax/100), 2)
    total_cost       = nightly_with_tax * nights
    average_rate     = nightly_with_tax

    # Show results with copy buttons
    col1, col2 = st.columns([1, 1])  # you can tweak ratios, e.g., [1, 2] for even tighter
    with col1:
        st.success(f"Total Cost:")
        if nights >1:
            st.info(f"Average Nightly Rate (with tax): ${average_rate:.2f}")
    with col2:
        st.code(f"{total_cost:.2f}", language="plaintext")
        if nights >1:
            st.code(f"{average_rate:.2f}", language="plaintext")
