from pathlib import Path

from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).parents[1]


def _assert_app_runs(filename: str) -> None:
    app = AppTest.from_file(str(PROJECT_ROOT / filename), default_timeout=15).run()
    assert not app.exception, [exception.value for exception in app.exception]


def test_root_locus_app_runs_with_defaults() -> None:
    _assert_app_runs("root_locus_app.py")


def test_bode_app_runs_with_defaults() -> None:
    _assert_app_runs("bode_app.py")
