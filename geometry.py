"""
geometry.py — Motor cross-section with semi-closed stator slots.

Strategy: define one base slot on +X axis, rotate to each of the 72 positions.
No bore circle drawn — bore surface = tooth-face arcs + slot-opening arcs.
"""

import math
import femm

GEO = dict(
    R_se      = 91.4,   # stator outer radius
    R_si      = 57.5,   # stator bore (reference; no circle drawn)
    Q_s       = 72,
    # slot geometry (base slot on +X axis)
    w_open    = 2.8,    # slot opening width  (mm)
    h_neck    = 0.6,    # neck depth (mm)
    h_slot    = 18.5,   # total slot depth  (mm)
    w_bottom  = 5.444,  # slot body width at bottom (mm) — from lamination drawing
    R_bot     = 3.885,  # slot bottom arc radius (mm)  — from lamination drawing
    # rotor
    R_re      = 57.0,
    R_bar_bot = 37.6,
    R_ri      = 30.0,
    Q_r       = 28,
    w_r_top   = 5.5,
    # misc
    R_ag      = 57.25,
    R_bound   = 110.0,
)

# ── Base slot vertices (slot centred on +X axis) ──────────────────────────────
# P1/P6 : bore opening (R_si, ±w_open/2)     – Cartesian y = ±1.4 mm
# P2/P5 : neck end    (_Rn,  ±w_open/2)     – same y → rectangular neck
# P3/P4 : body bottom (_Rb,  ±w_bottom/2)   – Cartesian y = ±2.722 mm
#
# The straight walls P2→P3 and P5→P4 taper from ±1.4 mm to ±2.722 mm
# in Cartesian y, matching the lamination drawing (5.444 mm body width).
# The slot bottom is a circular arc of radius R_bot = 3.885 mm connecting
# P3 and P4, curving away from the bore (deepening the slot by ~1.1 mm).
_g  = GEO
_hw = _g['w_open'] / 2           # 1.400 mm  (half opening)
_hb = _g['w_bottom'] / 2         # 2.722 mm  (half body width at bottom)
_Rn = _g['R_si'] + _g['h_neck']  # 58.100 mm (neck-end radius)
_Rb = _g['R_si'] + _g['h_slot']  # 76.000 mm (body-end radius)

_BASE = [
    (_g['R_si'], +_hw),   # P1 – bore, CCW side
    (_Rn,        +_hw),   # P2 – neck end, CCW
    (_Rb,        +_hb),   # P3 – body bottom, CCW  (Cartesian y = +2.722)
    (_Rb,        -_hb),   # P4 – body bottom, CW   (Cartesian y = −2.722)
    (_Rn,        -_hw),   # P5 – neck end, CW
    (_g['R_si'], -_hw),   # P6 – bore, CW side
]

# Arc spans at the bore level
_HALF_DEG  = math.degrees(math.asin(_hw / _g['R_si']))   # ≈ 1.394°
_SLOT_ARC  = 2.0 * _HALF_DEG                              # ≈ 2.788° (opening)
_TOOTH_ARC = 360.0 / _g['Q_s'] - _SLOT_ARC               # ≈ 2.212° (tooth face)

# Slot-bottom arc: P4 → P3 CCW, radius R_bot = 3.885 mm
# chord = 2 × _hb = 5.444 mm → angle = 2 × arcsin(2.722/3.885) ≈ 89.0°
_BOT_ARC = 2.0 * math.degrees(math.asin(_hb / _g['R_bot']))   # ≈ 89.0°


# ── Helpers ───────────────────────────────────────────────────────────────────

def _rot(pt, theta):
    c, s = math.cos(theta), math.sin(theta)
    return (c * pt[0] - s * pt[1],
            s * pt[0] + c * pt[1])


def _slot_pts(i):
    """Return [P1..P6] for slot i after rotating by i × 5°."""
    theta = i * 2.0 * math.pi / GEO['Q_s']
    return [_rot(p, theta) for p in _BASE]


def _full_circle(R):
    femm.mi_drawarc( R, 0.0, -R, 0.0, 180.0, 1)
    femm.mi_drawarc(-R, 0.0,  R, 0.0, 180.0, 1)


# ── Drawing functions ─────────────────────────────────────────────────────────

def draw_circles():
    """Boundary + rotor circles (no bore or slot-crown circle)."""
    for R in (GEO['R_bound'], GEO['R_se'],
              GEO['R_re'], GEO['R_bar_bot'], GEO['R_ri']):
        _full_circle(R)


def draw_stator_slots():
    """72 semi-closed stator slots + tooth-face arcs."""
    Q = GEO['Q_s']
    for i in range(Q):
        P1, P2, P3, P4, P5, P6 = _slot_pts(i)

        # 5 slot walls
        femm.mi_drawline(*P1, *P2)   # right neck
        femm.mi_drawline(*P2, *P3)   # right body taper
        femm.mi_drawarc(*P4, *P3, _BOT_ARC, 5)  # slot bottom arc ≈89°, 5°/seg
        femm.mi_drawline(*P4, *P5)   # left body taper
        femm.mi_drawline(*P5, *P6)   # left neck

        # Slot opening arc: P6 → P1  (CCW, ≈2.788°)
        femm.mi_drawarc(*P6, *P1, _SLOT_ARC, 1)

        # Tooth face arc: P1_i → P6_{i+1}  (CCW, ≈2.212°)
        P6_next = _slot_pts((i + 1) % Q)[5]
        femm.mi_drawarc(*P1, *P6_next, _TOOTH_ARC, 1)


def draw_rotor_bars():
    """28 × 2 radial lines for rotor bar boundaries."""
    g = GEO
    delta = math.asin((g['w_r_top'] / 2.0) / g['R_re'])
    for n in range(g['Q_r']):
        theta_c = n * 2.0 * math.pi / g['Q_r']
        for side in (-1, +1):
            angle = theta_c + side * delta
            femm.mi_drawline(
                g['R_bar_bot'] * math.cos(angle), g['R_bar_bot'] * math.sin(angle),
                g['R_re']      * math.cos(angle), g['R_re']      * math.sin(angle),
            )


def draw_all():
    draw_circles()
    draw_stator_slots()
    draw_rotor_bars()


# ── Label position helpers ────────────────────────────────────────────────────

def _pt(R, theta_rad):
    return R * math.cos(theta_rad), R * math.sin(theta_rad)


def stator_slot_label_pos(n: int, config: int = 1, layer: int = 0):
    """Centroid inside stator slot n (0-indexed).  All configs → R≈66.75 mm."""
    theta = n * 2.0 * math.pi / GEO['Q_s']
    R_lbl = (GEO['R_si'] + GEO['R_si'] + GEO['h_slot']) / 2.0  # 66.75 mm
    return _pt(R_lbl, theta)


def rotor_bar_label_pos(n: int):
    theta = n * 2.0 * math.pi / GEO['Q_r']
    return _pt((GEO['R_bar_bot'] + GEO['R_re']) / 2.0, theta)


def rotor_iron_label_pos(n: int):
    theta = (n + 0.5) * 2.0 * math.pi / GEO['Q_r']
    return _pt((GEO['R_bar_bot'] + GEO['R_re']) / 2.0, theta)


def region_label_pos(name: str):
    g = GEO
    if name == 'outer_air':
        return _pt((g['R_se'] + g['R_bound']) / 2.0, 0.0)
    if name == 'stator_yoke':
        # In the yoke (R > slot bottom ≈76 mm), between slots 0 and 1
        theta_mid = 0.5 * 2.0 * math.pi / g['Q_s']
        return _pt((76.0 + g['R_se']) / 2.0, theta_mid)
    if name == 'airgap':
        return _pt(g['R_ag'], 0.0)
    if name == 'rotor_yoke':
        return _pt((g['R_ri'] + g['R_bar_bot']) / 2.0, 0.0)
    if name == 'shaft':
        return _pt(g['R_ri'] / 2.0, 0.0)
    raise ValueError(name)
