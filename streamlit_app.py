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
    """Compute the base rate and tax breakdown for a given grand total.

    The hotel system appears to compute the base rate by first
    estimating it as total/(1 + sum of rates) and then adjusting by
    one cent when the state tax rounding overshoots.  The state tax is
    computed last as the residual so that the sum of base and taxes
    exactly matches the grand total.

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
    # Convert total to Decimal with two decimal places
    total_dec = Decimal(str(target_total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # Estimate the base by removing all tax rates (state+city+lodging)
    naive_base = total_dec / (1 + STATE_TAX_RATE + CITY_TAX_RATE + LODGING_TAX_RATE)
    naive_base = naive_base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # Compute city and lodging taxes using the naive base
    city_tax = (naive_base * CITY_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    lodging_tax = (naive_base * LODGING_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # State tax predicted using rounding up (not used directly)
    predicted_state = (naive_base * STATE_TAX_RATE * 100).to_integral_value(rounding=ROUND_UP) / Decimal("100")
    # Residual state tax required to hit the total
    residual_state = total_dec - naive_base - city_tax - lodging_tax
    residual_state = residual_state.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # If the predicted state exceeds the residual, the base is too high.
    # Lower the base by one cent and recompute city, lodging and state.
    if predicted_state > residual_state:
        adjusted_base = naive_base - Decimal("0.01")
        if adjusted_base <= 0:
            return None
        city_tax = (adjusted_base * CITY_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        lodging_tax = (adjusted_base * LODGING_TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        state_tax = total_dec - adjusted_base - city_tax - lodging_tax
        state_tax = state_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(adjusted_base), float(state_tax), float(city_tax), float(lodging_tax), float(total_dec)
    else:
        # Use the naive base and residual state
        return float(naive_base), float(residual_state), float(city_tax), float(lodging_tax), float(total_dec)


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
