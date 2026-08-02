from __future__ import annotations

import colorsys
from pathlib import Path
import re


SUITE_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PALETTE_SETS = {"SET-A", "SET-B", "SET-C", "SET-D", "SET-E", "SET-F"}
CORE_ROLES = {"primary", "contrast", "auxiliary", "neutral", "accent"}
TONE_TARGETS = {
    "primary_mid": 47.0,
    "contrast_mid": 58.0,
    "accent_soft": 70.0,
    "surface_tint": 93.0,
}
TONE_TO_CORE_ROLE = {
    "primary_mid": "primary",
    "contrast_mid": "contrast",
    "accent_soft": "accent",
    "surface_tint": "primary",
}
LSTAR_TOLERANCE = 0.5
MAX_FAMILY_HUE_DISTANCE = 1.0


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def parse_python_roles(source: str, roles: set[str]) -> dict[str, dict[str, str]]:
    group_pattern = re.compile(
        r'^\s*"(?P<name>SET-[A-Z])":\s*\{(?P<body>.*?)^\s*\},',
        re.MULTILINE | re.DOTALL,
    )
    role_names = "|".join(sorted(roles, key=len, reverse=True))
    role_pattern = re.compile(
        rf'"(?P<role>{role_names})"\s*:\s*"(?P<hex>#[0-9A-Fa-f]{{6}})"'
    )
    return {
        group.group("name"): {
            item.group("role"): item.group("hex").upper()
            for item in role_pattern.finditer(group.group("body"))
        }
        for group in group_pattern.finditer(source)
    }


def parse_matlab_tones(source: str) -> dict[str, dict[str, str]]:
    group_pattern = re.compile(
        r'^\s*case "(?P<name>SET-[A-Z])"(?P<body>.*?)'
        r'(?=^\s*case "|^\s*otherwise)',
        re.MULTILINE | re.DOTALL,
    )
    role_names = "|".join(sorted(TONE_TARGETS, key=len, reverse=True))
    tone_pattern = re.compile(
        rf"^\s*(?P<red>\d+)\s+(?P<green>\d+)\s+(?P<blue>\d+)"
        rf"\s*;?\s*\.\.\.\s*%\s*(?P<role>{role_names})"
        r"\s+(?P<hex>#[0-9A-Fa-f]{6})\s*$",
        re.MULTILINE,
    )
    palettes: dict[str, dict[str, str]] = {}
    for group in group_pattern.finditer(source):
        tones: dict[str, str] = {}
        for item in tone_pattern.finditer(group.group("body")):
            rgb_hex = "#{:02X}{:02X}{:02X}".format(
                int(item.group("red")),
                int(item.group("green")),
                int(item.group("blue")),
            )
            # 锁：MATLAB 扩展色的 RGB 数值必须与同行十六进制注释一致。
            assert rgb_hex == item.group("hex").upper()
            tones[item.group("role")] = rgb_hex
        palettes[group.group("name")] = tones
    return palettes


def rgb(hex_value: str) -> tuple[float, float, float]:
    return tuple(
        int(hex_value[index : index + 2], 16) / 255
        for index in (1, 3, 5)
    )


def lstar(hex_value: str) -> float:
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in rgb(hex_value)
    ]
    y_value = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    delta = 6 / 29
    f_value = (
        y_value ** (1 / 3)
        if y_value > delta**3
        else y_value / (3 * delta**2) + 4 / 29
    )
    return 116 * f_value - 16


def hue(hex_value: str) -> float:
    return colorsys.rgb_to_hls(*rgb(hex_value))[0] * 360


def hue_distance(left: float, right: float) -> float:
    absolute = abs(left - right)
    return min(absolute, 360 - absolute)


def test_each_palette_has_four_cross_language_companion_tones() -> None:
    python_source = read("cumcm-live-python-coder/assets/cumcm_plot_style.py")
    matlab_source = read("cumcm-live-matlab-coder/assets/cumcm_plot_style.m")
    python_tones = parse_python_roles(python_source, set(TONE_TARGETS))
    matlab_tones = parse_matlab_tones(matlab_source)

    # 锁：六个已批准配色组都必须提供完整扩展色阶。
    assert set(python_tones) == EXPECTED_PALETTE_SETS
    # 锁：Python 与 MATLAB 必须暴露相同的扩展色组。
    assert python_tones.keys() == matlab_tones.keys()
    for palette_set in EXPECTED_PALETTE_SETS:
        # 锁：每组扩展色必须恰含四个约定语义角色。
        assert set(python_tones[palette_set]) == set(TONE_TARGETS)
        # 锁：两种语言的同组扩展色必须逐字一致。
        assert python_tones[palette_set] == matlab_tones[palette_set]


def test_companion_tones_keep_target_lightness_and_parent_hue() -> None:
    python_source = read("cumcm-live-python-coder/assets/cumcm_plot_style.py")
    tones = parse_python_roles(python_source, set(TONE_TARGETS))
    cores = parse_python_roles(python_source, CORE_ROLES)

    for palette_set in EXPECTED_PALETTE_SETS:
        for tone_role, target in TONE_TARGETS.items():
            value = tones[palette_set][tone_role]
            # 锁：扩展色阶必须命中预定明度层级，不能退化为随意加色。
            assert abs(lstar(value) - target) <= LSTAR_TOLERANCE, (
                palette_set,
                tone_role,
                lstar(value),
            )
            parent_role = TONE_TO_CORE_ROLE[tone_role]
            # 锁：每个扩展色必须保留其父角色色相，维持单组色系统一。
            assert hue_distance(hue(value), hue(cores[palette_set][parent_role])) <= MAX_FAMILY_HUE_DISTANCE


def test_extended_colors_are_opt_in_and_core_cycle_remains_default() -> None:
    python_source = read("cumcm-live-python-coder/assets/cumcm_plot_style.py")
    matlab_source = read("cumcm-live-matlab-coder/assets/cumcm_plot_style.m")

    # 锁：两种样式资产都必须公开可选扩展系列和独立背景浅阶。
    assert '"extended_palette": extended_palette' in python_source
    assert "style.extendedColors" in matlab_source and "style.surfaceTint" in matlab_source
    # 锁：默认自动循环仍使用五个灰度安全核心色，不自动塞入扩展色。
    assert 'selected_palette["palette"]' in python_source
    assert "colororder(current, style.colors)" in matlab_source
    # 锁：扩展色不得通过随机配色实现。
    assert "random" not in python_source.lower()
    assert "random" not in matlab_source.lower()


def test_one_palette_and_one_object_map_govern_the_whole_paper() -> None:
    required_files = (
        "README.md",
        "SUITE.md",
        "cumcm-live-python-coder/SKILL.md",
        "cumcm-live-matlab-coder/SKILL.md",
        "cumcm-live-paper-writer/SKILL.md",
        "cumcm-live-python-coder/assets/run-manifest.md",
        "cumcm-live-matlab-coder/assets/run-manifest.md",
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md",
    )
    for relative_path in required_files:
        content = read(relative_path)
        # 锁：全链路必须显式传递所选配色组。
        assert "palette_set" in content, relative_path
        # 锁：全链路必须冻结对象到视觉角色的统一映射。
        assert "object_color_map" in content, relative_path

    playbook = read("cumcm-live-paper-writer/references/abc-figure-design-playbook.md")
    # 锁：扩展色只能增加同一色系层次，不能变成第二套配色。
    assert "扩展色不是第二套配色" in playbook
    # 锁：类别过多时必须改用分面，而不是继续临时造色。
    assert "超过 8 个类别时优先排序、分面或小多图" in playbook
