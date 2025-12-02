"""Streamlit Hotel Rate Breakdown Calculator

This Streamlit app computes the tax breakdown for hotel room rates
using the same rounding logic applied by your hotel system.  You
provide a **grand total** (the amount charged including taxes) and
optionally specify the **number of nights**.  The calculator then
estimates the base rate per night and the individual state, city and
lodging taxes.  It also multiplies those per‑night values by the
number of nights to show totals for the entire stay.

Please note that the hotel system sometimes allocates a penny
difference between the base rate and the taxes.  This calculator
assumes the same rounding rules but may yield results that are up to
one cent lower than what the system computes.  A penny short is
always safer than a penny over when dealing with virtual credit
cards.
"""

import streamlit as st
from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_UP


# Increase precision for Decimal computations
getcontext().prec = 10

# Define tax rates as Decimals for precise arithmetic
STATE_TAX_RATE = Decimal("0.06875")
CITY_TAX_RATE = Decimal("0.01125")
LODGING_TAX_RATE = Decimal("0.05")


def compute_breakdown(base: float) -> tuple[float, float, float, float, float]:
    """Compute taxes and total for a given base rate.

    Parameters
    ----------
    base : float
        The pre‑tax base rate.

    Returns
    -------
    tuple
        (base, state_tax, city_tax, lodging_tax, total) all as floats
        rounded to two decimals.
    """
    # Convert base to Decimal at two‑decimal precision
    base_dec = Decimal(str(base)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # State tax is always rounded up to the nearest cent
    state_tax = (base_dec * STATE_TAX_RATE * 100).to_integral_value(rounding=ROUND_UP) / Decimal("100")
    # City tax uses standard half‑up rounding
    city_tax = (base_dec * CITY_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # Lodging tax uses standard half‑up rounding
    lodging_tax = (base_dec * LODGING_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # Sum up
    total = base_dec + state_tax + city_tax + lodging_tax
    return (float(base_dec), float(state_tax), float(city_tax), float(lodging_tax), float(total))


def find_base_from_total(target_total: float) -> tuple[float, float, float, float, float] | None:
    """Solve for the base rate given a grand total using hotel rounding rules.

    The hotel system sometimes allocates a penny difference between the
    base rate and the state tax so that the grand total stays exact.
    This implementation first estimates the base by dividing the total
    by the combined rate (1 + state + city + lodging) and rounding to
    two decimals.  It then walks downward in one‑cent increments to
    find a candidate base that preserves the total but minimises the
    base (and correspondingly increases the state tax) when a penny
    discrepancy exists.

    Parameters
    ----------
    target_total : float
        The grand total including taxes.

    Returns
    -------
    tuple or None
        (base, state_tax, city_tax, lodging_tax, total) as floats if a
        solution is found; otherwise None.
    """
    total_dec = Decimal(str(target_total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # Compute the naive base by removing all tax rates
    naive_base = total_dec / (1 + STATE_TAX_RATE + CITY_TAX_RATE + LODGING_TAX_RATE)
    naive_base = naive_base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # Search downward from the naive base for a better fit
    candidates: list[tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]] = []
    for cents_offset in range(0, 21):  # search up to 20 cents below the naive base
        candidate_base = naive_base - Decimal(cents_offset) * Decimal("0.01")
        if candidate_base <= 0:
            continue
        # Predicted taxes using normal rounding
        city_tax = (candidate_base * CITY_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        lodging_tax = (candidate_base * LODGING_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        predicted_state = (candidate_base * STATE_TAX_RATE * 100).to_integral_value(rounding=ROUND_UP) / Decimal("100")
        # Compute the residual state tax needed to hit the total
        residual_state = total_dec - candidate_base - city_tax - lodging_tax
        residual_state = residual_state.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # Skip negative residuals
        if residual_state < 0:
            continue
        diff = residual_state - predicted_state
        # Accept if residual state is within a cent of predicted and prefer
        # moving a penny from base to state (diff >= 0)
        if abs(diff) <= Decimal("0.01"):
            candidates.append((candidate_base, residual_state, city_tax, lodging_tax, total_dec, diff))
    if candidates:
        # Prefer positive diff (penny moved to state), else highest diff allowed
        candidates.sort(key=lambda x: (-(x[5] > 0), x[0]))
        chosen_base, state_tax, city_tax, lodging_tax, total_final, _ = candidates[0]
        return float(chosen_base), float(state_tax), float(city_tax), float(lodging_tax), float(total_final)
    # Fallback exhaustive search
    approx_base = total_dec / (1 + STATE_TAX_RATE + CITY_TAX_RATE + LODGING_TAX_RATE)
    for offset_cents in range(-300, 301):
        candidate = (approx_base + Decimal(offset_cents) * Decimal("0.01")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if candidate <= 0:
            continue
        b, st, ct, lt, total_f = compute_breakdown(float(candidate))
        if abs(total_f - float(total_dec)) < 0.005:
            return b, st, ct, lt, total_f
    return None


def main() -> None:
    """Run the Streamlit app."""
    st.set_page_config(page_title="Hotel Rate Breakdown", page_icon="🏨")
    st.title("Hotel Rate Breakdown Calculator")
    st.markdown(
        """
        Provide the **grand total** for your stay (including taxes) and the
        **number of nights**.  This calculator will estimate the base rate
        per night and the corresponding state, city and lodging taxes
        using the hotel's rounding rules.  The results may be up to
        one penny short of the system's calculation due to rounding
        differences.
        """
    )

    total_input = st.number_input(
        "Enter Grand Total for Entire Stay ($)",
        min_value=0.00,
        step=0.01,
        format="%.2f",
    )
    nights = st.number_input(
        "Number of nights",
        min_value=1,
        value=1,
        step=1,
        format="%d",
    )
    if st.button("Compute Breakdown"):
        if nights <= 0:
            st.error("Number of nights must be at least 1.")
            return
        if total_input < 0:
            st.error("Grand total must be non‑negative.")
            return
        # Compute per‑night total
        per_night_total = total_input / nights
        result = find_base_from_total(per_night_total)
        if result is None:
            st.error("No matching base rate found for the given total.")
        else:
            base_night, state_tax_night, city_tax_night, lodging_tax_night, total_night = result
            # Multiply per‑night values by nights
            base_total = base_night * nights
            state_tax_total = state_tax_night * nights
            city_tax_total = city_tax_night * nights
            lodging_tax_total = lodging_tax_night * nights
            grand_total = base_total + state_tax_total + city_tax_total + lodging_tax_total
            # Display per‑night breakdown
            st.subheader("Per‑Night Breakdown")
            st.metric("Base Rate per Night", f"$ {base_night:.2f}")
            st.metric("State Tax per Night (6.875% – rounded up)", f"$ {state_tax_night:.2f}")
            st.metric("City Tax per Night (1.125%)", f"$ {city_tax_night:.2f}")
            st.metric("Lodging Tax per Night (5.0%)", f"$ {lodging_tax_night:.2f}")
            st.markdown("---")
            # Display totals for stay when nights > 1
            if nights > 1:
                st.subheader("Total for Stay")
                st.metric("Base Total", f"$ {base_total:.2f}")
                st.metric("State Tax Total", f"$ {state_tax_total:.2f}")
                st.metric("City Tax Total", f"$ {city_tax_total:.2f}")
                st.metric("Lodging Tax Total", f"$ {lodging_tax_total:.2f}")
                st.markdown("---")
                st.metric("Grand Total", f"$ {grand_total:.2f}")
            else:
                # For a single night, show the grand total at the end
                st.markdown("---")
                st.metric("Grand Total", f"$ {grand_total:.2f}")


if __name__ == "__main__":
    main()
