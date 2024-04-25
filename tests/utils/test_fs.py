from pathlib import Path

import pytest

from hyprshade.utils.fs import ls_dirs, scandir_recursive


class TestScandirRecursive:
    def test_empty(self, tmp_path: Path):
        assert list(scandir_recursive(tmp_path, max_depth=0)) == []

    def test_root(self, tmp_path: Path):
        for name in ["foo", "bar", "baz"]:
            (tmp_path / name).touch()

        assert sorted(f.name for f in scandir_recursive(tmp_path, max_depth=0)) == [
            "bar",
            "baz",
            "foo",
        ]

    def test_recursive(self, tmp_path: Path):
        (tmp_path / "foo").mkdir()
        (tmp_path / "foo" / "bar").mkdir()
        (tmp_path / "foo" / "baz").mkdir()
        for name in ["a", "b", "c"]:
            (tmp_path / name).touch()
        for name in ["d", "e", "f"]:
            (tmp_path / "foo" / name).touch()
        for name in ["g", "h", "i"]:
            (tmp_path / "foo" / "bar" / name).touch()
        assert sorted(f.name for f in scandir_recursive(tmp_path, max_depth=0)) == [
            "a",
            "b",
            "c",
        ]
        assert sorted(f.name for f in scandir_recursive(tmp_path, max_depth=1)) == [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
        ]
        assert sorted(f.name for f in scandir_recursive(tmp_path, max_depth=2)) == [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
        ]

    def test_negative_max_depth(self, tmp_path: Path):
        with pytest.raises(AssertionError):
            list(scandir_recursive(tmp_path, max_depth=-1))

    def test_invalid_path(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            list(scandir_recursive(tmp_path / "doesnotexist", max_depth=0))


class TestLsDirs:
    def test_empty(self):
        assert list(ls_dirs([])) == []

    def test_single(self, tmp_path: Path):
        (tmp_file := tmp_path / "foo").touch()
        assert list(ls_dirs([tmp_path])) == [str(tmp_file)]

    def test_multiple(self, tmp_path: Path):
        (tmp_file1 := tmp_path / "bar").touch()
        (tmp_file2 := tmp_path / "foo").touch()
        assert list(ls_dirs([tmp_path])) == list(map(str, [tmp_file1, tmp_file2]))

    def test_multiple_dirs(self, tmp_path_factory: pytest.TempPathFactory):
        paths = []
        for name in ["foo", "bar", "baz"]:
            tmp_path = tmp_path_factory.mktemp(name)
            (tmp_path / f"qux{name}").touch()
            paths.append(tmp_path)

        assert list(ls_dirs(paths)) == list(
            map(
                str,
                [
                    paths[1] / "quxbar",
                    paths[2] / "quxbaz",
                    paths[0] / "quxfoo",
                ],
            )
        )
