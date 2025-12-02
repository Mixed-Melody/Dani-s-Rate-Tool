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

    This function searches around an approximate base value to find a
    candidate base rate (in cents) whose computed total exactly matches
    the desired total when taxes are rounded according to the hotel
    rules.

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
    target_total_dec = Decimal(str(target_total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # Rough starting point (ignores rounding effects)
    approx_base = target_total_dec / (1 + STATE_TAX_RATE + CITY_TAX_RATE + LODGING_TAX_RATE)
    # Search plus/minus $3.00 around the approximate base in 1‑cent increments
    # to account for rounding differences.
    for offset_cents in range(-300, 301):
        candidate_base = (approx_base + Decimal(offset_cents) * Decimal("0.01")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if candidate_base <= 0:
            continue
        # Compute the total for this candidate
        base_f, st, ct, lt, total_f = compute_breakdown(float(candidate_base))
        if abs(total_f - float(target_total_dec)) < 0.005:
            return base_f, st, ct, lt, total_f
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
