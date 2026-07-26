from __future__ import annotations

import colorsys
from itertools import combinations
from pathlib import Path
import re


SUITE_ROOT = Path(__file__).resolve().parents[1]
ROLES = {"primary", "contrast", "auxiliary", "neutral", "accent"}
COLORED_ROLES = ("primary", "contrast", "auxiliary", "accent")
LSTAR_ROLE_ORDER = ("primary", "accent", "neutral", "contrast", "auxiliary")
TARGET_LSTAR = {
    "primary": 29.6,
    "accent": 41.8,
    "neutral": 53.9,
    "contrast": 66.2,
    "auxiliary": 78.3,
}
LSTAR_TOLERANCE = 0.5


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def parse_python_palettes(source: str) -> dict[str, dict[str, str]]:
    group_pattern = re.compile(
        r'^\s*"(?P<name>SET-[A-Z])":\s*\{(?P<body>.*?)^\s*\},',
        re.MULTILINE | re.DOTALL,
    )
    role_pattern = re.compile(
        r'"(?P<role>primary|contrast|auxiliary|neutral|accent)"'
        r'\s*:\s*"(?P<hex>#[0-9A-Fa-f]{6})"'
    )
    palettes = {}
    for match in group_pattern.finditer(source):
        roles = {
            item.group("role"): item.group("hex").upper()
            for item in role_pattern.finditer(match.group("body"))
        }
        palettes[match.group("name")] = roles
    return palettes


def parse_matlab_palettes(source: str) -> dict[str, dict[str, str]]:
    group_pattern = re.compile(
        r'^\s*case "(?P<name>SET-[A-Z])"(?P<body>.*?)'
        r'(?=^\s*case "|^\s*otherwise)',
        re.MULTILINE | re.DOTALL,
    )
    role_pattern = re.compile(
        r"^\s*(?P<red>\d+)\s+(?P<green>\d+)\s+(?P<blue>\d+)"
        r"\s*;?\s*\.\.\.\s*%\s*"
        r"(?P<role>primary|contrast|auxiliary|neutral|accent)"
        r"\s+(?P<hex>#[0-9A-Fa-f]{6})\s*$",
        re.MULTILINE,
    )
    palettes = {}
    for match in group_pattern.finditer(source):
        roles = {}
        for item in role_pattern.finditer(match.group("body")):
            rgb_hex = "#{:02X}{:02X}{:02X}".format(
                int(item.group("red")),
                int(item.group("green")),
                int(item.group("blue")),
            )
            comment_hex = item.group("hex").upper()
            assert rgb_hex == comment_hex
            roles[item.group("role")] = rgb_hex
        palettes[match.group("name")] = roles
    return palettes


def lstar(hex_value: str) -> float:
    channels = [
        int(hex_value[index : index + 2], 16) / 255
        for index in (1, 3, 5)
    ]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    y_value = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    delta = 6 / 29
    f_value = (
        y_value ** (1 / 3)
        if y_value > delta**3
        else y_value / (3 * delta**2) + 4 / 29
    )
    return 116 * f_value - 16


def hls_saturation(hex_value: str) -> float:
    rgb = tuple(
        int(hex_value[index : index + 2], 16) / 255
        for index in (1, 3, 5)
    )
    return colorsys.rgb_to_hls(*rgb)[2]


def hls_hue_degrees(hex_value: str) -> float:
    rgb = tuple(
        int(hex_value[index : index + 2], 16) / 255
        for index in (1, 3, 5)
    )
    return colorsys.rgb_to_hls(*rgb)[0] * 360


def hue_distance(left: float, right: float) -> float:
    absolute = abs(left - right)
    return min(absolute, 360 - absolute)


def parsed_palettes() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    python_palettes = parse_python_palettes(
        read("cumcm-live-python-coder/assets/cumcm_plot_style.py")
    )
    matlab_palettes = parse_matlab_palettes(
        read("cumcm-live-matlab-coder/assets/cumcm_plot_style.m")
    )
    return python_palettes, matlab_palettes


def test_four_or_more_complete_palette_sets_match_across_languages() -> None:
    python_palettes, matlab_palettes = parsed_palettes()

    assert len(python_palettes) >= 4
    assert len(matlab_palettes) >= 4
    assert python_palettes.keys() == matlab_palettes.keys()
    for palette_name in python_palettes:
        assert set(python_palettes[palette_name]) == ROLES
        assert set(matlab_palettes[palette_name]) == ROLES
        assert python_palettes[palette_name] == matlab_palettes[palette_name]


def test_series_colors_have_monotonic_and_print_safe_lstar_spacing() -> None:
    python_palettes, _ = parsed_palettes()

    for palette_name, colors in python_palettes.items():
        levels = {role: lstar(value) for role, value in colors.items()}
        for role, target in TARGET_LSTAR.items():
            assert abs(levels[role] - target) <= LSTAR_TOLERANCE, (
                palette_name,
                role,
                levels[role],
            )
        assert all(
            levels[left] < levels[right]
            for left, right in zip(LSTAR_ROLE_ORDER, LSTAR_ROLE_ORDER[1:])
        ), palette_name

        pairwise_differences = [
            abs(levels[left] - levels[right])
            for left, right in combinations(ROLES, 2)
        ]
        assert min(pairwise_differences) >= 10, palette_name

        sorted_levels = sorted(levels.values())
        adjacent_differences = [
            right - left
            for left, right in zip(sorted_levels, sorted_levels[1:])
        ]
        assert min(adjacent_differences) >= 10, palette_name
        assert min(sorted_levels) >= 20, palette_name
        assert max(sorted_levels) <= 82, palette_name


def test_colored_roles_are_saturated_but_academically_restrained() -> None:
    python_palettes, _ = parsed_palettes()

    for palette_name, colors in python_palettes.items():
        for role in COLORED_ROLES:
            saturation = hls_saturation(colors[role])
            assert 0.20 <= saturation <= 0.65, (
                palette_name,
                role,
                saturation,
            )
        assert hls_saturation(colors["neutral"]) <= 0.10, palette_name


def test_same_role_hues_are_separated_across_palette_sets() -> None:
    python_palettes, _ = parsed_palettes()

    for role in COLORED_ROLES:
        hues = [
            hls_hue_degrees(colors[role])
            for colors in python_palettes.values()
        ]
        distances = [
            hue_distance(left, right)
            for left, right in combinations(hues, 2)
        ]
        assert min(distances) >= 60, (role, min(distances))


def test_accent_is_the_most_saturated_series_color() -> None:
    python_palettes, _ = parsed_palettes()

    for palette_name, colors in python_palettes.items():
        saturations = {
            role: hls_saturation(value) for role, value in colors.items()
        }
        assert saturations["accent"] == max(saturations.values()), palette_name


def test_runtime_styles_keep_hardcoded_colors_without_lstar_solver() -> None:
    python_style = read("cumcm-live-python-coder/assets/cumcm_plot_style.py")
    matlab_style = read("cumcm-live-matlab-coder/assets/cumcm_plot_style.m")

    for source in (python_style, matlab_style):
        assert "rgb_to_hls" not in source
        assert "hls_to_rgb" not in source
        assert "colorsys" not in source
