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
        use_state = st.checkbox("Include State Tax", value=True)
        use_city = st.checkbox("Include City Tax", value=True)
        use_lodging = st.checkbox("Include Lodging Tax", value=True)
    else:
        use_state = use_city = use_lodging = True

    active_tax = (
            (STATE_TAX if use_state else 0.0) +
            (CITY_TAX if use_city else 0.0) +
            (LODGING_TAX if use_lodging else 0.0)
    )
    st.caption(f"Current Tax Rate: **{active_tax:.2f}%**")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Reverse: Total → Rate", "Forward: Rate → Total", "Special Rate"])

# --- Reverse Calculator ---
with tab1:
    st.subheader("Reverse Calculator – Total to Rate")
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
    st.subheader("Special Rate Calculator – Quote Builder")

    base_rate_special = st.number_input("Base Rate ($)", min_value=0.0, format="%.2f", key="special_rate")
    nights_special = st.number_input("Number of Nights", min_value=1, value=1, key="special_nights")

    mode = st.radio("Adjust Rate By:", ["Discount (%)", "Exclude Tax Type"])

    # Tax Exclusion
    effective_tax = active_tax
    if mode == "Discount (%)":
        discount = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=10.0)
        adjusted_rate = base_rate_special * (1 - (discount / 100))
    else:
        exclude = st.selectbox("Exclude Tax Type", ["State Tax", "City Tax", "Lodging Tax"])
        adjusted_rate = base_rate_special
        if exclude == "State Tax":
            effective_tax -= STATE_TAX
        elif exclude == "City Tax":
            effective_tax -= CITY_TAX
        else:
            effective_tax -= LODGING_TAX

    total_cost = adjusted_rate * nights_special * (1 + (effective_tax / 100))
    avg_rate = total_cost / nights_special

    if st.button("Calculate Special Rate"):
        result = f"Total: ${total_cost:.2f} | Nightly: ${avg_rate:.2f} (Tax: {effective_tax:.2f}%)"
        st.success(f"Total Cost: ${total_cost:.2f}")
        st.info(f"Average Nightly Rate: ${avg_rate:.2f} (Effective Tax: {effective_tax:.2f}%)")
        st.text_input("Copy result:", value=result, label_visibility="collapsed")
