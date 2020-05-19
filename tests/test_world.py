"""A dummy test file."""
from pygohome.world import World


def test_true() -> None:
    """This should work."""
    assert True


def test_there_is_world() -> None:
    """There is a world."""
    world = World()
    assert world
