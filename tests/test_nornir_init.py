import threading

from nornir_mcp.nornir_init import NornirManager


def test_singleton_instance():
    """Test that NornirManager is a singleton."""
    m1 = NornirManager.instance()
    m2 = NornirManager.instance()
    assert m1 is m2


def test_thread_safe_singleton():
    """Test thread safety of the singleton (basic check)."""
    instances = []

    def get_instance():
        instances.append(NornirManager.instance())

    threads = [threading.Thread(target=get_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for i in range(1, len(instances)):
        assert instances[i] is instances[0]
