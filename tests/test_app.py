from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_app_runs_without_errors():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert len(at.metric) == 5
    assert at.title[0].value.endswith("Sales Dashboard")


def test_region_filter_updates_kpis():
    at = AppTest.from_file(APP, default_timeout=60).run()
    total_orders = at.metric[2].value
    at.sidebar.multiselect[0].select("Cusco").run()
    assert not at.exception
    assert at.metric[2].value != total_orders
