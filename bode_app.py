"""Interactive Bode Plot teaching application for ELEC223."""

import control as ct
import numpy as np
import streamlit as st

from control_labs.model import frequency_response, stability_margins
from control_labs.plots import bode_figure
from control_labs.ui import finite_text, plant_controls


st.set_page_config(page_title="ELEC223 Bode Lab", page_icon="📈", layout="wide")
st.title("Interactive Bode Plot Lab")
st.caption("Connect poles, zeros and loop gain to frequency response and stability margins.")

plant, gain = plant_controls()
show_closed_loop = st.sidebar.toggle("Overlay closed-loop response", value=False)
show_margins = st.sidebar.toggle("Show stability margins", value=True)
frequency_decades = st.sidebar.slider("Frequency range, log₁₀(ω)", -3.0, 4.0, (-2.0, 3.0), 0.5)
samples = st.sidebar.select_slider("Frequency samples", options=[300, 500, 800, 1_200], value=500)

st.latex(plant.latex(gain))
omega = np.logspace(frequency_decades[0], frequency_decades[1], samples)
loop = plant.loop_system(gain)
open_magnitude, open_phase = frequency_response(loop, omega)
gain_margin, phase_margin, phase_cross, gain_cross = stability_margins(loop)

closed_magnitude = closed_phase = None
if show_closed_loop:
    closed = ct.feedback(loop, 1)
    closed_magnitude, closed_phase = frequency_response(closed, omega)

gain_margin_db = 20 * np.log10(gain_margin) if np.isfinite(gain_margin) and gain_margin > 0 else gain_margin
gm_col, pm_col, cross_col = st.columns([1, 1, 1.2], gap="large")
gm_col.metric("Gain margin", finite_text(gain_margin_db, " dB"), border=True)
pm_col.metric("Phase margin", finite_text(phase_margin, "°"), border=True)
cross_col.metric("Gain crossover, ωgc", finite_text(gain_cross, " rad/s"), border=True)

figure = bode_figure(
    omega,
    open_magnitude,
    open_phase,
    closed_magnitude,
    closed_phase,
    phase_margin=phase_margin,
    gain_margin=gain_margin,
    phase_cross_frequency=phase_cross,
    gain_cross_frequency=gain_cross,
    show_margins=show_margins,
)
st.plotly_chart(figure, width="stretch", config={"displaylogo": False})

with st.expander("What to investigate"):
    st.markdown(
        """
        - Increase **K** by a factor of ten: magnitude rises by 20 dB, but phase is unchanged.
        - Move a pole toward the origin: observe where its magnitude slope and phase transition begin.
        - Move the zero: compare its +20 dB/decade contribution with the poles' −20 dB/decade contributions.
        - Watch the gain and phase margins as the open-loop response approaches instability.
        """
    )
