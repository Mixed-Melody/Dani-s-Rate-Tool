import streamlit as st

st.set_page_config(page_title="Lodging Calculator", layout="centered")

st.title("🏨 Lodging Total Calculator")

# Sidebar: Tax Rate Configuration
with st.sidebar:
    st.markdown("### ⚙️ Tax Configuration")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**State Tax**")
    with col2:
        state_tax = st.number_input("", min_value=0.0, value=4.5, format="%.2f", key="state_tax")

    col3, col4 = st.columns([1, 2])
    with col3:
        st.markdown("**City Tax**")
    with col4:
        city_tax = st.number_input("", min_value=0.0, value=3.0, format="%.2f", key="city_tax")

    col5, col6 = st.columns([1, 2])
    with col5:
        st.markdown("**Lodging Tax**")
    with col6:
        lodging_tax = st.number_input("", min_value=0.0, value=5.0, format="%.2f", key="lodging_tax")

    active_tax = state_tax + city_tax + lodging_tax
    st.caption(f"Total Applied Tax Rate: **{active_tax:.2f}%**")

# Main Inputs
st.markdown("### 📝 Rate Entry")

room_rate = st.number_input("Nightly Rate ($)", min_value=0.0, value=100.0, step=1.0)
num_nights = st.number_input("Number of Nights", min_value=1, value=1)

subtotal = room_rate * num_nights
st.markdown(f"**Subtotal (before tax):** ${subtotal:.2f}")

# Special Rate Options
with st.expander("💡 Special Rate Options"):
    col1, col2 = st.columns(2)

    with col1:
        apply_discount = st.checkbox("Apply Discount")
    with col2:
        exclude_tax = st.checkbox("Exclude Specific Tax")

    discount = 0
    exclude = ""

    if apply_discount:
        discount = st.number_input("Discount Percentage (%)", min_value=0.0, max_value=100.0, value=0.0, format="%.2f")

    if exclude_tax:
        exclude = st.selectbox("Which Tax to Exclude?", ["State Tax", "City Tax", "Lodging Tax"])

# Tax logic
effective_tax = active_tax
if exclude_tax:
    if exclude == "State Tax":
        effective_tax -= state_tax
    elif exclude == "City Tax":
        effective_tax -= city_tax
    elif exclude == "Lodging Tax":
        effective_tax -= lodging_tax

# Final total
adjusted_subtotal = subtotal * (1 - discount / 100)
total_with_tax = adjusted_subtotal * (1 + effective_tax / 100)

st.markdown(f"### 💰 Final Total: **${total_with_tax:.2f}**")

# Optional: Breakdown
with st.expander("📊 Detailed Breakdown"):
    st.write(f"Room Rate: ${room_rate:.2f}")
    st.write(f"Nights: {num_nights}")
    st.write(f"Subtotal: ${subtotal:.2f}")
    st.write(f"Discount: {discount:.2f}% → ${subtotal - adjusted_subtotal:.2f} off")
    st.write(f"Effective Tax Rate: {effective_tax:.2f}%")
    st.write(f"Final Total: ${total_with_tax:.2f}")
