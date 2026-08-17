"""Control-system model and numerical analysis functions."""

from __future__ import annotations

from dataclasses import dataclass

import control as ct
import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class PlantParameters:
    """Parameters for G0(s) = (s + z) / [s(s + p1)(s + p2)]."""

    zero: float = 1.0
    pole_1: float = 2.0
    pole_2: float = 5.0

    def __post_init__(self) -> None:
        values = (self.zero, self.pole_1, self.pole_2)
        if not all(np.isfinite(values)):
            raise ValueError("Plant parameters must be finite.")
        if any(value <= 0 for value in values):
            raise ValueError("Pole and zero locations must be positive.")

    @property
    def numerator(self) -> NDArray[np.float64]:
        return np.array([1.0, self.zero], dtype=float)

    @property
    def denominator(self) -> NDArray[np.float64]:
        return np.polymul([1.0, 0.0], np.polymul([1.0, self.pole_1], [1.0, self.pole_2]))

    def base_system(self) -> ct.TransferFunction:
        """Return G0(s), excluding the variable root-locus gain."""
        return ct.tf(self.numerator, self.denominator)

    def loop_system(self, gain: float) -> ct.TransferFunction:
        """Return L(s) = K G0(s)."""
        return gain * self.base_system()

    def latex(self, gain: float | str = "K") -> str:
        gain_text = gain if isinstance(gain, str) else f"{gain:.3g}"
        return (
            rf"L(s)={gain_text}\,\frac{{s+{self.zero:g}}}"
            rf"{{s(s+{self.pole_1:g})(s+{self.pole_2:g})}}"
        )


def gain_vector(selected_gain: float, maximum: float = 1e3, points: int = 700) -> NDArray[np.float64]:
    """Return a logarithmic gain vector that includes zero and the selected gain."""
    upper = max(maximum, selected_gain)
    positive = np.geomspace(1e-4, upper, points)
    return np.unique(np.concatenate(([0.0, selected_gain], positive)))


def root_locus(
    plant: PlantParameters,
    selected_gain: float,
    maximum_gain: float = 1e3,
) -> tuple[NDArray[np.complex128], NDArray[np.float64]]:
    data = ct.root_locus_map(plant.base_system(), gains=gain_vector(selected_gain, maximum_gain))
    return np.asarray(data.loci), np.asarray(data.gains)


def closed_loop_poles(plant: PlantParameters, gain: float) -> NDArray[np.complex128]:
    return np.asarray(ct.poles(ct.feedback(plant.loop_system(gain), 1)))


def damping_metrics(poles: NDArray[np.complex128]) -> tuple[float, float]:
    """Return damping ratio and natural frequency of the dominant pole."""
    if poles.size == 0:
        return np.nan, np.nan
    dominant = poles[np.argmax(np.real(poles))]
    natural_frequency = float(abs(dominant))
    if np.isclose(natural_frequency, 0.0):
        return np.nan, natural_frequency
    damping_ratio = float(-np.real(dominant) / natural_frequency)
    return damping_ratio, natural_frequency


def frequency_response(
    system: ct.TransferFunction,
    omega: NDArray[np.float64],
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return Bode magnitude in dB and unwrapped phase in degrees."""
    response = ct.frequency_response(system, omega)
    magnitude = np.squeeze(np.asarray(response.magnitude))
    phase = np.unwrap(np.squeeze(np.asarray(response.phase)))
    magnitude_db = 20.0 * np.log10(np.maximum(magnitude, np.finfo(float).tiny))
    return magnitude_db, np.rad2deg(phase)


def stability_margins(system: ct.TransferFunction) -> tuple[float, float, float, float]:
    """Return gain margin, phase margin, and their crossover frequencies."""
    gain_margin, phase_margin, phase_cross, gain_cross = ct.margin(system)
    return tuple(float(value) for value in (gain_margin, phase_margin, phase_cross, gain_cross))
