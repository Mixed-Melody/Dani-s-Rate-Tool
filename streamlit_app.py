"""Streamlit Hotel Rate Breakdown Calculator

This Streamlit app helps you compute the tax breakdown for hotel room
rates. It supports two modes:

1. Forward Calculation – where you enter a base rate (pre‑tax), and
   the app computes the state, city and lodging taxes along with the
   grand total.
2. Reverse Calculation – where you enter a grand total (tax included)
   and the app solves for the base rate that yields that total using
   the same rounding logic applied by the hotel system. It then
   displays the individual taxes and base rate.

The state tax rate is 6.875 % and is always rounded **up** to the next
cent. The city and lodging tax rates are 1.125 % and 5.0 % respectively
and both use normal half‑up rounding to two decimals.

The app also plots a simple bar chart to visualise the breakdown of
base rate and taxes.
"""

import streamlit as st
from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_UP
import matplotlib.pyplot as plt


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
    # This ignores rounding but serves as a starting point
    naive_base = total_dec / (1 + STATE_TAX_RATE + CITY_TAX_RATE + LODGING_TAX_RATE)
    naive_base = naive_base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # We will search downward from the naive base for a better fit
    candidates: list[tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]] = []
    for cents_offset in range(0, 21):  # search up to 20 cents below the naive base
        candidate_base = naive_base - Decimal(cents_offset) * Decimal("0.01")
        if candidate_base <= 0:
            continue
        # Predicted city and lodging taxes using normal rounding
        city_tax = (candidate_base * CITY_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        lodging_tax = (candidate_base * LODGING_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # Predicted state tax using standard rounding up
        predicted_state = (candidate_base * STATE_TAX_RATE * 100).to_integral_value(rounding=ROUND_UP) / Decimal("100")
        # Compute the residual state tax needed to hit the total
        residual_state = total_dec - candidate_base - city_tax - lodging_tax
        residual_state = residual_state.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # If the residual state is negative, break (base too high)
        if residual_state < 0:
            continue
        # The difference between residual and predicted state indicates
        # whether we have moved a penny from the base to the state.
        diff = residual_state - predicted_state
        # Accept the candidate if the residual state does not deviate by
        # more than 1 cent from the predicted state tax.  Prefer
        # candidates where diff >= 0 (state tax is equal or higher than
        # predicted), which results in a slightly lower base.
        if abs(diff) <= Decimal("0.01"):
            candidates.append((candidate_base, residual_state, city_tax, lodging_tax, total_dec, diff))
    # Select the best candidate according to diff and base
    if candidates:
        # Sort by diff descending (prefer positive diff), then by base ascending (prefer smaller base)
        candidates.sort(key=lambda x: (-(x[5] > 0), x[0]))
        chosen_base, state_tax, city_tax, lodging_tax, total_final, _ = candidates[0]
        return float(chosen_base), float(state_tax), float(city_tax), float(lodging_tax), float(total_final)
    # Fall back to the original exhaustive search if no candidate found
    # Rough starting point ignoring rounding
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
        Enter either a **base rate** (pre‑tax) or a **grand total** (with
        taxes) and this tool will compute the state, city and lodging
        taxes for you. When given a grand total, the app searches for
        the base rate that results in exactly that total using the same
        rounding rules applied by your hotel system.
        """
    )

    # Select calculation method
    method = st.radio(
        "Calculation Method",
        options=["Forward (Base → Total)", "Reverse (Total → Base)"],
        help="Choose whether you want to start with a base rate or a grand total."
    )

    # Take user input based on method
    if method == "Forward (Base → Total)":
        base_input = st.number_input(
            "Enter Base Rate ($)",
            min_value=0.00,
            step=0.01,
            format="%.2f"
        )
        if st.button("Compute Total"):
            base, state_tax, city_tax, lodging_tax, total = compute_breakdown(base_input)
            # Display results
            st.subheader("Breakdown")
            st.metric("Base Rate", f"$ {base:.2f}")
            st.metric("State Tax (6.875% – rounded up)", f"$ {state_tax:.2f}")
            st.metric("City Tax (1.125%)", f"$ {city_tax:.2f}")
            st.metric("Lodging Tax (5.0%)", f"$ {lodging_tax:.2f}")
            st.markdown("---")
            st.metric("Grand Total", f"$ {total:.2f}")

            # Plot bar chart
            components = ["Base", "State Tax", "City Tax", "Lodging Tax"]
            values = [base, state_tax, city_tax, lodging_tax]
            fig, ax = plt.subplots()
            ax.bar(components, values)
            ax.set_title("Rate Components")
            ax.set_ylabel("Amount ($)")
            st.pyplot(fig)
    else:
        total_input = st.number_input(
            "Enter Grand Total ($)",
            min_value=0.00,
            step=0.01,
            format="%.2f"
        )
        if st.button("Compute Base"):
            result = find_base_from_total(total_input)
            if result is None:
                st.error("No matching base rate found for the given total.")
            else:
                base, state_tax, city_tax, lodging_tax, total = result
                # Display results
                st.subheader("Breakdown")
                st.metric("Base Rate", f"$ {base:.2f}")
                st.metric("State Tax (6.875% – rounded up)", f"$ {state_tax:.2f}")
                st.metric("City Tax (1.125%)", f"$ {city_tax:.2f}")
                st.metric("Lodging Tax (5.0%)", f"$ {lodging_tax:.2f}")
                st.markdown("---")
                st.metric("Grand Total", f"$ {total:.2f}")

                # Plot bar chart
                components = ["Base", "State Tax", "City Tax", "Lodging Tax"]
                values = [base, state_tax, city_tax, lodging_tax]
                fig, ax = plt.subplots()
                ax.bar(components, values)
                ax.set_title("Rate Components")
                ax.set_ylabel("Amount ($)")
                st.pyplot(fig)


if __name__ == "__main__":
    main()
