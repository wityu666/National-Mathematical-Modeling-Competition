"""Portable Matplotlib style helpers for CUMCM paper figures."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

PALETTE_SETS = {
    "SET-A": {
        "primary": "#2F6B9A",
        "contrast": "#E07A5F",
        "auxiliary": "#3D9970",
        "neutral": "#6B7280",
        "accent": "#C44E52",
        "basis": "蓝—橙—绿的色相间距较大，重点红与主蓝具有明显明度差。",
    },
    "SET-B": {
        "primary": "#6F8FAF",
        "contrast": "#C49A7A",
        "auxiliary": "#8FA68E",
        "neutral": "#8B8D8F",
        "accent": "#B77B82",
        "basis": "低饱和冷暖分离，并以线型和标记补足相近灰度层级。",
    },
    "SET-C": {
        "primary": "#4C78A8",
        "contrast": "#F2A65A",
        "auxiliary": "#72A98F",
        "neutral": "#7A7F87",
        "accent": "#B56576",
        "basis": "主蓝、赭橙和重点玫红具有较大的色相与明度跨度。",
    },
    "SET-D": {
        "primary": "#5B6C8F",
        "contrast": "#C08A65",
        "auxiliary": "#789A9F",
        "neutral": "#77757A",
        "accent": "#A46F91",
        "basis": "蓝灰、陶棕和灰紫分处不同色相区，重点色与中性灰明度可分。",
    },
}

_SERIES_ROLES = ("primary", "contrast", "auxiliary", "neutral", "accent")
_CHROME_COLORS = {
    "light": "#F5F5F2",
    "text": "#4F555A",
    "grid": "#D1D5DB",
}


def get_palette_set(palette_set: str) -> dict[str, object]:
    """Return one explicitly selected, internally consistent palette set."""
    if not palette_set or not palette_set.strip():
        raise ValueError(
            "palette_set is required; explicitly choose SET-A, SET-B, SET-C, or SET-D"
        )
    normalized = palette_set.strip().upper()
    if normalized not in PALETTE_SETS:
        choices = ", ".join(PALETTE_SETS)
        raise ValueError(f"unknown palette_set {palette_set!r}; choose one of: {choices}")

    definition = PALETTE_SETS[normalized]
    colors = {role: definition[role] for role in _SERIES_ROLES}
    palette = [colors[role] for role in _SERIES_ROLES]
    sequential = LinearSegmentedColormap.from_list(
        f"cumcm_{normalized.lower()}_sequential",
        [_CHROME_COLORS["light"], colors["auxiliary"], colors["primary"], colors["neutral"]],
        N=256,
    )
    diverging = LinearSegmentedColormap.from_list(
        f"cumcm_{normalized.lower()}_diverging",
        [colors["primary"], "#DCE4E8", _CHROME_COLORS["light"], "#E8DAD7", colors["accent"]],
        N=256,
    )
    return {
        "palette_set": normalized,
        "colors": colors,
        "palette": palette,
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
