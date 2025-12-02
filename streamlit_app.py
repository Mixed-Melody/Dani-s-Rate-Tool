import streamlit as st

from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_UP

# Set precision high enough for cents-level math
getcontext().prec = 10

# Tax rates
state_rate = Decimal('0.06875')
city_rate = Decimal('0.01125')
lodging_rate = Decimal('0.05')

def compute_breakdown(base):
    """Given a base rate, return (total, state_tax, city_tax, lodging_tax)."""
    base_dec = Decimal(str(base)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    # State tax is always rounded *up* to the next cent
    state_tax = (base_dec * state_rate * 100).to_integral_value(rounding=ROUND_UP) / Decimal('100')
    # City and lodging taxes are rounded normally
    city_tax = (base_dec * city_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    lodging_tax = (base_dec * lodging_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = base_dec + state_tax + city_tax + lodging_tax
    return float(total), float(state_tax), float(city_tax), float(lodging_tax)

def find_base_from_total(target_total):
    """Find a base rate that exactly matches a given total with taxes."""
    target_total_dec = Decimal(str(target_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    # Naïve starting point (ignores rounding)
    approx_base = target_total_dec / (1 + state_rate + city_rate + lodging_rate)
    # Search ±$3 around the naive estimate
    for offset in range(-300, 301):
        candidate = (approx_base + Decimal(offset) * Decimal('0.01')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if candidate <= 0:
            continue
        total, st, ct, lt = compute_breakdown(float(candidate))
        # Match the total to within half a cent
        if abs(total - float(target_total)) < 0.005:
            return float(candidate), st, ct, lt
    return None  # No match found

# Example usage
totals_to_try = [200.76, 143.52, 179.23, 90.78, 91.51, 186.33]
for t in totals_to_try:
    base, st, ct, lt = find_base_from_total(t)
    print(f"Target total ${t}: base {base}, taxes: state {st}, city {ct}, lodging {lt}")
