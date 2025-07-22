import streamlit as st
from decimal import Decimal, getcontext, ROUND_CEILING

# ————— Decimal Setup —————
getcontext().prec = 9  # enough precision for our sums

def to_decimal(f):
    # Convert a float/str to Decimal exactly
    return Decimal(str(f))

def ceil2(value) -> Decimal:
    d = Decimal(str(value))
    return d.quantize(Decimal("0.01"), rounding=ROUND_CEILING)

def solve_base_rate(total, nights, tax_pct) -> Decimal:
    """
    Binary‑search for the base rate such that:
      ceil2(base_rate * (1 + tax_pct/100)) * nights == total
    """
    total_d  = Decimal(str(total))
    nights_d = Decimal(str(nights))
    tax_mult = Decimal(1) + (Decimal(str(tax_pct)) / 100)

    low, high = Decimal("0"), total_d
    for _ in range(25):  # 25 iterations for cent‑level precision
        mid = (low + high) / 2
        nightly = ceil2(mid * tax_mult)
        summed  = nightly * nights_d

        if summed == total_d:
            return mid
        if summed > total_d:
            high = mid
        else:
            low = mid
    return mid

# ————— App Config —————
st.set_page_config(page_title="Rate Calculator", layout="centered")
st.title("Hotel Rate Calculator")

# ————— Tax Rates (as Decimal) —————
STATE_TAX   = to_decimal(6.875)
CITY_TAX    = to_decimal(0.88)
LODGING_TAX = to_decimal(5.245)

# ————— Sidebar Tax Settings —————
with st.sidebar:
    st.markdown("### ⚙️ Advanced Tax Settings")
    adv = st.checkbox("Manually Adjust Tax Components")
    if adv:
        state_tax   = to_decimal(st.number_input("State Tax (%)",   value=6.875, step=0.001, format="%.3f"))
        city_tax    = to_decimal(st.number_input("City Tax (%)",    value=0.88,  step=0.001, format="%.3f"))
        lodging_tax = to_decimal(st.number_input("Lodging Tax (%)", value=5.245, step=0.001, format="%.3f"))
    else:
        state_tax, city_tax, lodging_tax = STATE_TAX, CITY_TAX, LODGING_TAX

    active_tax = state_tax + city_tax + lodging_tax
    st.caption(f"Current Tax Rate: **{active_tax:.3f}%**")

# ————— Tabs —————
tab1, tab2, tab3 = st.tabs([
    "Reverse: Total → Rate",
    "Forward: Rate → Total",
    "Special Rate"
])

# ─── Tab 1: Reverse ───
with tab1:
    total_amt_f = st.number_input("Total Amount ($)", 100.00, format="%.2f", key="rev_total")
    nights_i    = st.number_input("Number of Nights", 1, format="%d", key="rev_nights")

    total_amt = to_decimal(total_amt_f)
    # solve for base_rate so per‑night ceiling matches total
    base_rate = solve_base_rate(total=total_amt, nights=nights_i, tax_pct=active_tax)
    display_rate = f"{base_rate:.2f}"

    col1, col2 = st.columns(2)
    with col1: st.success("Base Nightly Rate:")
    with col2: st.code(display_rate, language="plaintext")


# ─── Tab 2: Forward ───
with tab2:
    rate_f   = st.number_input("Nightly Rate ($)", 100.00, format="%.2f", key="fwd_rate")
    nights_i = st.number_input("Number of Nights",   1,    format="%d", key="fwd_nights2")

    rate   = to_decimal(rate_f)
    nights = Decimal(str(nights_i))

    nightly_with_tax = ceil2(rate * (Decimal(1) + active_tax / 100))
    total            = nightly_with_tax * nights
    display_total    = f"{total:.2f}"

    col1, col2 = st.columns(2)
    with col1: st.success("Total Cost:")
    with col2: st.code(display_total, language="plaintext")


# ─── Tab 3: Special Rate ───
with tab3:
    rate_f       = st.number_input("Nightly Rate ($)", 100.00, format="%.2f", key="spec_rate")
    discount_pct = st.slider("Discount (%)", 0, 100, 0)
    nights_i     = st.number_input("Number of Nights", 1, format="%d", key="spec_nights")

    exclude_state   = st.checkbox("Exclude State Tax")
    exclude_city    = st.checkbox("Exclude City Tax")
    exclude_lodging = st.checkbox("Exclude Lodging Tax")

    rate      = to_decimal(rate_f)
    nights    = Decimal(str(nights_i))
    discount  = Decimal(str(discount_pct)) / Decimal(100)
    discounted = rate * (Decimal(1) - discount)

    taxes = [
        state_tax   if not exclude_state   else Decimal(0),
        city_tax    if not exclude_city    else Decimal(0),
        lodging_tax if not exclude_lodging else Decimal(0),
    ]
    eff_tax = sum(taxes)

    nightly_with_tax = ceil2(discounted * (Decimal(1) + eff_tax / 100))
    total_cost       = nightly_with_tax * nights
    avg_rate         = nightly_with_tax

    col1, col2 = st.columns(2)
    with col1:
        st.success("Total Cost:")
        if nights_i > 1:
            st.info(f"Average Nightly Rate: ${avg_rate:.2f}")
    with col2:
        st.code(f"{total_cost:.2f}", language="plaintext")
        if nights_i > 1:
            st.code(f"{avg_rate:.2f}", language="plaintext")
