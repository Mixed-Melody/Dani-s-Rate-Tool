import streamlit as st

st.set_page_config(page_title="Rate Calculator", layout="centered")

st.title("🏨 Hotel Rate Calculator")

# Tabs for the three modes
tab1, tab2, tab3 = st.tabs(["Reverse: Total → Rate", "Forward: Rate → Total", "Special Rate"])

# --- Reverse Calculator ---
with tab1:
    st.subheader("Reverse Calculator – Total to Rate")
    total_amount = st.number_input("Total Amount ($)", min_value=0.0, format="%.2f")
    nights = st.number_input("Number of Nights", min_value=1, value=1)
    tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, value=10.0, format="%.2f")

    if st.button("Calculate Rate", key="reverse"):
        base_rate = total_amount / ((1 + (tax_rate / 100)) * nights)
        st.success(f"Base Nightly Rate: ${base_rate:.2f}")

# --- Forward Calculator ---
with tab2:
    st.subheader("Forward Calculator – Rate to Total")
    base_rate_fwd = st.number_input("Nightly Rate ($)", min_value=0.0, format="%.2f")
    nights_fwd = st.number_input("Number of Nights", min_value=1, value=1, key="fwd_nights")
    tax_rate_fwd = st.number_input("Tax Rate (%)", min_value=0.0, value=10.0, format="%.2f", key="fwd_tax")

    if st.button("Calculate Total", key="forward"):
        total = base_rate_fwd * nights_fwd * (1 + (tax_rate_fwd / 100))
        st.success(f"Total Cost with Tax: ${total:.2f}")

# --- Special Rate Calculator ---
with tab3:
    st.subheader("Special Rate Calculator")
    mode = st.radio("Tax Adjustment Mode", ["Exclude Portion", "Reduce Tax Rate %"])

    total_special = st.number_input("Total Amount ($)", min_value=0.0, format="%.2f", key="special_total")
    nights_special = st.number_input("Number of Nights", min_value=1, value=1, key="special_nights")

    if mode == "Exclude Portion":
        exclusion = st.number_input("Excluded Tax Portion (%)", min_value=0.0, max_value=100.0, value=5.0)
        effective_tax = 10.0 - exclusion
    else:
        reduction = st.number_input("Apply Only (%) of Tax", min_value=0.0, max_value=100.0, value=70.0)
        effective_tax = 10.0 * (reduction / 100)

    if st.button("Calculate Special Rate"):
        base_special = total_special / ((1 + (effective_tax / 100)) * nights_special)
        st.success(f"Adjusted Nightly Rate: ${base_special:.2f} (Effective Tax: {effective_tax:.2f}%)")
