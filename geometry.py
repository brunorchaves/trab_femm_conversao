"""
geometry.py — Motor cross-section with semi-closed stator and rotor slots.

Strategy: define one base slot on +X axis, rotate to each position.
No bore circle drawn — bore surface = tooth-face arcs + slot-opening arcs.
"""

import math
import femm

GEO = dict(
    R_se      = 91.4,   # stator outer radius
    R_si      = 57.5,   # stator bore (reference; no circle drawn)
    Q_s       = 72,
    # stator slot geometry
    w_open    = 2.8,    # slot opening width  (mm)
    h_neck    = 0.6,    # neck depth (mm)
    h_slot    = 18.5,   # total slot depth  (mm)
    w_bottom  = 5.444,  # slot body width at bottom (mm)
    R_bot     = 3.885,  # slot bottom arc radius (mm)
    # rotor
    R_re      = 57.0,   # rotor outer radius
    R_ri      = 21.0,   # shaft bore radius  (Ø42 H7)
    Q_r       = 52,     # rotor slots
    # misc
    R_ag      = 57.25,  # airgap mid-radius (for block label)
    R_bound   = 110.0,  # boundary circle radius
)

# ── Stator base slot vertices (slot centred on +X axis) ──────────────────────
_g  = GEO
_hw = _g['w_open'] / 2           # 1.400 mm  (half opening)
_hb = _g['w_bottom'] / 2         # 2.722 mm  (half body width at bottom)
_Rn = _g['R_si'] + _g['h_neck']  # 58.100 mm (neck-end radius)
_Rb = _g['R_si'] + _g['h_slot']  # 76.000 mm (body-end radius)

_BASE_S = [
    (_g['R_si'], +_hw),   # P1 – bore, CCW side
    (_Rn,        +_hw),   # P2 – neck end, CCW
    (_Rb,        +_hb),   # P3 – body bottom, CCW
    (_Rb,        -_hb),   # P4 – body bottom, CW
    (_Rn,        -_hw),   # P5 – neck end, CW
    (_g['R_si'], -_hw),   # P6 – bore, CW side
]

_HALF_DEG_S = math.degrees(math.asin(_hw / _g['R_si']))   # ≈ 1.394°
_SLOT_ARC_S = 2.0 * _HALF_DEG_S                            # ≈ 2.788° (opening)
_TOOTH_ARC_S = 360.0 / _g['Q_s'] - _SLOT_ARC_S            # ≈ 2.212° (tooth face)

# Slot-bottom arc: P4 → P3 CCW, radius R_bot = 3.885 mm
_BOT_ARC_S = 2.0 * math.degrees(math.asin(_hb / _g['R_bot']))  # ≈ 89.0°


# ── Rotor slot geometry (28-slot original scaled by 28/52) ───────────────────
_SCALE_R  = 28.0 / 52.0

_W_OPEN_R = 0.600 * _SCALE_R        # 0.3231 mm  (opening width)
_W_TOP_R  = 6.198 * _SCALE_R        # 3.3374 mm  (trapezoid top width)
_R_BOT_R  = 2.031 * _SCALE_R / 2.0  # 0.5468 mm  (bottom semicircle radius)
_Y_FLARE_R = 2.600 * _SCALE_R       # 1.4000 mm  (flare section depth)
_Y_BOT_R  = 22.00 * _SCALE_R        # 11.846 mm  (total slot depth)

_R_NE_R  = _g['R_re'] - _Y_FLARE_R           # 55.600 mm  (end of flare)
_R_ARC_R = _g['R_re'] - _Y_BOT_R + _R_BOT_R  # 45.701 mm  (bottom-arc centre)

# Base rotor slot vertices (local frame: x = radial outward, y = tangential)
_BASE_R = [
    (_g['R_re'], +_W_OPEN_R / 2.0),  # P1 – opening CCW
    (_R_NE_R,    +_W_TOP_R  / 2.0),  # P2 – flare end CCW
    (_R_ARC_R,   +_R_BOT_R),          # P3 – arc start CCW  (right of semicircle)
    (_R_ARC_R,   -_R_BOT_R),          # P4 – arc start CW   (left  of semicircle)
    (_R_NE_R,    -_W_TOP_R  / 2.0),  # P5 – flare end CW
    (_g['R_re'], -_W_OPEN_R / 2.0),  # P6 – opening CW
]

_HALF_DEG_R  = math.degrees(math.asin(_W_OPEN_R / 2.0 / _g['R_re']))  # ≈ 0.1623°
_OPEN_ARC_R  = 2.0 * _HALF_DEG_R                                        # ≈ 0.3246°
_PITCH_R     = 360.0 / _g['Q_r']                                        # 6.9231°
_TOOTH_ARC_R = _PITCH_R - _OPEN_ARC_R                                   # ≈ 6.5985°


# ── Helpers ───────────────────────────────────────────────────────────────────

def _rot(pt, theta):
    c, s = math.cos(theta), math.sin(theta)
    return (c * pt[0] - s * pt[1],
            s * pt[0] + c * pt[1])


def _slot_pts_s(i):
    """Stator slot i vertices after rotation."""
    theta = i * 2.0 * math.pi / GEO['Q_s']
    return [_rot(p, theta) for p in _BASE_S]


def _slot_pts_r(i):
    """Rotor slot i vertices after rotation."""
    theta = i * 2.0 * math.pi / GEO['Q_r']
    return [_rot(p, theta) for p in _BASE_R]


def _full_circle(R):
    femm.mi_drawarc( R, 0.0, -R, 0.0, 180.0, 1)
    femm.mi_drawarc(-R, 0.0,  R, 0.0, 180.0, 1)


# ── Shaft bore with keyways (Ø42 H7 + 2 × 10 H7 keyways at ±90°, R1 fillets) ─
_KW_HW    = 5.0    # keyway half-width (10 mm total)
_KW_R_OUT = 25.17  # keyway outer radius from shaft centre
_KW_RFILL = 1.0    # R1 corner fillet radius

# y_C: x-coordinate of the fillet centre (perpendicular to the radial keyway axis)
# derived from: (R_ri + r_fill)^2 = (hw + r_fill)^2 + y_C^2
_y_C  = math.sqrt((_g['R_ri'] + _KW_RFILL)**2 - (_KW_HW + _KW_RFILL)**2)
_s_kw = _g['R_ri'] / (_g['R_ri'] + _KW_RFILL)  # projection factor onto bore circle

# Tangent points where bore circle meets the fillet arcs
_tb_TR = ( _s_kw * (_KW_HW + _KW_RFILL),  _s_kw * _y_C)
_tb_TL = (-_s_kw * (_KW_HW + _KW_RFILL),  _s_kw * _y_C)
_tb_BL = (-_s_kw * (_KW_HW + _KW_RFILL), -_s_kw * _y_C)
_tb_BR = ( _s_kw * (_KW_HW + _KW_RFILL), -_s_kw * _y_C)

# Tangent points where keyway walls meet the fillet arcs
_tk_TR = ( _KW_HW,  _y_C)
_tk_TL = (-_KW_HW,  _y_C)
_tk_BL = (-_KW_HW, -_y_C)
_tk_BR = ( _KW_HW, -_y_C)

# Arc angle subtended by each fillet and each bore arc segment
_ANG_KW = math.degrees(math.atan2(_y_C, _KW_HW + _KW_RFILL))  # ≈ 74.22°


# ── Drawing functions ─────────────────────────────────────────────────────────

def draw_shaft_bore_with_keyways():
    """Ø42 H7 bore + 2 × 10 H7 keyways at ±90° with R1 fillets.

    The bore boundary is split into 3 CCW arcs separated by the keyway slots.
    Each keyway corner has a CW fillet of radius 1 mm, drawn as CCW arcs by
    reversing the endpoint order (FEMM always draws CCW given p1→p2).
    """
    R  = _g['R_ri']       # 21.0 mm
    hw = _KW_HW           # 5.0 mm
    Rk = _KW_R_OUT        # 25.17 mm
    yC = _y_C             # ≈ 21.166 mm
    a  = _ANG_KW          # ≈ 74.22°

    # ── Bore arc 1: (R,0) → tb_TR  (74.22° CCW)
    femm.mi_drawarc(R, 0.0, *_tb_TR, a, 1)

    # ── Keyway +Y (at 90°): CW fillets drawn as CCW by swapping end-points
    femm.mi_drawarc(*_tk_TR, *_tb_TR, a, 1)   # fillet TR: CCW tk→tb ≡ CW bore→kw
    femm.mi_drawline( hw,  yC,  hw, Rk)
    femm.mi_drawline( hw, Rk,  -hw, Rk)
    femm.mi_drawline(-hw, Rk,  -hw, yC)
    femm.mi_drawarc(*_tb_TL, *_tk_TL, a, 1)   # fillet TL: CCW tb→tk ≡ CW kw→bore

    # ── Bore arc 2: tb_TL → tb_BL  (148.44° CCW, crosses 180°)
    femm.mi_drawarc(*_tb_TL, *_tb_BL, 2.0 * a, 1)

    # ── Keyway -Y (at 270°)
    femm.mi_drawarc(*_tk_BL, *_tb_BL, a, 1)   # fillet BL: CCW tk→tb ≡ CW bore→kw
    femm.mi_drawline(-hw, -yC, -hw, -Rk)
    femm.mi_drawline(-hw, -Rk,  hw, -Rk)
    femm.mi_drawline( hw, -Rk,  hw, -yC)
    femm.mi_drawarc(*_tb_BR, *_tk_BR, a, 1)   # fillet BR: CCW tb→tk ≡ CW kw→bore

    # ── Bore arc 3: tb_BR → (R,0)  (74.22° CCW)
    femm.mi_drawarc(*_tb_BR, R, 0.0, a, 1)


def draw_circles():
    """Boundary and stator outer circles; shaft bore drawn with keyways."""
    for R in (GEO['R_bound'], GEO['R_se']):
        _full_circle(R)
    draw_shaft_bore_with_keyways()


def draw_stator_slots():
    """72 semi-closed stator slots + tooth-face arcs."""
    Q = GEO['Q_s']
    for i in range(Q):
        P1, P2, P3, P4, P5, P6 = _slot_pts_s(i)

        femm.mi_drawline(*P1, *P2)   # right neck
        femm.mi_drawline(*P2, *P3)   # right body taper
        femm.mi_drawarc(*P4, *P3, _BOT_ARC_S, 5)  # slot bottom arc (CCW)
        femm.mi_drawline(*P4, *P5)   # left body taper
        femm.mi_drawline(*P5, *P6)   # left neck

        # Opening arc P6 → P1 (CCW, ≈ 2.788°)
        femm.mi_drawarc(*P6, *P1, _SLOT_ARC_S, 1)

        # Tooth face arc P1_i → P6_{i+1} (CCW, ≈ 2.212°)
        P6_next = _slot_pts_s((i + 1) % Q)[5]
        femm.mi_drawarc(*P1, *P6_next, _TOOTH_ARC_S, 1)


def draw_rotor_bars():
    """52 semi-closed rotor slots: trapezoidal with semicircle bottom.

    Each slot has:
      P1/P6  – opening at R_re (57.0 mm), half-width 0.162 mm
      P2/P5  – end of flare at R_ne (55.6 mm), half-width 1.669 mm
      P3/P4  – ends of bottom semicircle of radius 0.547 mm
    """
    Q = GEO['Q_r']
    for i in range(Q):
        P1, P2, P3, P4, P5, P6 = _slot_pts_r(i)

        femm.mi_drawline(*P1, *P2)             # right flare wall
        femm.mi_drawline(*P2, *P3)             # right trapezoid wall
        femm.mi_drawarc(*P3, *P4, 180.0, 5)   # bottom semicircle (CCW, inward)
        femm.mi_drawline(*P4, *P5)             # left trapezoid wall
        femm.mi_drawline(*P5, *P6)             # left flare wall

        # Opening arc P6 → P1 (CCW, ≈ 0.325°)
        femm.mi_drawarc(*P6, *P1, _OPEN_ARC_R, 1)

        # Tooth face arc P1_i → P6_{i+1} (CCW, ≈ 6.598°)
        P6_next = _rot(_BASE_R[5], (i + 1) * 2.0 * math.pi / Q)
        femm.mi_drawarc(*P1, *P6_next, _TOOTH_ARC_R, 1)


def draw_all():
    draw_circles()
    draw_stator_slots()
    draw_rotor_bars()


# ── Label position helpers ────────────────────────────────────────────────────

def _pt(R, theta_rad):
    return R * math.cos(theta_rad), R * math.sin(theta_rad)


def stator_slot_label_pos(n: int, config: int = 1, layer: int = 0):
    """Centroid inside stator slot n (0-indexed). R ≈ 66.75 mm."""
    theta = n * 2.0 * math.pi / GEO['Q_s']
    R_lbl = (GEO['R_si'] + GEO['R_si'] + GEO['h_slot']) / 2.0  # 66.75 mm
    return _pt(R_lbl, theta)


def rotor_bar_label_pos(n: int):
    """Centroid inside rotor bar n (0-indexed). Mid-depth of trapezoid."""
    theta = n * 2.0 * math.pi / GEO['Q_r']
    r_mid = (_R_NE_R + _R_ARC_R) / 2.0   # ≈ 50.65 mm
    return _pt(r_mid, theta)


def rotor_iron_label_pos(n: int):
    """Iron region between rotor bars (deep inner yoke)."""
    theta = (n + 0.5) * 2.0 * math.pi / GEO['Q_r']
    return _pt(35.0, theta)


def region_label_pos(name: str):
    g = GEO
    if name == 'outer_air':
        return _pt((g['R_se'] + g['R_bound']) / 2.0, 0.0)
    if name == 'stator_yoke':
        theta_mid = 0.5 * 2.0 * math.pi / g['Q_s']
        return _pt((76.0 + g['R_se']) / 2.0, theta_mid)
    if name == 'airgap':
        return _pt(g['R_ag'], 0.0)
    if name == 'rotor_yoke':
        # Deep in inner yoke (below slot bottoms at ≈45.15 mm), between slots 0 and 1
        theta_mid = 0.5 * 2.0 * math.pi / g['Q_r']
        return _pt(35.0, theta_mid)
    if name == 'shaft':
        return _pt(g['R_ri'] / 2.0, 0.0)
    raise ValueError(name)
