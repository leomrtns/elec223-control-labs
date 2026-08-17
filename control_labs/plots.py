"""Plotly figures used by both Streamlit applications."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .model import PlantParameters


COLORS = {
    "locus": "#2563eb",
    "selected": "#dc2626",
    "pole": "#111827",
    "zero": "#059669",
    "closed": "#7c3aed",
    "neutral": "#64748b",
}


def _axis_extent(values: np.ndarray, minimum_span: float = 2.0) -> tuple[float, float]:
    finite = np.asarray(values)[np.isfinite(values)]
    if not finite.size:
        return -minimum_span, minimum_span
    low, high = float(np.min(finite)), float(np.max(finite))
    span = max(high - low, minimum_span)
    padding = 0.12 * span
    return low - padding, high + padding


def root_locus_figure(
    plant: PlantParameters,
    loci: np.ndarray,
    selected_poles: np.ndarray,
    show_damping_grid: bool = True,
) -> go.Figure:
    fig = go.Figure()
    for branch in range(loci.shape[1]):
        values = loci[:, branch]
        fig.add_trace(
            go.Scatter(
                x=np.real(values),
                y=np.imag(values),
                mode="lines",
                line={"color": COLORS["locus"], "width": 2},
                name="Root locus" if branch == 0 else None,
                legendgroup="locus",
                showlegend=branch == 0,
                hovertemplate="Re: %{x:.3f}<br>Im: %{y:.3f}<extra></extra>",
            )
        )

    open_loop_poles = np.roots(plant.denominator)
    open_loop_zeros = np.roots(plant.numerator)
    fig.add_trace(
        go.Scatter(
            x=np.real(open_loop_poles),
            y=np.imag(open_loop_poles),
            mode="markers",
            marker={"symbol": "x", "size": 13, "color": COLORS["pole"], "line_width": 2},
            name="Open-loop poles",
            hovertemplate="Pole: %{x:.3f}%{y:+.3f}j<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=np.real(open_loop_zeros),
            y=np.imag(open_loop_zeros),
            mode="markers",
            marker={"symbol": "circle-open", "size": 13, "color": COLORS["zero"], "line_width": 3},
            name="Open-loop zeros",
            hovertemplate="Zero: %{x:.3f}%{y:+.3f}j<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=np.real(selected_poles),
            y=np.imag(selected_poles),
            mode="markers",
            marker={"symbol": "diamond", "size": 11, "color": COLORS["selected"]},
            name="Closed-loop poles at selected K",
            hovertemplate="Closed-loop pole: %{x:.3f}%{y:+.3f}j<extra></extra>",
        )
    )

    all_real = np.concatenate((np.real(loci).ravel(), np.real(selected_poles)))
    all_imag = np.concatenate((np.imag(loci).ravel(), np.imag(selected_poles)))
    x_range = _axis_extent(all_real)
    y_range = _axis_extent(all_imag)
    symmetric_y = max(abs(y_range[0]), abs(y_range[1]), 1.0)
    y_range = (-symmetric_y, symmetric_y)

    fig.add_vline(x=0, line_dash="dash", line_color=COLORS["neutral"], opacity=0.8)
    if show_damping_grid:
        radius = max(abs(x_range[0]), abs(x_range[1]), symmetric_y)
        for damping in (0.2, 0.4, 0.6, 0.8):
            angle = np.arccos(damping)
            x_end = -radius * np.cos(angle)
            y_end = radius * np.sin(angle)
            fig.add_shape(type="line", x0=0, y0=0, x1=x_end, y1=y_end, line={"color": "#94a3b8", "dash": "dot", "width": 1})
            fig.add_shape(type="line", x0=0, y0=0, x1=x_end, y1=-y_end, line={"color": "#94a3b8", "dash": "dot", "width": 1})

    fig.update_layout(
        title="Root locus of G₀(s)",
        xaxis_title="Real axis, σ (s⁻¹)",
        yaxis_title="Imaginary axis, jω (rad s⁻¹)",
        xaxis={"range": x_range, "zeroline": False},
        yaxis={"range": y_range, "scaleanchor": "x", "scaleratio": 1, "zeroline": True},
        hovermode="closest",
        legend={"orientation": "h", "y": 1.02, "yanchor": "bottom"},
        margin={"l": 50, "r": 25, "t": 90, "b": 50},
        height=620,
        uirevision="root-locus",
    )
    return fig

def bode_figure(
    omega: np.ndarray,
    open_magnitude_db: np.ndarray,
    open_phase_deg: np.ndarray,
    closed_magnitude_db: np.ndarray | None = None,
    closed_phase_deg: np.ndarray | None = None,
    phase_margin: float = np.nan,
    gain_margin: float = np.nan,
    phase_cross_frequency: float = np.nan,
    gain_cross_frequency: float = np.nan,
    show_margins: bool = True,
) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.10)
    fig.add_trace(
        go.Scatter(x=omega, y=open_magnitude_db, name="Open-loop magnitude", line={"color": COLORS["locus"], "width": 2.5}),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=omega, y=open_phase_deg, name="Open-loop phase", line={"color": COLORS["locus"], "width": 2.5}, showlegend=False),
        row=2,
        col=1,
    )
    if closed_magnitude_db is not None and closed_phase_deg is not None:
        fig.add_trace(
            go.Scatter(x=omega, y=closed_magnitude_db, name="Closed-loop magnitude", line={"color": COLORS["closed"], "width": 2, "dash": "dash"}),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(x=omega, y=closed_phase_deg, name="Closed-loop phase", line={"color": COLORS["closed"], "width": 2, "dash": "dash"}, showlegend=False),
            row=2,
            col=1,
        )

    if show_margins:
        fig.add_hline(y=0, line_dash="dot", line_color=COLORS["neutral"], row=1, col=1)
        fig.add_hline(y=-180, line_dash="dot", line_color=COLORS["neutral"], row=2, col=1)
        if np.isfinite(gain_cross_frequency) and gain_cross_frequency > 0 and np.isfinite(phase_margin):
            fig.add_vline(x=gain_cross_frequency, line_dash="dash", line_color=COLORS["selected"], row=2, col=1)
            fig.add_annotation(x=gain_cross_frequency, y=-180 + phase_margin / 2, text=f"PM = {phase_margin:.1f}°", showarrow=False, xanchor="left", row=2, col=1)
        if np.isfinite(phase_cross_frequency) and phase_cross_frequency > 0 and np.isfinite(gain_margin) and gain_margin > 0:
            gain_margin_db = 20 * np.log10(gain_margin)
            fig.add_vline(x=phase_cross_frequency, line_dash="dash", line_color=COLORS["selected"], row=1, col=1)
            fig.add_annotation(x=phase_cross_frequency, y=-gain_margin_db / 2, text=f"GM = {gain_margin_db:.1f} dB", showarrow=False, xanchor="left", row=1, col=1)

    fig.update_xaxes(type="log", title_text="Angular frequency, ω (rad s⁻¹)", row=2, col=1)
    fig.update_xaxes(type="log", row=1, col=1)
    fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
    fig.update_yaxes(title_text="Phase (degrees)", row=2, col=1)
    fig.update_layout(
        title="Bode response",
        height=720,
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.02, "yanchor": "bottom"},
        margin={"l": 65, "r": 25, "t": 90, "b": 55},
        uirevision="bode",
    )
    return fig
