from f1.processing.lap_processor import filter_valid_laps, build_driver_index, compute_top_n_laps
from f1.domain.models import Lap, Driver


def test_filter_valid_laps(mock_laps_response):
    laps = [Lap.from_dict(d) for d in mock_laps_response]
    valid = filter_valid_laps(laps)
    assert all(l.lap_duration is not None for l in valid)
    assert all(not l.is_pit_out_lap for l in valid)


def test_compute_top_n_laps(mock_laps_response, mock_drivers_response):
    laps = [Lap.from_dict(d) for d in mock_laps_response]
    drivers = [Driver.from_dict(d) for d in mock_drivers_response]
    valid = filter_valid_laps(laps)
    idx = build_driver_index(drivers)
    top = compute_top_n_laps(valid, idx, n=10)
    assert len(top) >= 1
    assert top[0].lap_duration <= top[-1].lap_duration
