import numpy as np

from control_labs.model import (
    PlantParameters,
    closed_loop_poles,
    frequency_response,
    root_locus,
)


def test_default_plant_coefficients() -> None:
    plant = PlantParameters()
    np.testing.assert_allclose(plant.numerator, [1.0, 1.0])
    np.testing.assert_allclose(plant.denominator, [1.0, 7.0, 10.0, 0.0])


def test_closed_loop_poles_match_characteristic_polynomial() -> None:
    plant = PlantParameters(zero=1.5, pole_1=2.0, pole_2=6.0)
    gain = 8.0
    padded_numerator = np.pad(gain * plant.numerator, (len(plant.denominator) - len(plant.numerator), 0))
    expected = np.roots(plant.denominator + padded_numerator)
    actual = closed_loop_poles(plant, gain)
    np.testing.assert_allclose(np.sort_complex(actual), np.sort_complex(expected))


def test_root_locus_contains_selected_closed_loop_poles() -> None:
    plant = PlantParameters()
    gain = 3.7
    loci, gains = root_locus(plant, gain, maximum_gain=100)
    selected_index = int(np.argmin(abs(gains - gain)))
    np.testing.assert_allclose(
        np.sort_complex(loci[selected_index]),
        np.sort_complex(closed_loop_poles(plant, gain)),
        atol=1e-8,
    )


def test_tenfold_gain_adds_twenty_db_without_phase_change() -> None:
    plant = PlantParameters()
    omega = np.logspace(-2, 3, 100)
    magnitude_1, phase_1 = frequency_response(plant.loop_system(1.0), omega)
    magnitude_10, phase_10 = frequency_response(plant.loop_system(10.0), omega)
    np.testing.assert_allclose(magnitude_10 - magnitude_1, 20.0, atol=1e-10)
    np.testing.assert_allclose(phase_10, phase_1, atol=1e-10)
