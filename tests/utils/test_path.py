import pytest

from hyprshade.utils.path import MAX_ITERATIONS, stripped_basename


def test_stripped_basename():
    assert stripped_basename("file") == "file"
    assert stripped_basename("file.txt") == "file"
    assert stripped_basename("file.tar.gz") == "file"
    assert stripped_basename("file.") == "file"
    assert stripped_basename("file..") == "file"

    assert stripped_basename("./path/file") == "file"
    assert stripped_basename("/path/file") == "file"
    assert stripped_basename("./path/file.txt") == "file"
    assert stripped_basename("/path/file.txt") == "file"
    assert stripped_basename("./path/file.tar.gz") == "file"
    assert stripped_basename("/path/file.tar.gz") == "file"


def test_strip_all_extensions():
    assert stripped_basename("file") == "file"
    assert stripped_basename("file.txt") == "file"
    assert stripped_basename("file.tar.gz") == "file"
    assert stripped_basename("file.") == "file"
    assert stripped_basename("file..") == "file"


def test_strip_all_extensions_max_iterations():
    with pytest.raises(ValueError, match="Max iterations reached"):
        stripped_basename("file" + (".txt" * MAX_ITERATIONS))
