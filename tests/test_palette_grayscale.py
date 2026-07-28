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
# 四组是当前去指纹设计的最低组数，少于四组会显著降低跨队伍差异。
MIN_PALETTE_SET_COUNT = 4
# 10 是灰度可辨的硬底线；实际设计目标为相邻约 12。
MIN_LSTAR_DISTANCE = 10.0
# 白底学术图的系列色保持在此明度窗口内。
MIN_VISIBLE_LSTAR = 20.0
MAX_VISIBLE_LSTAR = 82.0
# 彩色系列需要可见色相但保持克制，neutral 则维持近无彩。
MIN_COLORED_SATURATION = 0.20
MAX_COLORED_SATURATION = 0.65
MAX_NEUTRAL_SATURATION = 0.10
# 同角色跨组至少相隔 60° 才能形成可辨识的组间性格。
MIN_CROSS_SET_HUE_DISTANCE = 60.0


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
            # 锁：MATLAB RGB 三元组必须与同行十六进制注释逐字等价。
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

    # 锁：Python 至少保留四组可选配色。
    assert len(python_palettes) >= MIN_PALETTE_SET_COUNT
    # 锁：MATLAB 至少保留同等数量的配色组。
    assert len(matlab_palettes) >= MIN_PALETTE_SET_COUNT
    # 锁：两种语言必须暴露完全相同的配色组名。
    assert python_palettes.keys() == matlab_palettes.keys()
    for palette_name in python_palettes:
        # 锁：Python 每组必须恰含五个数据系列角色。
        assert set(python_palettes[palette_name]) == ROLES
        # 锁：MATLAB 每组必须恰含相同五个角色。
        assert set(matlab_palettes[palette_name]) == ROLES
        # 锁：两种语言的同名组必须表示逐字相同的颜色。
        assert python_palettes[palette_name] == matlab_palettes[palette_name]


def test_series_colors_have_monotonic_and_print_safe_lstar_spacing() -> None:
    python_palettes, _ = parsed_palettes()

    for palette_name, colors in python_palettes.items():
        levels = {role: lstar(value) for role, value in colors.items()}
        for role, target in TARGET_LSTAR.items():
            # 锁：每个角色的实测 L* 必须命中既定明度阶梯。
            assert abs(levels[role] - target) <= LSTAR_TOLERANCE, (
                palette_name,
                role,
                levels[role],
            )
        # 锁：五个角色必须按指定顺序形成严格递增明度阶梯。
        assert all(
            levels[left] < levels[right]
            for left, right in zip(LSTAR_ROLE_ORDER, LSTAR_ROLE_ORDER[1:])
        ), palette_name

        pairwise_differences = [
            abs(levels[left] - levels[right])
            for left, right in combinations(ROLES, 2)
        ]
        # 锁：组内任意两种系列色都不得低于灰度可辨硬底线。
        assert min(pairwise_differences) >= MIN_LSTAR_DISTANCE, palette_name

        sorted_levels = sorted(levels.values())
        adjacent_differences = [
            right - left
            for left, right in zip(sorted_levels, sorted_levels[1:])
        ]
        # 锁：按明度排序后的相邻系列仍须满足灰度可辨硬底线。
        assert min(adjacent_differences) >= MIN_LSTAR_DISTANCE, palette_name
        # 锁：最暗系列不能与坐标轴和正文黑色混同。
        assert min(sorted_levels) >= MIN_VISIBLE_LSTAR, palette_name
        # 锁：最亮系列在白底细线中仍须可见。
        assert max(sorted_levels) <= MAX_VISIBLE_LSTAR, palette_name


def test_colored_roles_are_saturated_but_academically_restrained() -> None:
    python_palettes, _ = parsed_palettes()

    for palette_name, colors in python_palettes.items():
        for role in COLORED_ROLES:
            saturation = hls_saturation(colors[role])
            # 锁：彩色角色既要保留可见色相，又不能过艳。
            assert MIN_COLORED_SATURATION <= saturation <= MAX_COLORED_SATURATION, (
                palette_name,
                role,
                saturation,
            )
        # 锁：neutral 必须保持近无彩以承担参考系列语义。
        assert hls_saturation(colors["neutral"]) <= MAX_NEUTRAL_SATURATION, palette_name


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
        # 锁：同角色在任意两组间必须保持足够色相距离。
        assert min(distances) >= MIN_CROSS_SET_HUE_DISTANCE, (
            role,
            min(distances),
        )


def test_accent_is_the_most_saturated_series_color() -> None:
    python_palettes, _ = parsed_palettes()

    for palette_name, colors in python_palettes.items():
        saturations = {
            role: hls_saturation(value) for role, value in colors.items()
        }
        # 锁：accent 必须是组内最高饱和度以维持重点语义。
        assert saturations["accent"] == max(saturations.values()), palette_name


def test_runtime_styles_keep_hardcoded_colors_without_lstar_solver() -> None:
    python_style = read("cumcm-live-python-coder/assets/cumcm_plot_style.py")
    matlab_style = read("cumcm-live-matlab-coder/assets/cumcm_plot_style.m")

    for source in (python_style, matlab_style):
        # 锁：运行时样式不得引入 HLS 反解求色逻辑。
        assert "rgb_to_hls" not in source
        # 锁：运行时样式不得动态从 HLS 生成配色。
        assert "hls_to_rgb" not in source
        # 锁：一次性色彩求解依赖不得进入出图资产。
        assert "colorsys" not in source
