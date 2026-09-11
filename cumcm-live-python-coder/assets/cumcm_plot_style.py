"""Portable Matplotlib style helpers for CUMCM paper figures."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

PALETTE_FAMILY = "MORANDI"
PALETTE_REVISION = "MORANDI-2026-09"

PALETTE_SETS = {
    "SET-A": {
        "primary": "#41416D",
        "contrast": "#A4A46B",
        "auxiliary": "#D4BAD4",
        "neutral": "#818181",
        "accent": "#984C4C",
        "primary_mid": "#6A6AA2",
        "contrast_mid": "#8E8E5B",
        "accent_soft": "#C4A3A3",
        "surface_tint": "#EBEBEF",
        "basis": "莫兰迪灰蓝与陶红；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.43–78.38，最小相邻 ΔL*=12.16。",
    },
    "SET-B": {
        "primary": "#5E385E",
        "contrast": "#7AAD7A",
        "auxiliary": "#D5BCBC",
        "neutral": "#818181",
        "accent": "#656533",
        "primary_mid": "#935C93",
        "contrast_mid": "#619861",
        "accent_soft": "#AEAE80",
        "surface_tint": "#EEEAEE",
        "basis": "莫兰迪灰紫与橄榄；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.45–78.31，最小相邻 ΔL*=12.11。",
    },
    "SET-C": {
        "primary": "#623B3B",
        "contrast": "#75AAAA",
        "auxiliary": "#C4C4A1",
        "neutral": "#818181",
        "accent": "#386E38",
        "primary_mid": "#996060",
        "contrast_mid": "#5F9595",
        "accent_soft": "#8CB68C",
        "surface_tint": "#EEEAEA",
        "basis": "莫兰迪陶土与鼠尾草；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.51–78.34，最小相邻 ΔL*=12.11。",
    },
    "SET-D": {
        "primary": "#47472B",
        "contrast": "#9E9EC3",
        "auxiliary": "#AACAAA",
        "neutral": "#818181",
        "accent": "#366B6B",
        "primary_mid": "#727247",
        "contrast_mid": "#8888B3",
        "accent_soft": "#88B3B3",
        "surface_tint": "#EBEBE6",
        "basis": "莫兰迪橄榄与灰青；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.46–78.28，最小相邻 ΔL*=12.02。",
    },
    "SET-E": {
        "primary": "#2E4D2E",
        "contrast": "#BD94BD",
        "auxiliary": "#A7C8C8",
        "neutral": "#818181",
        "accent": "#5A5AAC",
        "primary_mid": "#4C7A4C",
        "contrast_mid": "#AB7CAB",
        "accent_soft": "#A9A9C8",
        "surface_tint": "#E7ECE7",
        "basis": "莫兰迪森林灰绿与雾蓝；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.63–78.28，最小相邻 ΔL*=12.01。",
    },
    "SET-F": {
        "primary": "#2D4B4B",
        "contrast": "#BF9797",
        "auxiliary": "#C0C0D7",
        "neutral": "#818181",
        "accent": "#8F488F",
        "primary_mid": "#4B7777",
        "contrast_mid": "#AE8080",
        "accent_soft": "#C3A0C3",
        "surface_tint": "#E7ECEC",
        "basis": "莫兰迪灰青与灰玫瑰；彩色核心 HLS 饱和度约 0.22–0.34，L*≈29.66–78.35，最小相邻 ΔL*=12.04。",
    },
}

_SERIES_ROLES = ("primary", "contrast", "auxiliary", "neutral", "accent")
_TONE_ROLES = ("primary_mid", "contrast_mid", "accent_soft", "surface_tint")
_CHROME_COLORS = {
    "light": "#F5F5F2",
    "text": "#4F555A",
    "grid": "#D1D5DB",
}


def get_palette_set(palette_set: str) -> dict[str, object]:
    """Return one explicitly selected, internally consistent palette set."""
    if not palette_set or not palette_set.strip():
        raise ValueError(
            "palette_set is required; explicitly choose SET-A, SET-B, SET-C, SET-D, SET-E, or SET-F"
        )
    normalized = palette_set.strip().upper()
    if normalized not in PALETTE_SETS:
        choices = ", ".join(PALETTE_SETS)
        raise ValueError(f"unknown palette_set {palette_set!r}; choose one of: {choices}")

    definition = PALETTE_SETS[normalized]
    colors = {role: definition[role] for role in _SERIES_ROLES}
    tones = {role: definition[role] for role in _TONE_ROLES}
    palette = [colors[role] for role in _SERIES_ROLES]
    extended_palette = palette + [
        tones["primary_mid"],
        tones["contrast_mid"],
        tones["accent_soft"],
    ]
    sequential = LinearSegmentedColormap.from_list(
        f"cumcm_{normalized.lower()}_sequential",
        [
            _CHROME_COLORS["light"],
            colors["auxiliary"],
            colors["contrast"],
            colors["neutral"],
            colors["accent"],
            colors["primary"],
        ],
        N=256,
    )
    diverging = LinearSegmentedColormap.from_list(
        f"cumcm_{normalized.lower()}_diverging",
        [colors["primary"], "#DCE4E8", _CHROME_COLORS["light"], "#E8DAD7", colors["accent"]],
        N=256,
    )
    return {
        "palette_set": normalized,
        "palette_family": PALETTE_FAMILY,
        "palette_revision": PALETTE_REVISION,
        "colors": colors,
        "tones": tones,
        "palette": palette,
        "extended_palette": extended_palette,
        "sequential": sequential,
        "diverging": diverging,
        "basis": definition["basis"],
    }

_CJK_CANDIDATES = [
    "Heiti TC",
    "Heiti SC",
    "Hiragino Sans GB",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "Microsoft YaHei",
    "PingFang SC",
    "SimHei",
    "WenQuanYi Micro Hei",
]

_CJK_FONT_FILES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]


def choose_cjk_font(candidates: Sequence[str] = _CJK_CANDIDATES) -> str:
    """Return the first installed CJK font, or Matplotlib's fallback."""
    for font_path in map(Path, _CJK_FONT_FILES):
        if not font_path.exists():
            continue
        try:
            font_manager.fontManager.addfont(font_path)
        except (OSError, RuntimeError):
            continue
    installed = {item.name for item in font_manager.fontManager.ttflist}
    return next((name for name in candidates if name in installed), "DejaVu Sans")


def apply_cumcm_style(palette_set: str, font_name: str | None = None) -> str:
    """Apply one explicitly selected paper palette without changing plotted data."""
    selected_palette = get_palette_set(palette_set)
    selected = font_name or choose_cjk_font()
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [selected, "DejaVu Sans"],
            "axes.unicode_minus": False,
            "axes.prop_cycle": mpl.cycler(color=selected_palette["palette"]),
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "legend.edgecolor": _CHROME_COLORS["grid"],
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.5,
            "lines.markersize": 4.5,
            "text.color": _CHROME_COLORS["text"],
            "axes.labelcolor": _CHROME_COLORS["text"],
            "axes.edgecolor": _CHROME_COLORS["text"],
            "xtick.color": _CHROME_COLORS["text"],
            "ytick.color": _CHROME_COLORS["text"],
            "grid.color": _CHROME_COLORS["grid"],
            "grid.linewidth": 0.6,
            "grid.alpha": 0.65,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.bbox": "tight",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    return selected


def style_axes(ax, *, grid: bool = True) -> None:
    """Apply consistent axes treatment without changing plotted data."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid:
        ax.grid(True, axis="both")
        ax.set_axisbelow(True)


def label_panels(axes: Iterable, labels: Sequence[str] | None = None) -> None:
    """Add (a), (b), ... labels to a flat or nested axes collection."""
    flat = list(getattr(axes, "flat", axes))
    panel_labels = labels or [f"({chr(97 + i)})" for i in range(len(flat))]
    if len(panel_labels) < len(flat):
        raise ValueError("not enough panel labels")
    for ax, label in zip(flat, panel_labels):
        ax.text(
            0.01,
            0.99,
            label,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontfamily="DejaVu Sans",
            fontweight="bold",
        )


def export_figure(
    fig,
    output_stem: str | Path,
    *,
    formats: Sequence[str] = ("pdf", "png"),
    dpi: int = 320,
    close: bool = True,
) -> list[Path]:
    """Export vector and raster copies from one frozen figure object."""
    stem = Path(output_stem)
    if stem.suffix:
        raise ValueError("output_stem must not include a suffix")
    stem.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for fmt in formats:
        normalized = fmt.lower().lstrip(".")
        if normalized not in {"pdf", "svg", "png"}:
            raise ValueError(f"unsupported format: {fmt}")
        path = stem.with_suffix(f".{normalized}")
        kwargs = {"bbox_inches": "tight", "facecolor": "white"}
        if normalized == "png":
            kwargs["dpi"] = dpi
        fig.savefig(path, **kwargs)
        written.append(path)
    if close:
        plt.close(fig)
    return written
