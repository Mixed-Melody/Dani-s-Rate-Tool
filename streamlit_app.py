import streamlit as st
import pyperclip

st.set_page_config(page_title="Rate Calculator", layout="centered")
st.title("🏨 Hotel Rate Calculator")

# --- Constants ---
DEFAULT_TAX = 12.5
STATE_TAX = 4.5
LODGING_TAX = 5.0
CITY_TAX = 3.0

# --- Shared Tax Settings ---
with st.sidebar:
    st.markdown("### ⚙️ Advanced Settings")
    show_advanced = st.checkbox("Override Tax Rate")
    if show_advanced:
        tax_rate = st.number_input("Custom Tax Rate (%)", min_value=0.0, format="%.2f", value=DEFAULT_TAX)
    else:
        tax_rate = DEFAULT_TAX
    st.caption(f"Current Tax Rate: **{tax_rate:.2f}%**")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Reverse: Total → Rate", "Forward: Rate → Total", "Special Rate"])

# --- Reverse Calculator ---
with tab1:
    st.subheader("Reverse Calculator – Total to Rate")
    total_amount = st.number_input("Total Amount ($)", min_value=0.0, format="%.2f")
    nights = st.number_input("Number of Nights", min_value=1, value=1)

    if st.button("Calculate Rate", key="reverse"):
        base_rate = total_amount / ((1 + (tax_rate / 100)) * nights)
        st.success(f"Base Nightly Rate: ${base_rate:.2f}")
        st.code(f"{base_rate:.2f}", language="text")
        st.button("Copy Rate", on_click=lambda: pyperclip.copy(f"{base_rate:.2f}"))

# --- Forward Calculator ---
with tab2:
    st.subheader("Forward Calculator – Rate to Total")
    base_rate_fwd = st.number_input("Nightly Rate ($)", min_value=0.0, format="%.2f")
    nights_fwd = st.number_input("Number of Nights", min_value=1, value=1, key="fwd_nights")

    if st.button("Calculate Total", key="forward"):
        total = base_rate_fwd * nights_fwd * (1 + (tax_rate / 100))
        st.success(f"Total Cost with Tax: ${total:.2f}")
        st.code(f"{total:.2f}", language="text")
        st.button("Copy Total", on_click=lambda: pyperclip.copy(f"{total:.2f}"))

# --- Special Rate Calculator ---
with tab3:
    st.subheader("Special Rate Calculator – Quote Builder")

    base_rate_special = st.number_input("Base Rate ($)", min_value=0.0, format="%.2f", key="special_rate")
    nights_special = st.number_input("Number of Nights", min_value=1, value=1, key="special_nights")

    mode = st.radio("Adjust Rate By:", ["Discount (%)", "Exclude Tax Type"])

    if mode == "Discount (%)":
        discount = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=10.0)
        adjusted_rate = base_rate_special * (1 - (discount / 100))
        effective_tax = tax_rate
    else:
        tax_to_exclude = st.selectbox("Exclude Tax Type", ["State Tax", "Lodging Tax", "City Tax"])
        if tax_to_exclude == "State Tax":
            effective_tax = tax_rate - STATE_TAX
        elif tax_to_exclude == "Lodging Tax":
            effective_tax = tax_rate - LODGING_TAX
        else:
            effective_tax = tax_rate - CITY_TAX
        adjusted_rate = base_rate_special

    total_cost = adjusted_rate * nights_special * (1 + (effective_tax / 100))
    avg_rate = total_cost / nights_special

    if st.button("Calculate Special Rate"):
        st.success(f"Total Cost: ${total_cost:.2f}")
        st.info(f"Average Nightly Rate: ${avg_rate:.2f} (Effective Tax: {effective_tax:.2f}%)")
        st.code(f"Total: ${total_cost:.2f} | Nightly: ${avg_rate:.2f}")
        st.button("Copy Result", on_click=lambda: pyperclip.copy(f"{avg_rate:.2f} avg / {total_cost:.2f} total"))
