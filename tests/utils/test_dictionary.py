from hyprshade.utils.dictionary import deep_merge


class TestDeepMerge:
    def test_empty(self):
        assert deep_merge({}, {}, strategy="force") == {}
        assert deep_merge({}, {}, strategy="keep") == {}

    def test_shallow(self):
        assert deep_merge({"foo": "bar"}, {"foo": "baz"}, strategy="force") == {
            "foo": "baz"
        }
        assert deep_merge({"foo": "bar"}, {"foo": "baz"}, strategy="keep") == {
            "foo": "bar"
        }

        assert deep_merge({"foo": "bar"}, {"baz": "qux"}, strategy="force") == {
            "foo": "bar",
            "baz": "qux",
        }
        assert deep_merge({"foo": "bar"}, {"baz": "qux"}, strategy="keep") == {
            "foo": "bar",
            "baz": "qux",
        }

    def test_deep(self):
        assert deep_merge(
            {"foo": {"bar": "baz"}},
            {"foo": {"bar": "qux"}},
            strategy="force",
        ) == {"foo": {"bar": "qux"}}
        assert deep_merge(
            {"foo": {"bar": "baz"}},
            {"foo": {"bar": "qux"}},
            strategy="keep",
        ) == {"foo": {"bar": "baz"}}

        assert deep_merge(
            {"foo": {"bar": "baz"}},
            {"foo": {"baz": "qux"}},
            strategy="force",
        ) == {"foo": {"bar": "baz", "baz": "qux"}}
        assert deep_merge(
            {"foo": {"bar": "baz"}},
            {"foo": {"baz": "qux"}},
            strategy="keep",
        ) == {"foo": {"bar": "baz", "baz": "qux"}}

        assert deep_merge(
            {"foo": {"bar": {"baz": "qux"}}},
            {"foo": {"bar": {"baz": "quux", "qux": "quuz"}}, "baz": "qux"},
            strategy="force",
        ) == {"foo": {"bar": {"baz": "quux", "qux": "quuz"}}, "baz": "qux"}
        assert deep_merge(
            {"foo": {"bar": {"baz": "qux"}}},
            {"foo": {"bar": {"baz": "quux", "qux": "quuz"}}, "baz": "qux"},
            strategy="keep",
        ) == {"foo": {"bar": {"baz": "qux", "qux": "quuz"}}, "baz": "qux"}

    def test_referential_equality(self):
        d: dict = {}
        assert deep_merge(d, {"foo": "bar"}, strategy="force") is d
        assert deep_merge(d, {"baz": "qux"}, strategy="keep") is d
