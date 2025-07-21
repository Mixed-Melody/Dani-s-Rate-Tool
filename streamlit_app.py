import streamlit as st

st.set_page_config(page_title="Hotel Rate Calculator", layout="centered")

st.title("🏨 Hotel Rate Calculator")

# --- Tax Configuration ---
st.subheader("Tax Settings")
with st.expander("Advanced Tax Settings"):
    state_tax = st.number_input("State Tax %", value=4.0, step=0.1)
    city_tax = st.number_input("City Tax %", value=5.0, step=0.1)
    lodging_tax = st.number_input("Lodging Tax %", value=3.5, step=0.1)

total_tax = state_tax + city_tax + lodging_tax
tax_rate = total_tax / 100

# --- Reverse Calculator (Total to Rate) ---
st.header("🔁 Reverse Rate Calculator (From Total to Nightly Rate)")
with st.form("reverse_rate_form"):
    total_amount = st.number_input("Enter total amount ($)", min_value=0.0, step=0.01)
    num_nights = st.number_input("Number of nights", min_value=1, step=1, value=1)
    submitted = st.form_submit_button("Calculate Rate")

    if submitted and num_nights > 0:
        rate_before_tax = total_amount / (1 + tax_rate) / num_nights
        st.success(f"Base Rate Per Night: ${rate_before_tax:.2f}")
        st.download_button("Copy Rate", str(round(rate_before_tax, 2)), file_name="rate.txt")

# --- Normal Calculator (Rate to Total) ---
st.header("💰 Standard Rate Calculator (From Rate to Total)")
with st.form("standard_rate_form"):
    base_rate = st.number_input("Nightly rate ($)", min_value=0.0, step=0.01)
    nights = st.number_input("Number of nights", min_value=1, step=1, value=1)
    submitted_normal = st.form_submit_button("Calculate Total")

    if submitted_normal:
        total = base_rate * (1 + tax_rate) * nights
        st.success(f"Total Price (with tax): ${total:.2f}")
        st.download_button("Copy Total", str(round(total, 2)), file_name="total.txt")

# --- Special Rate (Quoting) ---
st.header("✨ Special Rate Quote")
with st.form("special_rate_form"):
    special_rate = st.number_input("Nightly base rate ($)", min_value=0.0, step=0.01)
    special_nights = st.number_input("Number of nights", min_value=1, step=1, value=1)

    apply_discount = st.checkbox("Apply discount?")
    discount_percentage = 0
    if apply_discount:
        discount_percentage = st.slider("Discount %", 0, 100, 10)

    exclude_tax_options = []
    st.markdown("**Exclude tax components?**")
    col1, col2, col3 = st.columns(3)
    with col1:
        exclude_state = st.checkbox("State Tax")
    with col2:
        exclude_city = st.checkbox("City Tax")
    with col3:
        exclude_lodging = st.checkbox("Lodging Tax")

    submitted_special = st.form_submit_button("Calculate Special Rate")

    if submitted_special:
        # Calculate total tax based on exclusions
        effective_tax = 0
        if not exclude_state:
            effective_tax += state_tax
        if not exclude_city:
            effective_tax += city_tax
        if not exclude_lodging:
            effective_tax += lodging_tax

        effective_tax_rate = effective_tax / 100
        discounted_rate = special_rate * (1 - discount_percentage / 100)
        total_price = discounted_rate * (1 + effective_tax_rate) * special_nights
        average_price = total_price / special_nights

        st.success(f"Total Price: ${total_price:.2f}")
        st.info(f"Average Price per Night: ${average_price:.2f}")
        st.download_button("Copy Quote Total", str(round(total_price, 2)), file_name="quote_total.txt")
