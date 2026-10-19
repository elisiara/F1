from f1.dashboard import build_service


def test_build_service_returns_singleton_like_instance():
    svc1 = build_service()
    svc2 = build_service()
    assert svc1 is svc2