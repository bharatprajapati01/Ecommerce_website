#!/usr/bin/env python3
"""Generate one SVG illustration per catalog product.

Every product in store/catalog.py names an `icon`; this script draws that icon on a
tinted background and writes store/static/store/products/<product-slug>.svg, so the
picture always shows what the product name says (a "Smart Watch" is a watch, a
"Cricket Bat" is a bat, a book cover shows the book's title).

Usage (from the project root):  python tools/generate_product_images.py
"""
import math
import sys
import textwrap
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from django.utils.text import slugify  # noqa: E402

from store.catalog import all_products  # noqa: E402

OUT = ROOT / "store" / "static" / "store" / "products"
INK = "#1f2937"
STEEL = "#cbd5e1"


# ---------- colour helpers ----------

def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(h, other, t):
    a, b = _rgb(h), _rgb(other)
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def dark(h, t=0.3):
    return mix(h, "#000000", t)


def light(h, t=0.4):
    return mix(h, "#ffffff", t)


# ---------- icons (each is drawn in a 200 x 200 box) ----------

def earbuds(c, name):
    d = dark(c)

    def bud(cx, sx):
        return (
            f'<rect x="{sx}" y="72" width="11" height="34" rx="5.5" fill="#fff" stroke="#cbd5e1" stroke-width="2.5"/>'
            f'<ellipse cx="{cx}" cy="62" rx="16" ry="18" fill="#fff" stroke="#cbd5e1" stroke-width="2.5"/>'
            f'<circle cx="{cx}" cy="62" r="6" fill="{c}" opacity=".85"/>'
        )

    return (
        bud(70, 64.5) + bud(130, 124.5)
        + f'<rect x="40" y="112" width="120" height="64" rx="30" fill="{c}"/>'
        + f'<path d="M40 138 H160" stroke="{d}" stroke-width="3"/>'
        + '<circle cx="100" cy="156" r="4" fill="#fff"/>'
    )


def headphones(c, name):
    d = dark(c)
    return (
        f'<path d="M44 122 A56 62 0 0 1 156 122" fill="none" stroke="{c}" stroke-width="11" stroke-linecap="round"/>'
        f'<path d="M50 112 A50 56 0 0 1 100 66" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="3" stroke-linecap="round"/>'
        f'<rect x="28" y="106" width="40" height="66" rx="17" fill="{c}"/>'
        f'<rect x="132" y="106" width="40" height="66" rx="17" fill="{c}"/>'
        f'<rect x="56" y="116" width="14" height="46" rx="7" fill="{d}"/>'
        f'<rect x="130" y="116" width="14" height="46" rx="7" fill="{d}"/>'
    )


def speaker(c, name):
    d = dark(c)
    dots = "".join(
        f'<circle cx="{x}" cy="{y}" r="3" fill="{d}" opacity=".55"/>'
        for y in range(100, 160, 10) for x in range(70, 134, 10)
    )
    return (
        f'<rect x="55" y="40" width="90" height="126" rx="28" fill="{c}"/>'
        + dots
        + '<circle cx="100" cy="64" r="6" fill="#fff" opacity=".9"/>'
        + '<rect x="84" y="78" width="32" height="4" rx="2" fill="#fff" opacity=".6"/>'
    )


def soundbar(c, name):
    slits = "".join(
        f'<rect x="{x}" y="64" width="3" height="20" rx="1.5" fill="#475569"/>'
        for x in range(34, 142, 8)
    )
    return (
        '<rect x="14" y="54" width="172" height="44" rx="22" fill="#1f2937"/>'
        + slits
        + f'<circle cx="164" cy="76" r="5" fill="{c}"/>'
        + '<rect x="40" y="98" width="14" height="8" rx="3" fill="#475569"/>'
        + '<rect x="146" y="98" width="14" height="8" rx="3" fill="#475569"/>'
        + '<rect x="70" y="120" width="60" height="58" rx="9" fill="#334155"/>'
        + f'<circle cx="100" cy="150" r="19" fill="#111827" stroke="{c}" stroke-width="3"/>'
        + '<circle cx="100" cy="150" r="7" fill="#334155"/>'
    )


def watch(c, name):
    d = dark(c)
    return (
        f'<rect x="74" y="12" width="52" height="64" rx="12" fill="{d}"/>'
        f'<rect x="74" y="124" width="52" height="64" rx="12" fill="{d}"/>'
        + "".join(f'<circle cx="100" cy="{y}" r="2.6" fill="#fff" opacity=".4"/>' for y in (146, 158, 170))
        + '<rect x="144" y="90" width="7" height="16" rx="3" fill="#94a3b8"/>'
        + '<rect x="56" y="58" width="90" height="84" rx="26" fill="#1f2937"/>'
        + '<rect x="64" y="66" width="74" height="68" rx="20" fill="#0b1220"/>'
        + '<text x="101" y="106" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#fff">10:09</text>'
        + f'<path d="M80 122 H122" stroke="{c}" stroke-width="4" stroke-linecap="round"/>'
        + f'<path d="M82 80 H108" stroke="{c}" stroke-width="3" stroke-linecap="round" opacity=".7"/>'
    )


def band(c, name):
    return (
        f'<rect x="78" y="8" width="44" height="184" rx="20" fill="{c}"/>'
        + "".join(f'<circle cx="100" cy="{y}" r="2.6" fill="#fff" opacity=".4"/>' for y in (152, 164, 176))
        + '<rect x="82" y="46" width="36" height="84" rx="12" fill="#0b1220"/>'
        + '<text x="100" y="72" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#fff">72</text>'
        + f'<path d="M87 98 H94 L98 88 L104 110 L108 98 H113" fill="none" stroke="{light(c, .35)}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def powerbank(c, name):
    d = dark(c)
    bars = "".join(
        f'<rect x="{72 + i * 14}" y="52" width="10" height="6" rx="2" fill="{"#fff" if i < 3 else d}" opacity="{1 if i < 3 else .5}"/>'
        for i in range(4)
    )
    return (
        f'<rect x="58" y="30" width="84" height="140" rx="16" fill="{c}"/>'
        + bars
        + f'<rect x="70" y="78" width="60" height="54" rx="10" fill="{d}" opacity=".35"/>'
        + '<path d="M106 88 L90 114 H101 L95 132 L114 104 H103 Z" fill="#fff"/>'
        + '<rect x="78" y="148" width="16" height="7" rx="3.5" fill="#0f172a"/>'
        + '<rect x="106" y="148" width="16" height="7" rx="3.5" fill="#0f172a"/>'
    )


def keyboard(c, name):
    def row(y, n, x0, accent=()):
        return "".join(
            f'<rect x="{x0 + i * 13.4:.1f}" y="{y}" width="11" height="11" rx="2.5" fill="{c if i in accent else "#e5e7eb"}"/>'
            for i in range(n)
        )

    return (
        '<rect x="12" y="65" width="176" height="72" rx="12" fill="#1f2937"/>'
        + row(74, 12, 21, (0,))
        + row(88, 11, 25)
        + row(102, 11, 29, (10,))
        + '<rect x="21" y="116" width="22" height="11" rx="2.5" fill="#e5e7eb"/>'
        + f'<rect x="47" y="116" width="86" height="11" rx="2.5" fill="{light(c, .55)}"/>'
        + '<rect x="137" y="116" width="14" height="11" rx="2.5" fill="#e5e7eb"/>'
        + '<rect x="155" y="116" width="14" height="11" rx="2.5" fill="#e5e7eb"/>'
    )


def mouse(c, name):
    d = dark(c)
    return (
        f'<rect x="62" y="28" width="76" height="144" rx="38" fill="{c}"/>'
        f'<path d="M62 92 H138 M100 28 V92" stroke="{d}" stroke-width="2.5" fill="none"/>'
        '<rect x="95" y="48" width="10" height="26" rx="5" fill="#1f2937"/>'
        '<path d="M74 66 Q76 44 92 38" stroke="#fff" stroke-opacity=".45" stroke-width="4" fill="none" stroke-linecap="round"/>'
    )


def charger(c, name):
    return (
        '<rect x="56" y="36" width="88" height="98" rx="16" fill="#f8fafc" stroke="#cbd5e1" stroke-width="3"/>'
        f'<rect x="57.5" y="86" width="85" height="14" fill="{c}"/>'
        '<rect x="84" y="50" width="32" height="14" rx="7" fill="#1f2937"/>'
        '<rect x="88" y="54" width="24" height="6" rx="3" fill="#475569"/>'
        '<text x="100" y="122" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#64748b">65W</text>'
        '<rect x="76" y="134" width="9" height="30" rx="2" fill="#94a3b8"/>'
        '<rect x="115" y="134" width="9" height="30" rx="2" fill="#94a3b8"/>'
    )


def phone(c, name):
    icons = "".join(
        f'<rect x="{74 + col * 20}" y="{58 + row * 23}" width="14" height="14" rx="4" fill="#fff" opacity=".85"/>'
        for row in range(4) for col in range(3)
    )
    return (
        '<rect x="58" y="12" width="84" height="176" rx="18" fill="#1f2937"/>'
        f'<rect x="63" y="18" width="74" height="164" rx="14" fill="{c}"/>'
        '<text x="100" y="46" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#fff">10:09</text>'
        + icons
        + '<rect x="88" y="21" width="24" height="5" rx="2.5" fill="#0b1220"/>'
        + '<rect x="84" y="171" width="32" height="3.5" rx="2" fill="#fff" opacity=".8"/>'
    )


def tablet(c, name):
    return (
        '<rect x="26" y="34" width="148" height="132" rx="14" fill="#1f2937"/>'
        f'<rect x="34" y="42" width="132" height="116" rx="7" fill="{c}"/>'
        '<rect x="44" y="52" width="60" height="34" rx="6" fill="#fff" opacity=".85"/>'
        '<rect x="110" y="52" width="46" height="34" rx="6" fill="#fff" opacity=".55"/>'
        '<rect x="44" y="94" width="30" height="54" rx="6" fill="#fff" opacity=".55"/>'
        '<rect x="80" y="94" width="76" height="24" rx="6" fill="#fff" opacity=".85"/>'
        '<rect x="80" y="124" width="76" height="24" rx="6" fill="#fff" opacity=".4"/>'
        '<circle cx="30" cy="100" r="2" fill="#475569"/>'
    )


def book(c, name):
    d = dark(c, .35)
    lines = textwrap.wrap(name, 11, break_long_words=False) or [name]
    longest = max(len(x) for x in lines)
    fs = min(16.0, 76 / (0.62 * longest))
    lh = fs * 1.25
    y0 = 78 - lh * len(lines) / 2 + fs * 0.8
    text = "".join(
        f'<text x="108" y="{y0 + i * lh:.1f}" text-anchor="middle" font-family="Georgia, serif" font-weight="700" font-size="{fs:.1f}" fill="#fff">{escape(x)}</text>'
        for i, x in enumerate(lines)
    )
    return (
        '<rect x="58" y="26" width="98" height="156" rx="5" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="2"/>'
        + "".join(f'<path d="M62 {y} H154" stroke="#e2e8f0" stroke-width="1.5"/>' for y in range(170, 120, -8))
        + f'<rect x="50" y="20" width="100" height="156" rx="6" fill="{c}"/>'
        + f'<rect x="50" y="20" width="14" height="156" rx="6" fill="{d}"/>'
        + f'<rect x="58" y="20" width="6" height="156" fill="{d}"/>'
        + '<path d="M74 40 H142" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>'
        + text
        + '<path d="M74 118 H142" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>'
        + '<circle cx="108" cy="146" r="9" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="2"/>'
        + '<circle cx="108" cy="146" r="3" fill="#fff" opacity=".7"/>'
    )


def tshirt(c, name):
    d = dark(c)
    return (
        f'<path d="M62 38 L86 26 Q100 44 114 26 L138 38 L176 70 L152 98 L138 86 L138 170 L62 170 L62 86 L48 98 L24 70 Z" fill="{c}"/>'
        f'<path d="M86 26 Q100 44 114 26" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M62 160 H138" stroke="{d}" stroke-width="2" opacity=".35"/>'
        '<circle cx="120" cy="64" r="5" fill="#fff" opacity=".55"/>'
    )


def jeans(c, name):
    d = dark(c, .3)
    l = light(c, .4)
    loops = "".join(f'<rect x="{x}" y="18" width="5" height="12" rx="1.5" fill="{d}"/>' for x in (66, 84, 111, 129))
    return (
        f'<path d="M60 20 H140 L148 74 L152 184 H108 L100 90 L92 184 H48 L52 74 Z" fill="{c}"/>'
        f'<rect x="60" y="20" width="80" height="14" fill="{d}"/>'
        + loops
        + f'<path d="M100 34 V90" stroke="{d}" stroke-width="2"/>'
        + f'<path d="M66 42 Q74 70 94 64" fill="none" stroke="{l}" stroke-width="2" stroke-dasharray="4 3"/>'
        + f'<path d="M134 42 Q126 70 106 64" fill="none" stroke="{l}" stroke-width="2" stroke-dasharray="4 3"/>'
        + '<circle cx="100" cy="42" r="3.2" fill="#fbbf24"/>'
        + f'<path d="M72 160 H50 M128 160 H150" stroke="{d}" stroke-width="2" opacity=".4"/>'
    )


def shirt(c, name):
    d = dark(c, .3)
    btn = "".join(f'<circle cx="100" cy="{y}" r="2.6" fill="#fff"/>' for y in (80, 102, 124, 146))
    return (
        f'<path d="M62 36 L86 24 L100 38 L114 24 L138 36 L178 120 L156 130 L138 98 L138 172 L62 172 L62 98 L44 130 L22 120 Z" fill="{c}"/>'
        f'<path d="M86 24 L114 24 L100 58 Z" fill="{d}"/>'
        '<path d="M80 22 L102 60 L90 62 L72 38 Z" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" stroke-linejoin="round"/>'
        '<path d="M120 22 L98 60 L110 62 L128 38 Z" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" stroke-linejoin="round"/>'
        f'<path d="M100 62 V172" stroke="{d}" stroke-width="2.5"/>'
        + btn
        + f'<rect x="110" y="72" width="22" height="24" rx="2" fill="none" stroke="{d}" stroke-width="2"/>'
    )


def shorts(c, name):
    d = dark(c)
    return (
        f'<path d="M54 44 H146 L160 144 H110 L100 90 L90 144 H40 Z" fill="{c}"/>'
        f'<rect x="54" y="44" width="92" height="14" fill="{d}"/>'
        '<path d="M92 58 Q96 74 94 88 M108 58 Q104 74 106 88" stroke="#fff" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        f'<rect x="46" y="98" width="26" height="28" rx="3" fill="{d}" opacity=".4"/>'
        f'<rect x="128" y="98" width="26" height="28" rx="3" fill="{d}" opacity=".4"/>'
    )


def dress(c, name):
    d = dark(c)
    l = light(c, .6)
    pts = [(84, 104), (102, 98), (118, 108), (70, 134), (92, 128), (112, 134), (132, 128),
           (58, 162), (80, 158), (100, 152), (122, 158), (144, 160)]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="{l}"/>' for x, y in pts)
    return (
        f'<path d="M82 18 L90 18 L100 36 L110 18 L118 18 L126 70 L154 176 Q100 192 46 176 L74 70 Z" fill="{c}"/>'
        + dots
        + f'<path d="M73 68 L127 68 L125 82 L75 82 Z" fill="{d}"/>'
        + f'<path d="M90 18 L100 36 L110 18" fill="none" stroke="{d}" stroke-width="3" stroke-linejoin="round"/>'
    )


def kurti(c, name):
    d = dark(c)
    l = light(c, .6)
    return (
        f'<path d="M68 26 L88 20 L100 42 L112 20 L132 26 L170 78 L150 92 L137 76 L142 182 L112 182 L100 158 L88 182 L58 182 L63 76 L50 92 L30 78 Z" fill="{c}"/>'
        f'<path d="M88 20 L100 64 L112 20" fill="none" stroke="{d}" stroke-width="4" stroke-linejoin="round"/>'
        f'<path d="M100 66 V118" stroke="{l}" stroke-width="3" stroke-dasharray="2 5" stroke-linecap="round"/>'
        f'<path d="M60 170 H92 M108 170 H140" stroke="{l}" stroke-width="4"/>'
        + "".join(f'<circle cx="{x}" cy="160" r="3" fill="{l}"/>' for x in (68, 80, 120, 132))
    )


def leggings(c, name):
    d = dark(c)
    l = light(c, .45)
    return (
        f'<path d="M66 20 H134 L140 80 L128 186 H104 L100 84 L96 186 H72 L60 80 Z" fill="{c}"/>'
        f'<rect x="66" y="20" width="68" height="16" fill="{d}"/>'
        f'<path d="M70 40 L64 82 L76 182" fill="none" stroke="{l}" stroke-width="3" opacity=".7"/>'
        f'<path d="M130 40 L136 82 L124 182" fill="none" stroke="{l}" stroke-width="3" opacity=".7"/>'
    )


def hoodie(c, name):
    d = dark(c)
    return (
        f'<path d="M64 58 L36 80 L22 150 L48 156 L62 114 L62 174 L138 174 L138 114 L152 156 L178 150 L164 80 L136 58 Z" fill="{c}"/>'
        f'<path d="M70 60 Q68 18 100 18 Q132 18 130 60 Q100 82 70 60 Z" fill="{d}"/>'
        f'<path d="M80 58 Q100 72 120 58 Q116 34 100 32 Q84 34 80 58 Z" fill="{dark(c, .6)}"/>'
        '<path d="M92 72 L90 104 M108 72 L110 104" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M72 130 H128 L136 164 H64 Z" fill="{d}" opacity=".45"/>'
        f'<path d="M62 168 H138" stroke="{d}" stroke-width="5"/>'
    )


def jacket(c, name):
    d = dark(c)
    quilt = "".join(f'<path d="M62 {y} H138" stroke="{d}" stroke-width="2.5" opacity=".6"/>' for y in (80, 104, 128, 152))
    sl = (
        f'<path d="M32 98 L54 102 M28 124 L51 128" stroke="{d}" stroke-width="2.5" opacity=".6"/>'
        f'<path d="M168 98 L146 102 M172 124 L149 128" stroke="{d}" stroke-width="2.5" opacity=".6"/>'
    )
    return (
        f'<path d="M64 44 L34 66 L22 150 L48 156 L62 108 L62 176 L138 176 L138 108 L152 156 L178 150 L166 66 L136 44 Z" fill="{c}"/>'
        + quilt + sl
        + f'<rect x="76" y="18" width="48" height="32" rx="12" fill="{d}"/>'
        + '<path d="M100 48 V176" stroke="#fbbf24" stroke-width="3"/>'
    )


def sneaker(c, name):
    d = dark(c)
    laces = "".join(
        f'<path d="M{x} {y} l8 -10" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
        for x, y in ((76, 82), (86, 88), (96, 94))
    )
    return (
        '<path d="M18 146 H184 V156 Q184 166 174 166 H30 Q18 166 18 154 Z" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2.5"/>'
        f'<path d="M24 146 L24 100 Q24 88 36 86 L62 82 L72 60 Q82 54 90 62 L100 88 Q140 96 170 122 Q184 134 182 146 Z" fill="{c}"/>'
        f'<path d="M38 86 Q56 80 70 62 Q64 84 62 88 Z" fill="{d}"/>'
        + laces
        + '<path d="M40 132 Q92 130 134 106" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" opacity=".85"/>'
        + f'<path d="M24 146 H182" stroke="{d}" stroke-width="3" opacity=".5"/>'
    )


def sandal(c, name):
    return (
        '<path d="M100 14 Q136 14 142 52 Q146 92 132 124 Q124 186 100 188 Q76 186 70 128 Q54 92 58 52 Q64 14 100 14 Z" fill="#c8a27a" stroke="#a07850" stroke-width="3"/>'
        f'<path d="M56 62 Q100 44 146 62 L146 84 Q100 66 56 84 Z" fill="{c}"/>'
        f'<path d="M60 104 Q100 88 140 104 L138 124 Q100 108 62 124 Z" fill="{c}"/>'
        '<circle cx="100" cy="64" r="4" fill="#fbbf24"/><circle cx="100" cy="102" r="4" fill="#fbbf24"/>'
        '<path d="M86 150 Q100 158 114 150" stroke="#a07850" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"/>'
    )


def shoe(c, name):
    d = dark(c, .35)
    eyelets = "".join(f'<circle cx="{x}" cy="{y}" r="2.8" fill="#e2e8f0"/>' for x, y in ((94, 78), (104, 84), (114, 90)))
    laces = "".join(f'<path d="M{x - 8} {y + 4} L{x + 8} {y - 4}" stroke="#e2e8f0" stroke-width="2.5" stroke-linecap="round"/>' for x, y in ((94, 78), (104, 84), (114, 90)))
    return (
        '<path d="M18 148 H186 V158 Q186 168 176 168 H28 Q18 168 18 158 Z" fill="#1f2937"/>'
        '<rect x="20" y="162" width="40" height="12" rx="3" fill="#111827"/>'
        f'<path d="M24 148 L24 108 Q24 96 38 94 L74 90 Q92 72 104 66 Q124 62 130 84 Q168 96 182 128 Q188 140 186 148 Z" fill="{c}"/>'
        f'<path d="M38 94 L74 90 Q84 82 92 74" fill="none" stroke="{d}" stroke-width="3"/>'
        f'<path d="M130 86 Q160 104 176 134" fill="none" stroke="{d}" stroke-width="3"/>'
        + eyelets + laces
        + '<path d="M40 120 Q80 112 120 100" stroke="#fff" stroke-opacity=".25" stroke-width="5" fill="none" stroke-linecap="round"/>'
    )


def bottle(c, name):
    d = dark(c)
    return (
        f'<rect x="84" y="12" width="32" height="24" rx="7" fill="{d}"/>'
        '<rect x="90" y="34" width="20" height="14" fill="#cbd5e1"/>'
        f'<path d="M72 62 Q72 48 86 48 H114 Q128 48 128 62 V176 Q128 190 114 190 H86 Q72 190 72 176 Z" fill="{c}"/>'
        f'<rect x="72" y="104" width="56" height="16" fill="{d}" opacity=".55"/>'
        '<rect x="80" y="62" width="7" height="116" rx="3.5" fill="#fff" opacity=".35"/>'
    )


def _mug(x, y, col):
    d = dark(col)
    return (
        f'<path d="M{x + 62} {y + 16} Q{x + 90} {y + 16} {x + 90} {y + 42} Q{x + 90} {y + 66} {x + 58} {y + 62}" fill="none" stroke="{col}" stroke-width="9" stroke-linecap="round"/>'
        f'<rect x="{x}" y="{y}" width="62" height="76" rx="10" fill="{col}"/>'
        f'<rect x="{x}" y="{y}" width="62" height="12" rx="6" fill="{d}" opacity=".45"/>'
        f'<rect x="{x + 8}" y="{y + 18}" width="6" height="48" rx="3" fill="#fff" opacity=".35"/>'
    )


def mugs(c, name):
    return _mug(84, 50, light(c, .45)) + _mug(24, 92, c)


def flask(c, name):
    d = dark(c)
    return (
        '<path d="M134 22 Q160 22 160 46 Q160 62 138 62" fill="none" stroke="#1f2937" stroke-width="8" stroke-linecap="round"/>'
        f'<rect x="66" y="10" width="68" height="30" rx="10" fill="{d}"/>'
        f'<rect x="72" y="38" width="56" height="150" rx="16" fill="{c}"/>'
        f'<rect x="72" y="80" width="56" height="10" fill="{d}" opacity=".6"/>'
        '<rect x="72" y="170" width="56" height="18" rx="9" fill="#1f2937"/>'
        '<rect x="80" y="52" width="6" height="104" rx="3" fill="#fff" opacity=".35"/>'
    )


def lamp(c, name):
    d = dark(c)
    return (
        '<path d="M104 66 L142 84 L176 170 L96 150 Z" fill="#fde68a" opacity=".55"/>'
        '<rect x="50" y="168" width="70" height="12" rx="6" fill="#1f2937"/>'
        '<path d="M86 172 L64 104" stroke="#334155" stroke-width="7" stroke-linecap="round"/>'
        '<path d="M64 104 L120 56" stroke="#334155" stroke-width="7" stroke-linecap="round"/>'
        f'<circle cx="64" cy="104" r="7" fill="{d}"/>'
        f'<circle cx="86" cy="170" r="6" fill="{c}"/>'
        f'<path d="M110 38 L152 58 L142 82 L100 62 Z" fill="{c}"/>'
        '<path d="M114 44 L140 56" stroke="#fff" stroke-opacity=".5" stroke-width="3" stroke-linecap="round"/>'
    )


def lights(c, name):
    def f(x):
        return 64 + 22 * math.sin(x / 200 * math.pi * 2.4)

    wire = "M" + " L".join(f"{x} {f(x):.1f}" for x in range(6, 196, 4))
    cols = ["#fde047", "#fbbf24", "#fb923c", "#fde047", "#fbbf24", "#fb923c"]
    bulbs = ""
    for i, x in enumerate((24, 52, 80, 108, 136, 166)):
        y = f(x)
        col = cols[i]
        bulbs += (
            f'<path d="M{x} {y:.1f} V{y + 10:.1f}" stroke="#475569" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y + 26:.1f}" r="17" fill="{col}" opacity=".25"/>'
            f'<rect x="{x - 4}" y="{y + 8:.1f}" width="8" height="8" rx="2" fill="#475569"/>'
            f'<ellipse cx="{x}" cy="{y + 24:.1f}" rx="8" ry="10" fill="{col}"/>'
            f'<ellipse cx="{x - 2.5}" cy="{y + 21:.1f}" rx="2.2" ry="3" fill="#fff" opacity=".7"/>'
        )
    return f'<path d="{wire}" fill="none" stroke="#475569" stroke-width="3" stroke-linejoin="round"/>' + bulbs


def pan(c, name):
    return (
        f'<rect x="136" y="92" width="58" height="16" rx="8" fill="{c}"/>'
        '<circle cx="184" cy="100" r="3" fill="#fff" opacity=".8"/>'
        '<circle cx="86" cy="100" r="66" fill="#1f2937"/>'
        '<circle cx="86" cy="100" r="56" fill="#374151"/>'
        '<path d="M48 78 Q58 54 86 48" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="5" stroke-linecap="round"/>'
        '<ellipse cx="88" cy="102" rx="26" ry="22" fill="#fff"/>'
        '<circle cx="90" cy="102" r="10" fill="#fbbf24"/>'
        '<circle cx="87" cy="99" r="3" fill="#fff" opacity=".6"/>'
    )


def cooker(c, name):
    d = dark(c)
    return (
        '<rect x="14" y="100" width="28" height="12" rx="6" fill="#1f2937"/>'
        '<rect x="158" y="100" width="28" height="12" rx="6" fill="#1f2937"/>'
        '<rect x="40" y="90" width="120" height="84" rx="12" fill="#cbd5e1"/>'
        f'<rect x="40" y="124" width="120" height="12" fill="{c}"/>'
        '<path d="M34 92 Q34 52 100 52 Q166 52 166 92 Z" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>'
        f'<rect x="90" y="36" width="20" height="14" rx="4" fill="{d}"/>'
        '<rect x="97" y="24" width="6" height="14" rx="2" fill="#1f2937"/>'
        '<circle cx="128" cy="74" r="7" fill="#fff" stroke="#94a3b8" stroke-width="2"/>'
        '<path d="M128 74 L131 70" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>'
        '<rect x="52" y="98" width="8" height="68" rx="4" fill="#fff" opacity=".5"/>'
    )


def knife(c, name):
    inner = (
        '<path d="M14 112 Q20 92 50 90 L140 90 L140 116 Q60 120 14 112 Z" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>'
        '<path d="M26 108 Q60 106 136 106" stroke="#fff" stroke-opacity=".9" stroke-width="2" fill="none"/>'
        '<rect x="136" y="88" width="9" height="30" rx="2" fill="#94a3b8"/>'
        f'<rect x="144" y="90" width="44" height="26" rx="12" fill="{c}"/>'
        '<circle cx="156" cy="103" r="2.8" fill="#e2e8f0"/><circle cx="170" cy="103" r="2.8" fill="#e2e8f0"/>'
    )
    return f'<g transform="rotate(-24 100 100)">{inner}</g>'


def board(c, name):
    d = dark(c, .25)
    outline = "M54 38 H146 Q160 38 160 52 V158 Q160 172 146 172 H54 Q40 172 40 158 V52 Q40 38 54 38 Z"
    hole = "M90 54 a10 10 0 1 0 20 0 a10 10 0 1 0 -20 0 Z"
    return (
        f'<path fill-rule="evenodd" d="{outline} {hole}" fill="{c}"/>'
        f'<path d="M52 88 Q100 82 148 92 M52 114 Q100 122 148 110 M52 140 Q100 134 148 144" fill="none" stroke="{d}" stroke-width="2.5" opacity=".45"/>'
        f'<rect x="54" y="152" width="92" height="6" rx="3" fill="{d}" opacity=".4"/>'
    )


def kettle(c, name):
    d = dark(c)
    return (
        '<path d="M58 84 Q20 84 24 128 Q28 160 60 154" fill="none" stroke="#1f2937" stroke-width="10" stroke-linecap="round"/>'
        f'<path d="M140 100 L170 64 Q176 62 178 70 L172 84 L140 126 Z" fill="{c}"/>'
        f'<path d="M56 88 Q56 66 100 66 Q144 66 144 88 V164 Q144 172 136 172 H64 Q56 172 56 164 Z" fill="{c}"/>'
        f'<path d="M70 70 Q100 30 130 70 Z" fill="{d}"/>'
        '<circle cx="100" cy="42" r="7" fill="#1f2937"/>'
        '<rect x="50" y="170" width="100" height="12" rx="5" fill="#1f2937"/>'
        '<rect x="66" y="92" width="7" height="70" rx="3.5" fill="#fff" opacity=".35"/>'
        '<circle cx="100" cy="152" r="5" fill="#fff" opacity=".85"/>'
    )


def toaster(c, name):
    d = dark(c)

    def bread(x):
        return (
            f'<rect x="{x}" y="46" width="42" height="48" rx="14" fill="#f3d9a4" stroke="#c98d3f" stroke-width="3"/>'
            f'<rect x="{x + 6}" y="52" width="30" height="38" rx="10" fill="#f8e7c0"/>'
        )

    return (
        bread(54) + bread(104)
        + f'<rect x="24" y="86" width="152" height="82" rx="22" fill="{c}"/>'
        + f'<rect x="24" y="86" width="152" height="12" rx="6" fill="{d}" opacity=".6"/>'
        + '<rect x="164" y="112" width="18" height="9" rx="4.5" fill="#1f2937"/>'
        + '<circle cx="54" cy="134" r="10" fill="#1f2937"/><path d="M54 134 L60 127" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>'
        + '<rect x="40" y="168" width="16" height="8" rx="3" fill="#1f2937"/>'
        + '<rect x="144" y="168" width="16" height="8" rx="3" fill="#1f2937"/>'
    )


def mat(c, name):
    d = dark(c)
    l = light(c, .5)
    return (
        f'<rect x="36" y="64" width="128" height="72" rx="36" fill="{c}"/>'
        f'<rect x="98" y="64" width="9" height="72" fill="#1f2937"/>'
        f'<rect x="126" y="64" width="9" height="72" fill="#1f2937"/>'
        f'<circle cx="72" cy="100" r="36" fill="{l}"/>'
        f'<circle cx="72" cy="100" r="26" fill="none" stroke="{d}" stroke-width="3"/>'
        f'<circle cx="72" cy="100" r="16" fill="none" stroke="{d}" stroke-width="3"/>'
        f'<circle cx="72" cy="100" r="6" fill="{d}"/>'
    )


def dumbbell(c, name):
    def one(dy, col):
        return (
            f'<g transform="translate(0,{dy})">'
            '<rect x="58" y="94" width="84" height="12" rx="6" fill="#94a3b8"/>'
            '<rect x="76" y="92" width="48" height="16" rx="5" fill="#475569"/>'
            '<rect x="32" y="66" width="20" height="68" rx="7" fill="#1f2937"/>'
            f'<rect x="50" y="76" width="12" height="48" rx="5" fill="{col}"/>'
            '<rect x="148" y="66" width="20" height="68" rx="7" fill="#1f2937"/>'
            f'<rect x="138" y="76" width="12" height="48" rx="5" fill="{col}"/>'
            '</g>'
        )

    return (
        '<g transform="translate(100,100) scale(.78) translate(-100,-100)">'
        + one(-46, c) + one(46, mix(c, "#1f2937", .25))
        + "</g>"
    )


def football(c, name):
    def pent(cx, cy, r, rot):
        return [(cx + r * math.cos(math.radians(rot + 72 * i)), cy + r * math.sin(math.radians(rot + 72 * i))) for i in range(5)]

    def poly(pts):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    def pol(r, a):
        return 100 + r * math.cos(math.radians(a)), 100 + r * math.sin(math.radians(a))

    out = ['<clipPath id="fbclip"><circle cx="100" cy="100" r="68"/></clipPath>',
           '<circle cx="100" cy="100" r="68" fill="#fff"/>',
           '<g clip-path="url(#fbclip)">']
    for i in range(5):
        a = -90 + 72 * i
        x1, y1 = pol(22, a)
        x2, y2 = pol(48, a)
        out.append(f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{c}" stroke-width="3"/>')
        for da in (-36, 36):
            x3, y3 = pol(46, a + da)
            out.append(f'<path d="M{x2:.1f} {y2:.1f} L{x3:.1f} {y3:.1f}" stroke="{c}" stroke-width="3"/>')
        oa = a + 36
        cx, cy = pol(70, oa)
        out.append(f'<polygon points="{poly(pent(cx, cy, 24, oa + 180))}" fill="{c}"/>')
    out.append(f'<polygon points="{poly(pent(100, 100, 22, -90))}" fill="{c}"/>')
    out.append("</g>")
    out.append(f'<circle cx="100" cy="100" r="68" fill="none" stroke="{c}" stroke-width="4"/>')
    out.append('<path d="M60 56 Q76 40 100 36" stroke="#fff" stroke-opacity=".7" stroke-width="5" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def racket(c, name):
    strings = "".join(f'<path d="M{x} 18 V106" />' for x in range(70, 134, 8)) + "".join(f'<path d="M62 {y} H138" />' for y in range(20, 108, 8))
    inner = (
        '<clipPath id="rk"><ellipse cx="100" cy="62" rx="33" ry="43"/></clipPath>'
        f'<g clip-path="url(#rk)" stroke="#94a3b8" stroke-width="1.2" fill="none">{strings}</g>'
        f'<ellipse cx="100" cy="62" rx="36" ry="46" fill="none" stroke="{c}" stroke-width="7"/>'
        f'<path d="M80 100 L98 128 M120 100 L102 128" stroke="{c}" stroke-width="6" fill="none" stroke-linecap="round"/>'
        '<rect x="96.5" y="124" width="7" height="38" rx="3" fill="#94a3b8"/>'
        '<rect x="92" y="156" width="16" height="36" rx="6" fill="#1f2937"/>'
    )
    shuttle = (
        '<g transform="translate(36 140) rotate(-25)">'
        '<path d="M-9 14 L-17 -20 H17 L9 14 Z" fill="#fff" stroke="#cbd5e1" stroke-width="1.5"/>'
        '<path d="M-5 14 L-8 -20 M0 14 V-20 M5 14 L8 -20" stroke="#e2e8f0" stroke-width="1.5"/>'
        f'<path d="M-17 -20 H17" stroke="{c}" stroke-width="3"/>'
        '<circle cx="0" cy="18" r="9" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>'
        '</g>'
    )
    return f'<g transform="rotate(28 100 110)">{inner}</g>' + shuttle


def bat(c, name):
    grip_lines = "".join(f'<path d="M93 {y} H107" stroke="#fff" stroke-opacity=".5" stroke-width="2"/>' for y in range(20, 58, 6))
    inner = (
        '<rect x="94" y="14" width="12" height="74" rx="4" fill="#d4a762"/>'
        f'<rect x="93" y="12" width="14" height="48" rx="5" fill="{c}"/>'
        + grip_lines
        + '<path d="M86 84 L100 66 L114 84 Z" fill="#d4a762" stroke="#b98a4a" stroke-width="2"/>'
        + '<path d="M86 84 L114 84 L124 160 Q124 174 100 174 Q76 174 76 160 Z" fill="#e6c28b" stroke="#b98a4a" stroke-width="2.5"/>'
        + '<path d="M100 88 V172" stroke="#b98a4a" stroke-width="2" opacity=".6"/>'
        + '<path d="M90 100 V160 M110 100 V160" stroke="#b98a4a" stroke-width="1.5" opacity=".45"/>'
    )
    ball = (
        '<circle cx="152" cy="150" r="17" fill="#b91c1c"/>'
        '<path d="M141 141 Q153 150 141 160 M163 141 Q151 150 163 160" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" stroke-dasharray="3 3"/>'
    )
    return f'<g transform="rotate(20 100 100)">{inner}</g>' + ball


ICONS = {
    "earbuds": earbuds, "headphones": headphones, "speaker": speaker, "soundbar": soundbar,
    "watch": watch, "band": band, "powerbank": powerbank, "keyboard": keyboard,
    "mouse": mouse, "charger": charger, "phone": phone, "tablet": tablet,
    "book": book,
    "tshirt": tshirt, "jeans": jeans, "shirt": shirt, "shorts": shorts, "dress": dress,
    "kurti": kurti, "leggings": leggings, "hoodie": hoodie, "jacket": jacket,
    "sneaker": sneaker, "sandal": sandal, "shoe": shoe,
    "bottle": bottle, "mugs": mugs, "flask": flask, "lamp": lamp, "lights": lights,
    "pan": pan, "cooker": cooker, "knife": knife, "board": board, "kettle": kettle,
    "toaster": toaster,
    "mat": mat, "dumbbell": dumbbell, "football": football, "racket": racket, "bat": bat,
}


def build_svg(name, icon_svg, tint):
    c1, c2 = tint
    title = escape(name)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 450" role="img" aria-label="{title}">
<title>{title}</title>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>
<rect width="600" height="450" fill="url(#bg)"/>
<circle cx="300" cy="225" r="172" fill="#fff" opacity=".55"/>
<ellipse cx="300" cy="404" rx="118" ry="11" fill="#0f172a" opacity=".1"/>
<g transform="translate(120 45) scale(1.8)">{icon_svg}</g>
</svg>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for _cat, _sub, name, _desc, _price, _stock, icon, colour, tint in all_products():
        svg = build_svg(name, ICONS[icon](colour, name), tint)
        (OUT / f"{slugify(name)}.svg").write_text(svg, encoding="utf-8")
        count += 1
    print(f"Wrote {count} product images to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
