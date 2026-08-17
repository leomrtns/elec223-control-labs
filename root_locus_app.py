"""Interactive Root Locus teaching application for ELEC223."""

import numpy as np
import streamlit as st

from control_labs.model import closed_loop_poles, damping_metrics, root_locus
from control_labs.plots import root_locus_figure
from control_labs.ui import finite_text, plant_controls


st.set_page_config(page_title="ELEC223 Root Locus Lab", page_icon="🎯", layout="wide")
st.title("Interactive Root Locus Lab")
st.caption("Explore how gain moves the closed-loop poles, and how plant poles and zeros reshape the locus.")

plant, gain = plant_controls()
show_grid = st.sidebar.toggle("Show damping-ratio grid", value=True)
maximum_gain = st.sidebar.select_slider("Maximum locus gain", options=[10.0, 100.0, 1_000.0, 10_000.0], value=1_000.0)

st.latex(plant.latex())
loci, _ = root_locus(plant, selected_gain=gain, maximum_gain=maximum_gain)
poles = closed_loop_poles(plant, gain)
damping_ratio, natural_frequency = damping_metrics(poles)
stable = bool(np.all(np.real(poles) < 0))

status_col, damping_col, frequency_col = st.columns(3, gap="large")
status_col.metric("Closed-loop stability", "Stable" if stable else "Unstable", border=True)
damping_col.metric("Dominant damping ratio, ζ", finite_text(damping_ratio, precision=3), border=True)
frequency_col.metric(
    "Dominant natural frequency, ωₙ",
    finite_text(natural_frequency, " rad/s"),
    border=True,
)

figure = root_locus_figure(plant, loci, poles, show_damping_grid=show_grid)
st.plotly_chart(figure, width="stretch", config={"displaylogo": False})

with st.expander("How to use this plot"):
    st.markdown(
        """
        - Move **K**: the red diamonds move along the blue locus, while the locus stays fixed.
        - Move **p₁**, **p₂**, or **z**: the open-loop system changes, so the complete locus is recalculated.
        - A closed-loop system is stable only when every red diamond is in the left half-plane.
        - The dotted rays indicate constant damping ratio; points farther from the origin have higher natural frequency.
        """
    )
