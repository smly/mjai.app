def test_import():
    import mlibriichi.mlibriichi.arena

    assert mlibriichi.mlibriichi.arena
    assert "py_match" in dir(mlibriichi.mlibriichi.arena.Match)
