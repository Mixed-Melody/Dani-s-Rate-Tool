import streamlit as st

# --- Constants ---
TAX_STATE = 0.06875
TAX_CITY = 0.01125
TAX_LODGING = 0.05
TAX_TOTAL = TAX_STATE + TAX_CITY + TAX_LODGING

# --- App Layout ---
st.title("Rate Breakdown Tool")
st.write("Use this tool to reverse-calculate hotel room rates or break down taxes.")

method = st.radio("Calculation Method", ("Forward Calculate (Base to Total)", "Reverse Calculate (Total to Base)"))

if method == "Reverse Calculate (Total to Base)":
    total = st.number_input("Enter Grand Total ($)", min_value=0.00, step=0.01)
else:
    total = st.number_input("Enter Base Rate ($)", min_value=0.00, step=0.01)

# --- Rate Calculation ---
if method == "Reverse Calculate (Total to Base)":
    base_rate = total / (1 + TAX_TOTAL)
else:
    base_rate = total

state_tax = base_rate * TAX_STATE
city_tax = base_rate * TAX_CITY
lodging_tax = base_rate * TAX_LODGING
grand_total = base_rate + state_tax + city_tax + lodging_tax

# --- Display Results ---
st.write("### Breakdown:")
st.write(f"Base Rate: ${base_rate:.2f}")
st.write(f"State Tax (6.875%): ${state_tax:.2f}")
st.write(f"City Tax (1.125%): ${city_tax:.2f}")
st.write(f"Lodging Tax (5.0%): ${lodging_tax:.2f}")
st.markdown("---")
st.write(f"**Grand Total: ${grand_total:.2f}**")
