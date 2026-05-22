"""
geometry.py — Motor cross-section for FEMM.

Strategy: draw 7 concentric circles, then pure RADIAL LINES for slot/bar sides.
The circles automatically form arcs between the line endpoints — no manual arc
drawing per slot. This avoids the chord/angle inconsistency bug.

Regions created (all properly enclosed):
  R_bound .. R_se       : outer air (1 region)
  R_slot_crown .. R_se  : stator yoke (1 region)
  R_si .. R_slot_crown  : 72 slot wedges + 72 tooth wedges
  R_re .. R_si          : air gap (1 region)
  R_bar_bot .. R_re     : 28 bar wedges + 28 rotor-iron wedges
  R_ri .. R_bar_bot     : rotor yoke (1 region)
  0 .. R_ri             : shaft (1 region)
"""

import math
import femm

# ── Machine constants (all in mm) ─────────────────────────────────
GEO = dict(
    R_se         = 91.4,   # stator outer radius
    R_slot_crown = 76.6,   # = R_si + h_so + h_s = 57.5+0.6+18.5
    R_si         = 57.5,   # stator bore radius
    R_re         = 57.0,   # rotor outer radius
    R_bar_bot    = 37.6,   # = R_re - h_r = 57.0-19.4
    R_ri         = 30.0,   # shaft/bore inner radius
    R_ag         = 57.25,  # air gap midline (post-processing)
    R_bound      = 110.0,  # outer boundary
    Q_s          = 72,     # stator slots
    Q_r          = 28,     # rotor bars
    w_so         = 1.6,    # stator slot opening width (mm)
    w_r_top      = 5.5,    # rotor bar width at outer surface (mm)
)


def _full_circle(R):
    """Draw a complete circle of radius R as two 180-deg arcs."""
    femm.mi_drawarc( R, 0, -R, 0, 180, 1)
    femm.mi_drawarc(-R, 0,  R, 0, 180, 1)


def _radial_line(R_inner, R_outer, angle_rad):
    """Draw a radial line at angle_rad from R_inner to R_outer."""
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    femm.mi_drawline(R_inner * c, R_inner * s,
                     R_outer * c, R_outer * s)


def _slot_half_angle(R, w):
    """Half-angle (rad) subtended by width w on a circle of radius R."""
    return math.asin((w / 2.0) / R)


def draw_circles():
    """Draw all 7 boundary circles."""
    for R in (GEO['R_bound'], GEO['R_se'], GEO['R_slot_crown'],
              GEO['R_si'], GEO['R_re'], GEO['R_bar_bot'], GEO['R_ri']):
        _full_circle(R)


def draw_stator_slots():
    """Draw 72 × 2 radial lines that define stator slot/tooth boundaries."""
    g = GEO
    delta = _slot_half_angle(g['R_si'], g['w_so'])   # half-angle of slot mouth
    for n in range(g['Q_s']):
        theta_c = n * 2 * math.pi / g['Q_s']
        for side in (-1, +1):   # left and right edges
            angle = theta_c + side * delta
            _radial_line(g['R_si'], g['R_slot_crown'], angle)


def draw_rotor_bars():
    """Draw 28 × 2 radial lines that define rotor bar/iron boundaries."""
    g = GEO
    delta = _slot_half_angle(g['R_re'], g['w_r_top'])
    for n in range(g['Q_r']):
        theta_c = n * 2 * math.pi / g['Q_r']
        for side in (-1, +1):
            angle = theta_c + side * delta
            _radial_line(g['R_bar_bot'], g['R_re'], angle)


def draw_all():
    """Draw complete motor cross-section."""
    draw_circles()
    draw_stator_slots()
    draw_rotor_bars()


# ── Block-label position helpers ──────────────────────────────────

def _pt(R, theta_rad):
    return R * math.cos(theta_rad), R * math.sin(theta_rad)


def stator_slot_label_pos(n: int, config: int, layer: int):
    """Label position inside stator slot n (0-indexed).

    For config 1 (single layer): centred in slot.
    For config 2/3 (double layer): layer 0 = upper (near bore), layer 1 = lower.
    """
    g = GEO
    theta = n * 2 * math.pi / g['Q_s']
    R1 = g['R_si']
    R2 = g['R_slot_crown']
    if config == 1:
        R_lbl = (R1 + R2) / 2
    else:
        R_lbl = R1 + (R2 - R1) * (0.25 if layer == 0 else 0.75)
    return _pt(R_lbl, theta)


def stator_tooth_label_pos(n: int):
    """Label position in tooth between slots n and n+1 (0-indexed)."""
    g = GEO
    theta = (n + 0.5) * 2 * math.pi / g['Q_s']   # midpoint between slots
    R_lbl = (g['R_si'] + g['R_slot_crown']) / 2
    return _pt(R_lbl, theta)


def rotor_bar_label_pos(n: int):
    g = GEO
    theta = n * 2 * math.pi / g['Q_r']
    R_lbl = (g['R_bar_bot'] + g['R_re']) / 2
    return _pt(R_lbl, theta)


def rotor_iron_label_pos(n: int):
    """Label in rotor iron between bars n and n+1."""
    g = GEO
    theta = (n + 0.5) * 2 * math.pi / g['Q_r']
    R_lbl = (g['R_bar_bot'] + g['R_re']) / 2
    return _pt(R_lbl, theta)


def region_label_pos(name: str):
    g = GEO
    if name == 'outer_air':
        return _pt((g['R_se'] + g['R_bound']) / 2, 0)
    if name == 'stator_yoke':
        return _pt((g['R_slot_crown'] + g['R_se']) / 2, 0)
    if name == 'airgap':
        return _pt(g['R_ag'], 0)
    if name == 'rotor_yoke':
        return _pt((g['R_ri'] + g['R_bar_bot']) / 2, 0)
    if name == 'shaft':
        return _pt(g['R_ri'] / 2, 0)
    raise ValueError(name)
