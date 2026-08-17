"""Shared Streamlit controls and formatting helpers."""

from __future__ import annotations

import math

import streamlit as st

from .model import PlantParameters


def plant_controls() -> tuple[PlantParameters, float]:
    st.sidebar.header("System parameters")
    st.sidebar.caption(r"$G_0(s)=\dfrac{s+z}{s(s+p_1)(s+p_2)}$ and $L(s)=K G_0(s)$")
    zero = st.sidebar.slider("Zero location, z", 0.1, 10.0, 1.0, 0.1)
    pole_1 = st.sidebar.slider("Pole location, p₁", 0.2, 12.0, 2.0, 0.1)
    pole_2 = st.sidebar.slider("Pole location, p₂", 0.2, 20.0, 5.0, 0.1)
    log_gain = st.sidebar.slider("Loop gain, log₁₀(K)", -2.0, 3.0, 0.0, 0.02)
    gain = 10.0**log_gain
    st.sidebar.metric("Selected gain, K", f"{gain:.4g}")
    return PlantParameters(zero=zero, pole_1=pole_1, pole_2=pole_2), gain


def finite_text(value: float, unit: str = "", precision: int = 2) -> str:
    if math.isnan(value):
        return "Not defined"
    if math.isinf(value):
        return "∞"
    return f"{value:.{precision}f}{unit}"
