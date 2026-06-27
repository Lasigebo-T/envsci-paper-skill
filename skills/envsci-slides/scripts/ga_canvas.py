#!/usr/bin/env python3
"""
ga_canvas.py — envsci-slides
Build a journal-spec graphical-abstract / TOC canvas and export SVG + PNG at the
right pixel/dpi. The colorblind-safe palette is embedded so this script is
standalone (no runtime dependency on envsci-figures).

Presets:
  elsevier-ga : 1328 x 531 px (w x h) @ 300 dpi   (Elsevier graphical abstract)
  est-toc     :  975 x 525 px (3.25 x 1.75 in) @ 300 dpi  (ACS ES&T TOC graphic)

Usage:
  py ga_canvas.py --preset elsevier-ga --title "..." --subtitle "..." --out ga
  py ga_canvas.py --selftest

Requires: matplotlib.
"""
from __future__ import annotations

import argparse
import os
import struct

# Okabe–Ito colorblind-safe palette, kept consistent with envsci-figures.
PALETTE = {
    "blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
    "vermillion": "#D55E00", "skyblue": "#56B4E9", "yellow": "#F0E442",
    "purple": "#CC79A7", "black": "#000000", "grey": "#999999",
}

# preset -> (width_in, height_in, dpi, label)
PRESETS = {
    "elsevier-ga": (1328 / 300, 531 / 300, 300, "Elsevier graphical abstract 1328x531 px"),
    "est-toc": (3.25, 1.75, 300, "ACS ES&T TOC 3.25x1.75 in @300 dpi"),
}


def build_canvas(preset: str, title: str = "", subtitle: str = ""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if preset not in PRESETS:
        raise ValueError(f"unknown preset {preset!r}; choose from {list(PRESETS)}")
    w_in, h_in, dpi, _ = PRESETS[preset]
    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.add_patch(plt.Rectangle((0, 0.82), 1, 0.18, color=PALETTE["blue"]))
    if title:
        ax.text(0.5, 0.91, title, ha="center", va="center",
                color="white", fontsize=11, fontweight="bold", wrap=True)
    if subtitle:
        ax.text(0.5, 0.50, subtitle, ha="center", va="center",
                color=PALETTE["black"], fontsize=8, wrap=True)
    ax.add_patch(plt.Rectangle((0.04, 0.06), 0.92, 0.70, fill=False,
                               edgecolor=PALETTE["grey"], lw=1, linestyle="--"))
    ax.text(0.5, 0.41, "[ place verified figure / schematic here ]",
            ha="center", va="center", color=PALETTE["grey"], fontsize=7)
    return fig, dpi


def export(fig, dpi, out_stem: str):
    png, svg = f"{out_stem}.png", f"{out_stem}.svg"
    fig.savefig(png, dpi=dpi)
    fig.savefig(svg)
    return png, svg


def _png_size(png_path: str):
    with open(png_path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    return struct.unpack(">II", head[16:24])


def run_selftest() -> int:
    import tempfile
    import matplotlib.pyplot as plt

    expected = {"elsevier-ga": (1328, 531), "est-toc": (975, 525)}
    failures = []
    with tempfile.TemporaryDirectory() as d:
        for preset, (ew, eh) in expected.items():
            fig, dpi = build_canvas(preset, title="Self-test", subtitle="demo")
            stem = os.path.join(d, preset)
            png, svg = export(fig, dpi, stem)
            plt.close(fig)
            assert os.path.isfile(png) and os.path.isfile(svg), preset
            w, h = _png_size(png)
            if abs(w - ew) > 2 or abs(h - eh) > 2:
                failures.append(f"{preset}: got {w}x{h}, want {ew}x{eh}")
    if failures:
        print("selftest: FAIL\n" + "\n".join(failures))
        return 1
    print("selftest: OK")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="ga_canvas.py",
        description="Build a journal-spec graphical-abstract / TOC canvas (SVG + PNG).",
    )
    p.add_argument("--preset", choices=list(PRESETS), default="elsevier-ga")
    p.add_argument("--title", default="")
    p.add_argument("--subtitle", default="")
    p.add_argument("--out", default="ga", help="output file stem (.png and .svg)")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return run_selftest()
    fig, dpi = build_canvas(args.preset, args.title, args.subtitle)
    png, svg = export(fig, dpi, args.out)
    print(f"wrote {png} and {svg} ({PRESETS[args.preset][3]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
