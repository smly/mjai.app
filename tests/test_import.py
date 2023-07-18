def test_import():
    import mjaisimulator.mjaisimulator.arena

    assert mjaisimulator.mjaisimulator.arena
    assert "py_match" in dir(mjaisimulator.mjaisimulator.arena.Match)
