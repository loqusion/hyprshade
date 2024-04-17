from hyprshade.utils.base64 import pathsafe_b64decode, pathsafe_b64encode


class TestPathEncode:
    def test_path(self):
        assert (
            pathsafe_b64encode(
                "/usr/share/hyprshade/shaders/blue-light-filter.glsl.mustache"
            )
            == b"L3Vzci9zaGFyZS9oeXByc2hhZGUvc2hhZGVycy9ibHVlLWxpZ2h0LWZpbHRlci5nbHNsLm11c3RhY2hl"
        )

    def test_unencoded_input_length_not_multiple_of_three(self):
        assert (
            pathsafe_b64encode("/usr/share/hyprshade") == b"L3Vzci9zaGFyZS9oeXByc2hhZGU"
        )

    def test_valid_posix_file_name(self):
        assert b"/" not in pathsafe_b64encode(bytes.fromhex("FFE0"))


class TestPathDecode:
    def test_path(self):
        assert (
            pathsafe_b64decode(
                "L3Vzci9zaGFyZS9oeXByc2hhZGUvc2hhZGVycy9ibHVlLWxpZ2h0LWZpbHRlci5nbHNsLm11c3RhY2hl"
            )
            == b"/usr/share/hyprshade/shaders/blue-light-filter.glsl.mustache"
        )

    def test_decoded_input_length_not_multiple_of_four(self):
        assert (
            pathsafe_b64decode("L3Vzci9zaGFyZS9oeXByc2hhZGU") == b"/usr/share/hyprshade"
        )


class TestPathEncodeDecode:
    def test(self):
        encoded = pathsafe_b64encode(bytes.fromhex("FFE0"))
        assert pathsafe_b64decode(encoded) == bytes.fromhex("FFE0")
