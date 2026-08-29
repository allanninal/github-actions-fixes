from actions_cache_audit import prefix_of, unstable_keys


def cache(key, size=1000):
    return {"key": key, "size_in_bytes": size}


def test_prefix_strips_the_hash_segment():
    assert prefix_of("Linux-node-a1b2c3d4e5f6") == "Linux-node"


def test_a_key_with_no_hash_is_unchanged():
    assert prefix_of("Linux-node") == "Linux-node"


def test_a_healthy_cache_is_not_flagged():
    caches = [cache(f"Linux-node-{h}") for h in ("a1b2c3d4", "b2c3d4e5")]
    assert unstable_keys(caches) == {}


def test_many_entries_on_one_prefix_is_flagged():
    """The signature of a key that changes every run."""
    caches = [cache(f"Linux-node-{i:08x}") for i in range(9)]
    assert "Linux-node" in unstable_keys(caches)


def test_the_threshold_is_respected():
    caches = [cache(f"Linux-node-{i:08x}") for i in range(4)]
    assert unstable_keys(caches, min_entries=5) == {}
