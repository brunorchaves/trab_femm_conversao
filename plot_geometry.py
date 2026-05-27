"""
plot_geometry.py — Cross-section plots of stator (Q_s=72) and rotor (Q_r=52).
Geometry matches geometry.py exactly (updated rotor: trapezoidal semi-closed slots).
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

rcParams['font.family'] = 'DejaVu Sans'

# ── Palette ───────────────────────────────────────────────────────────────────
IRON  = '#cdc9be'
CU    = '#b84020'
ALU   = '#4a9fd4'
AIR   = '#e8eaf0'
SHAFT = '#8a8a9a'
EDG   = '#333333'
BG    = 'white'

# ── Machine parameters ────────────────────────────────────────────────────────
R_se      = 91.4
R_si      = 57.5
Q_s       = 72
w_open    = 2.8
h_neck    = 0.6
h_slot    = 18.5
w_bottom  = 5.444
R_bot_arc = 3.885

_hw = w_open / 2
_hb = w_bottom / 2
_Rn = R_si + h_neck
_Rb = R_si + h_slot   # 76.0 mm

BASE_S = [
    (R_si, +_hw), (_Rn, +_hw), (_Rb, +_hb),
    (_Rb,  -_hb), (_Rn, -_hw), (R_si, -_hw),
]

# ── Rotor parameters (Q_r=52, trapezoidal semi-closed, scaled 28/52) ──────────
R_re   = 57.0
R_ri   = 21.0      # shaft bore Ø42 H7
Q_r    = 52

# Shaft keyway geometry (Ø42 H7 + 2 × 10 H7 keyways @ 180°)
_KW_HW      = 5.00    # half-width of keyway (10 mm total)
_KW_R_OUTER = 25.17   # radial extent of keyway (50.34/2 mm)
_KW_FILLET  = 1.00    # corner fillet radius R1

_SCALE = 28.0 / 52.0
_W_OPEN_R = 0.600 * _SCALE      # 0.3231 mm
_W_TOP_R  = 6.198 * _SCALE      # 3.3374 mm
_R_BOT_R  = 2.031 * _SCALE / 2  # 0.5468 mm  (bottom semicircle radius)
_Y_FLARE  = 2.600 * _SCALE      # 1.4000 mm  (flare depth)
_Y_BOT    = 22.00 * _SCALE      # 11.846 mm  (total slot depth)
_R_NE     = R_re - _Y_FLARE     # 55.600 mm  (end of flare)
_R_ARC    = R_re - _Y_BOT + _R_BOT_R  # 45.701 mm (arc centre)

BASE_R = [
    (R_re,  +_W_OPEN_R / 2),   # P1 – opening CCW
    (_R_NE, +_W_TOP_R  / 2),   # P2 – flare end CCW
    (_R_ARC, +_R_BOT_R),        # P3 – arc start (right)
    (_R_ARC, -_R_BOT_R),        # P4 – arc end   (left)
    (_R_NE, -_W_TOP_R  / 2),   # P5 – flare end CW
    (R_re,  -_W_OPEN_R / 2),   # P6 – opening CW
]

_HALF_DEG_R  = np.degrees(np.arcsin(_W_OPEN_R / 2 / R_re))
_OPEN_ARC_R  = 2.0 * _HALF_DEG_R          # ≈ 0.325°
_PITCH_R     = 360.0 / Q_r                # 6.923°
_TOOTH_ARC_R = _PITCH_R - _OPEN_ARC_R     # ≈ 6.598°


# ── Geometry helpers ──────────────────────────────────────────────────────────

def rot_pts(pts, theta):
    c, s = np.cos(theta), np.sin(theta)
    return [(c * x - s * y, s * x + c * y) for x, y in pts]


def arc_pts(R, a1, a2, n=80):
    """CCW arc of circle R from angle a1 to a2."""
    if a2 < a1:
        a2 += 2 * np.pi
    t = np.linspace(a1, a2, n)
    return R * np.cos(t), R * np.sin(t)


def rounded_bottom_s(P3, P4, R_arc, n=50):
    """Stator slot bottom arc: bulges outward (toward yoke)."""
    mx, my = (P3[0] + P4[0]) / 2, (P3[1] + P4[1]) / 2
    hc = np.hypot(P3[0] - mx, P3[1] - my)
    d  = np.sqrt(max(R_arc**2 - hc**2, 0.0))
    rm = np.hypot(mx, my)
    cx, cy = mx - d * mx / rm, my - d * my / rm
    a3 = np.arctan2(P3[1] - cy, P3[0] - cx)
    a4 = np.arctan2(P4[1] - cy, P4[0] - cx)
    if a4 > a3:
        a4 -= 2 * np.pi
    t = np.linspace(a3, a4, n)
    return cx + R_arc * np.cos(t), cy + R_arc * np.sin(t)


def stator_slot_poly(i, n_arc=30):
    """Polygon (conductor region) for stator slot i."""
    pts = rot_pts(BASE_S, i * 2 * np.pi / Q_s)
    P1, P2, P3, P4, P5, P6 = pts
    ax_x, ax_y = arc_pts(R_si, np.arctan2(P6[1], P6[0]),
                                np.arctan2(P1[1], P1[0]), n_arc)
    bx, by = rounded_bottom_s(P3, P4, R_bot_arc, n_arc)
    px = np.concatenate([ax_x, [P2[0], P3[0]], bx, [P5[0], P6[0]]])
    py = np.concatenate([ax_y, [P2[1], P3[1]], by, [P5[1], P6[1]]])
    return px, py


def rotor_bar_poly(n, n_arc=80):
    """Polygon (aluminium bar) for rotor slot n — trapezoidal with semicircle bottom."""
    theta = n * 2 * np.pi / Q_r
    pts = rot_pts(BASE_R, theta)
    P1, P2, P3, P4, P5, P6 = pts

    # Bottom semicircle P3→P4 (CCW, going inward)
    cx = (P3[0] + P4[0]) / 2
    cy = (P3[1] + P4[1]) / 2
    r_b = np.hypot(P3[0] - cx, P3[1] - cy)
    a3  = np.arctan2(P3[1] - cy, P3[0] - cx)
    t_bot = np.linspace(a3, a3 + np.pi, n_arc)
    bx = cx + r_b * np.cos(t_bot)
    by = cy + r_b * np.sin(t_bot)

    # Opening arc P6→P1 (CCW, tiny arc at R_re)
    a6 = np.arctan2(P6[1], P6[0])
    a1 = np.arctan2(P1[1], P1[0])
    if a1 < a6:
        a1 += 2 * np.pi
    t_op = np.linspace(a6, a1, max(4, n_arc // 20))
    ox = R_re * np.cos(t_op)
    oy = R_re * np.sin(t_op)

    # Polygon: opening arc → right walls → bottom arc → left walls (closed)
    xs = np.concatenate([ox, [P1[0], P2[0], P3[0]], bx, [P5[0], P6[0]]])
    ys = np.concatenate([oy, [P1[1], P2[1], P3[1]], by, [P5[1], P6[1]]])
    return xs, ys


def shaft_hole_with_keyways(n_arc=240, n_fillet=20):
    """CCW polygon of the shaft bore + 2 keyways @ 0° and 180°, with R1 fillets."""
    R_bore = R_ri
    hw     = _KW_HW
    R_kw   = _KW_R_OUTER
    r_fill = _KW_FILLET
    y_C = np.sqrt((R_bore + r_fill) ** 2 - (hw + r_fill) ** 2)
    s   = R_bore / (R_bore + r_fill)

    tb_TR = ( s * (hw + r_fill),  s * y_C)
    tb_TL = (-s * (hw + r_fill),  s * y_C)
    tb_BR = ( s * (hw + r_fill), -s * y_C)
    tb_BL = (-s * (hw + r_fill), -s * y_C)
    tk_TR = ( hw,  y_C);  tk_TL = (-hw,  y_C)
    tk_BR = ( hw, -y_C);  tk_BL = (-hw, -y_C)
    C_TR  = ( hw + r_fill,  y_C);  C_TL = (-(hw + r_fill),  y_C)
    C_BR  = ( hw + r_fill, -y_C);  C_BL = (-(hw + r_fill), -y_C)

    ang_TR = np.arctan2(tb_TR[1], tb_TR[0])
    ang_TL = np.arctan2(tb_TL[1], tb_TL[0])
    ang_BR = np.arctan2(tb_BR[1], tb_BR[0])
    ang_BL = np.arctan2(tb_BL[1], tb_BL[0])

    def fillet(C, p0, p1, r, n):
        a0 = np.arctan2(p0[1] - C[1], p0[0] - C[0])
        a1 = np.arctan2(p1[1] - C[1], p1[0] - C[0])
        if a0 < a1:
            a0 += 2 * np.pi   # CW direction
        return [(C[0] + r * np.cos(t), C[1] + r * np.sin(t))
                for t in np.linspace(a0, a1, n)]

    pts = []
    for t in np.linspace(0, ang_TR, n_arc // 4):
        pts.append((R_bore * np.cos(t), R_bore * np.sin(t)))
    pts += fillet(C_TR, tb_TR, tk_TR, r_fill, n_fillet)
    pts.append(( hw,  R_kw)); pts.append((-hw,  R_kw))
    pts += fillet(C_TL, tk_TL, tb_TL, r_fill, n_fillet)
    ang_BL_ccw = ang_BL + 2 * np.pi if ang_BL < ang_TL else ang_BL
    for t in np.linspace(ang_TL, ang_BL_ccw, n_arc // 2):
        pts.append((R_bore * np.cos(t), R_bore * np.sin(t)))
    pts += fillet(C_BL, tb_BL, tk_BL, r_fill, n_fillet)
    pts.append((-hw, -R_kw)); pts.append(( hw, -R_kw))
    pts += fillet(C_BR, tk_BR, tb_BR, r_fill, n_fillet)
    for t in np.linspace(ang_BR, 0, n_arc // 4):
        pts.append((R_bore * np.cos(t), R_bore * np.sin(t)))
    return pts


# ── Annotation helper ─────────────────────────────────────────────────────────

def dim(ax, x1, y1, x2, y2, label, lcolor='#222', fsize=8.5,
        tx=None, ty=None, rot=0):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='<->', color=lcolor, lw=0.9,
                                mutation_scale=8))
    if tx is None:
        tx = (x1 + x2) / 2
    if ty is None:
        ty = (y1 + y2) / 2
    ax.text(tx, ty, label, fontsize=fsize, color=lcolor, ha='center',
            va='center', rotation=rot,
            bbox=dict(fc='white', ec='none', alpha=0.7, pad=1))


# ══════════════════════════════════════════════════════════════════════════════
#  STATOR FIGURE
# ══════════════════════════════════════════════════════════════════════════════

fig_s, axes_s = plt.subplots(1, 2, figsize=(14, 7.2), facecolor=BG)
fig_s.subplots_adjust(left=0.01, right=0.99, bottom=0.07, top=0.91, wspace=0.04)

# ── LEFT: full stator ─────────────────────────────────────────────────────────
ax = axes_s[0]
ax.set_aspect('equal'); ax.set_facecolor(BG); ax.axis('off')

ax.add_patch(plt.Circle((0, 0), R_se, fc=IRON, ec=EDG, lw=1.1, zorder=1))
ax.add_patch(plt.Circle((0, 0), R_si, fc=AIR,  ec=EDG, lw=0.7, ls='--', zorder=2))

for i in range(Q_s):
    px, py = stator_slot_poly(i, n_arc=10)
    ax.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                              fc=CU, ec=EDG, lw=0.25, alpha=0.90, zorder=3))

for i in [0, 18, 36, 54]:
    theta_c = i * 2 * np.pi / Q_s
    r_lbl = (_Rb + R_si) / 2
    ax.text(r_lbl * np.cos(theta_c), r_lbl * np.sin(theta_c),
            str(i + 1), fontsize=6, color='white', ha='center', va='center',
            fontweight='bold', zorder=5)

dim(ax, -R_se, -R_se - 8, R_se, -R_se - 8,
    f'Ø {2*R_se:.0f} mm  ($R_{{se}}$ = {R_se} mm)', ty=-R_se - 12, fsize=9)
ax.text(-R_si * 0.68, R_si * 0.68, f'$R_{{si}}$ = {R_si} mm',
        fontsize=8, color='#0055aa', ha='right',
        bbox=dict(fc='white', ec='none', alpha=0.8))

ax.set_xlim(-R_se - 16, R_se + 16)
ax.set_ylim(-R_se - 20, R_se + 18)
ax.set_title(f'Seção transversal completa  —  $Q_s$ = {Q_s} ranhuras',
             fontsize=12, color='#111', pad=5)

# ── RIGHT: 4-slot detail ──────────────────────────────────────────────────────
ax = axes_s[1]
ax.set_aspect('equal'); ax.set_facecolor(BG); ax.axis('off')

DS    = [0, 1, 2, 3]
a_lo  = (DS[0]  - 0.85) * 2 * np.pi / Q_s
a_hi  = (DS[-1] + 1.85) * 2 * np.pi / Q_s
t_out = np.linspace(a_lo, a_hi, 300)

iron_x = np.concatenate([R_se * np.cos(t_out), R_si * np.cos(t_out[::-1])])
iron_y = np.concatenate([R_se * np.sin(t_out), R_si * np.sin(t_out[::-1])])
ax.fill(iron_x, iron_y, color=IRON, zorder=1)
ax.fill(np.append(R_si * np.cos(t_out), 0),
        np.append(R_si * np.sin(t_out), 0),
        color=AIR, alpha=0.6, zorder=0)

for R, lc, ls, lw in [(R_se, EDG, '-', 1.2), (R_si, '#0055aa', '--', 0.9),
                       (_Rn, '#228822', ':', 0.8), (_Rb, '#cc3300', ':', 0.8)]:
    ax.plot(R * np.cos(t_out), R * np.sin(t_out), color=lc, ls=ls, lw=lw, zorder=5)

slot_colors = [CU, '#3a7ec8', '#2aaa55', '#c8a020']
for k, i in enumerate(DS):
    px, py = stator_slot_poly(i, n_arc=60)
    ax.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                              fc=slot_colors[k], ec=EDG, lw=0.7, alpha=0.85, zorder=3))
    theta_c = i * 2 * np.pi / Q_s
    r_lbl   = (_Rb + R_si) / 2
    ax.text(r_lbl * np.cos(theta_c), r_lbl * np.sin(theta_c),
            str(i + 1), fontsize=8, color='white', ha='center', va='center',
            fontweight='bold', zorder=6)

P1, P2, P3, P4, P5, P6 = rot_pts(BASE_S, 0.0)
dim(ax, R_si + 0.8, -_hw, R_si + 0.8, +_hw,
    f'$w_o$ = {w_open} mm', lcolor='#0055aa', fsize=7.5, tx=R_si + 3.2, ty=0, rot=90)
dim(ax, R_si, _hw + 1.4, _Rn, _hw + 1.4,
    f'$h_n$ = {h_neck}', lcolor='#228822', fsize=7.5, tx=(R_si + _Rn) / 2, ty=_hw + 2.5)
dim(ax, _Rb - 1.0, -_hb, _Rb - 1.0, +_hb,
    f'$w_b$ = {w_bottom} mm', lcolor='#cc3300', fsize=7.5, tx=_Rb - 3.8, ty=0, rot=90)
dim(ax, R_si, -1.0, _Rb, -1.0,
    f'$h_s$ = {h_slot} mm', lcolor='#222', fsize=7.5, tx=(R_si + _Rb) / 2, ty=-2.4)
ax.text(_Rb + 1.3, 1.8, f'$R_{{bot}}$ = {R_bot_arc} mm', fontsize=7, color='#666', ha='left')
ax.text(70, 13, f'Passo = {360.0/Q_s:.2f}°/ranhura', fontsize=7.5, color='#444',
        ha='center', bbox=dict(fc='white', ec='#aaa', alpha=0.85, pad=2))

xs_d = [p[0] for i in DS for p in rot_pts(BASE_S, i * 2 * np.pi / Q_s)]
ys_d = [p[1] for i in DS for p in rot_pts(BASE_S, i * 2 * np.pi / Q_s)]
mg = 5
ax.set_xlim(min(xs_d) - mg, R_se + mg + 6)
ax.set_ylim(min(ys_d) - mg - 1, max(ys_d) + mg + 4)
ax.set_title('Detalhe — 4 ranhuras (slots 1–4)  |  escala ampliada',
             fontsize=12, color='#111', pad=5)

leg_s = [mpatches.Patch(fc=IRON, ec=EDG, label='Ferro (M250-50A)'),
         mpatches.Patch(fc=CU,   ec=EDG, label='Cobre (condutor)'),
         mpatches.Patch(fc=AIR,  ec=EDG, label='Entreferro / Ar')]
ax.legend(handles=leg_s, loc='lower right', fontsize=8, framealpha=0.9)

fig_s.suptitle(
    f'Geometria do Estator  |  $Q_s$ = {Q_s}  |  $g$ = 0,5 mm  |  M250-50A',
    fontsize=12, color='#111', y=0.975)

out_s = '/home/ribb/Área de trabalho/ufmg/trab_femm/stator_geometry_new.png'
fig_s.savefig(out_s, dpi=160, bbox_inches='tight', facecolor=BG)
print(f'Salvo: {out_s}')


# ══════════════════════════════════════════════════════════════════════════════
#  ROTOR FIGURE
# ══════════════════════════════════════════════════════════════════════════════

fig_r, axes_r = plt.subplots(1, 2, figsize=(14, 7.2), facecolor=BG)
fig_r.subplots_adjust(left=0.01, right=0.99, bottom=0.07, top=0.91, wspace=0.04)


# ── LEFT: full rotor cross-section ───────────────────────────────────────────
ax = axes_r[0]
ax.set_aspect('equal'); ax.set_facecolor(BG); ax.axis('off')

# Rotor iron disc
ax.add_patch(plt.Circle((0, 0), R_re, fc=IRON, ec=EDG, lw=1.1, zorder=1))
# Shaft with keyways (SHAFT-colored polygon: bore Ø42 + 2 × 10 keyways)
_shaft_pts = shaft_hole_with_keyways()
ax.add_patch(plt.Polygon(_shaft_pts, closed=True, fc=SHAFT, ec=EDG, lw=0.8, zorder=4))

# 52 bars
for n in range(Q_r):
    px, py = rotor_bar_poly(n, n_arc=40)
    ax.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                              fc=ALU, ec='#1a5580', lw=0.4, alpha=0.95, zorder=2))

# Bar index labels at 4 cardinal positions
for n in [0, Q_r // 4, Q_r // 2, 3 * Q_r // 4]:
    theta_c = n * 2 * np.pi / Q_r
    r_lbl = (_R_NE + _R_ARC) / 2
    ax.text(r_lbl * np.cos(theta_c), r_lbl * np.sin(theta_c),
            str(n + 1), fontsize=6, color='white', ha='center', va='center',
            fontweight='bold', zorder=5)

dim(ax, -R_re, -R_re - 8, R_re, -R_re - 8,
    f'Ø {2*R_re:.0f} mm  ($R_{{re}}$ = {R_re} mm)', ty=-R_re - 12, fsize=9)
dim(ax, -R_ri, R_ri + 5, R_ri, R_ri + 5,
    f'Ø {2*R_ri:.0f} mm  (eixo Ø42 H7)', ty=R_ri + 9, fsize=9)

ax.set_xlim(-R_re - 16, R_re + 16)
ax.set_ylim(-R_re - 20, R_re + 16)
ax.set_title(f'Seção transversal completa  —  $Q_r$ = {Q_r} barras',
             fontsize=12, color='#111', pad=5)


# ── RIGHT: 4-bar detail (bars 1–4 near +X axis) ──────────────────────────────
ax = axes_r[1]
ax.set_aspect('equal'); ax.set_facecolor(BG); ax.axis('off')

DB    = [0, 1, 2, 3]
_dh_r = np.radians(_HALF_DEG_R)
a_lo_r = (DB[0]  - 0.9) * 2 * np.pi / Q_r
a_hi_r = (DB[-1] + 0.9) * 2 * np.pi / Q_r
t_arc  = np.linspace(a_lo_r, a_hi_r, 300)

# Iron wedge from shaft to R_re
ring_x = np.concatenate([R_re * np.cos(t_arc), R_ri * np.cos(t_arc[::-1])])
ring_y = np.concatenate([R_re * np.sin(t_arc), R_ri * np.sin(t_arc[::-1])])
ax.fill(ring_x, ring_y, color=IRON, zorder=1)

# Reference arcs
for R, lc, ls, lw in [
    (R_re,  EDG,       '-',  1.2),
    (_R_NE, '#228822', ':',  0.8),
    (_R_ARC,'#cc3300', ':',  0.7),
    (R_ri,  SHAFT,     '-',  1.0),
]:
    ax.plot(R * np.cos(t_arc), R * np.sin(t_arc), color=lc, ls=ls, lw=lw, zorder=5)

# 4 bars (different blues)
bar_colors = [ALU, '#2a9fd0', '#1a8fc0', '#0a7fb0']
for k, n in enumerate(DB):
    px, py = rotor_bar_poly(n, n_arc=120)
    ax.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                              fc=bar_colors[k % len(bar_colors)],
                              ec='#1a5580', lw=0.9, alpha=0.95, zorder=3))
    theta_c = n * 2 * np.pi / Q_r
    r_lbl   = (_R_NE + _R_ARC) / 2
    ax.text(r_lbl * np.cos(theta_c), r_lbl * np.sin(theta_c),
            str(n + 1), fontsize=9, color='white', ha='center', va='center',
            fontweight='bold', zorder=6)

# ── Dimensions on bar 0 (on +X axis) ────────────────────────────────────────
# Opening width at R_re
dim(ax, R_re + 2.0, -_W_OPEN_R/2, R_re + 2.0, +_W_OPEN_R/2,
    f'$w_o$ = {_W_OPEN_R:.3f} mm', lcolor='#0055aa', fsize=7.5,
    tx=R_re + 4.5, ty=0, rot=90)

# Trapezoid width at R_NE
dim(ax, _R_NE - 0.8, -_W_TOP_R/2, _R_NE - 0.8, +_W_TOP_R/2,
    f'$w_{{top}}$ = {_W_TOP_R:.3f} mm', lcolor='#228822', fsize=7.5,
    tx=_R_NE - 3.8, ty=0, rot=90)

# Total slot depth
h_slot_r = R_re - (_R_ARC - _R_BOT_R)   # R_re - R_deepest
off_t = np.radians(-3.5)
dim(ax,
    (_R_ARC - _R_BOT_R) * np.cos(off_t), (_R_ARC - _R_BOT_R) * np.sin(off_t),
    R_re  * np.cos(off_t), R_re  * np.sin(off_t),
    f'$h_r$ = {h_slot_r:.2f} mm', lcolor='#222', fsize=7.5,
    tx=((R_re + _R_ARC - _R_BOT_R) / 2) * np.cos(off_t) - 3.0,
    ty=((R_re + _R_ARC - _R_BOT_R) / 2) * np.sin(off_t), rot=90)

# r_bot (semicircle radius)
ax.text(_R_ARC - _R_BOT_R - 1.0, 1.0,
        f'$r_{{bot}}$ = {_R_BOT_R:.3f} mm', fontsize=7, color='#cc3300', ha='right')

# Angular pitch
r_ann  = R_re + 9
arc_t2 = np.linspace(_dh_r * 0.7, 2 * np.pi / Q_r - _dh_r * 0.7, 40)
ax.plot(r_ann * np.cos(arc_t2), r_ann * np.sin(arc_t2), 'k-', lw=0.9, alpha=0.6)
ax.annotate('', xy=(r_ann * np.cos(arc_t2[-1]), r_ann * np.sin(arc_t2[-1])),
            xytext=(r_ann * np.cos(arc_t2[-2]), r_ann * np.sin(arc_t2[-2])),
            arrowprops=dict(arrowstyle='->', color='#333', lw=0.8))
ax.annotate('', xy=(r_ann * np.cos(arc_t2[0]),  r_ann * np.sin(arc_t2[0])),
            xytext=(r_ann * np.cos(arc_t2[1]),  r_ann * np.sin(arc_t2[1])),
            arrowprops=dict(arrowstyle='->', color='#333', lw=0.8))
t_mid  = (arc_t2[0] + arc_t2[-1]) / 2
ax.text(r_ann * np.cos(t_mid), r_ann * np.sin(t_mid) + 3.5,
        f'{_PITCH_R:.2f}°\n(passo)', fontsize=7.5, color='#333', ha='center')

# Circle labels
for R, lc, txt, frac in [
    (R_re,  EDG,       f'$R_{{re}}$ = {R_re} mm', 0.82),
    (_R_NE, '#228822', f'$R_{{ne}}$ = {_R_NE:.1f} mm', 0.73),
    (_R_ARC,'#cc3300', f'$R_{{arc}}$ = {_R_ARC:.2f} mm', 0.62),
]:
    t_lbl = a_hi_r * frac + a_lo_r * (1 - frac)
    ax.text(R * np.cos(t_lbl) + 0.5, R * np.sin(t_lbl) + 1.0,
            txt, fontsize=7.5, color=lc, ha='left')

# Iron label between bars 1 and 2
t_iron = 0.5 * 2 * np.pi / Q_r
r_iron = (_R_NE + _R_ARC) / 2
ax.text(r_iron * np.cos(t_iron), r_iron * np.sin(t_iron),
        'ferro\n(M250-50A)', fontsize=6.5, color='#444', ha='center', va='center',
        style='italic', zorder=7)

# Zoom bounds
xmin = (_R_ARC - _R_BOT_R) * np.cos(a_hi_r) - 4
xmax = R_re + 15
ymin = R_re * np.sin(a_lo_r) - 4
ymax = R_re * np.sin(a_hi_r) + 16
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.set_title(f'Detalhe — 4 barras (barras 1–4)  |  escala ampliada',
             fontsize=12, color='#111', pad=5)

leg_r = [mpatches.Patch(fc=IRON,  ec=EDG,      label='Ferro (M250-50A)'),
         mpatches.Patch(fc=ALU,   ec='#1a5580', label='Alumínio (barra)'),
         mpatches.Patch(fc=SHAFT, ec=EDG,       label='Eixo')]
ax.legend(handles=leg_r, loc='lower right', fontsize=8, framealpha=0.9)

fig_r.suptitle(
    f'Geometria do Rotor  |  $Q_r$ = {Q_r}  |  $R_{{re}}$ = {R_re} mm  |  '
    f'$R_{{ri}}$ = {R_ri} mm (Ø42 H7)  |  escala 28/52',
    fontsize=12, color='#111', y=0.975)

out_r = '/home/ribb/Área de trabalho/ufmg/trab_femm/rotor_geometry_new.png'
fig_r.savefig(out_r, dpi=160, bbox_inches='tight', facecolor=BG)
print(f'Salvo: {out_r}')


# ══════════════════════════════════════════════════════════════════════════════
#  FULL MOTOR (stator + rotor + airgap)
# ══════════════════════════════════════════════════════════════════════════════

fig_m, ax = plt.subplots(1, 1, figsize=(9, 9), facecolor=BG)
ax.set_aspect('equal'); ax.set_facecolor(BG); ax.axis('off')

# Outer air
ax.add_patch(plt.Circle((0, 0), R_se,  fc=AIR,  ec=EDG, lw=0.5, zorder=0))
# Stator iron
ax.add_patch(plt.Circle((0, 0), R_se,  fc=IRON, ec=EDG, lw=1.1, zorder=1))
# Airgap (bore = AIR)
ax.add_patch(plt.Circle((0, 0), R_si,  fc=AIR,  ec='none',      zorder=2))
# Rotor iron
ax.add_patch(plt.Circle((0, 0), R_re,  fc=IRON, ec='none',      zorder=2))
# Shaft with keyways
ax.add_patch(plt.Polygon(shaft_hole_with_keyways(), closed=True,
                          fc=SHAFT, ec=EDG, lw=0.7, zorder=5))

# Stator slots
for i in range(Q_s):
    px, py = stator_slot_poly(i, n_arc=8)
    ax.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                              fc=CU, ec=EDG, lw=0.2, alpha=0.90, zorder=3))

# Rotor bars
for n in range(Q_r):
    px, py = rotor_bar_poly(n, n_arc=40)
    ax.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                              fc=ALU, ec='#1a5580', lw=0.3, alpha=0.95, zorder=3))

# Airgap mid-line
t_g = np.linspace(0, 2 * np.pi, 400)
ax.plot(57.25 * np.cos(t_g), 57.25 * np.sin(t_g),
        color='#cc2222', lw=0.6, ls='--', alpha=0.5, zorder=4)

# Labels
ax.text(0, R_se + 5, f'$Q_s$ = {Q_s}  estator', fontsize=10,
        ha='center', color=IRON, fontweight='bold',
        bbox=dict(fc='none', ec='none'))
ax.text(0, -(R_se + 8), f'$Q_r$ = {Q_r}  rotor', fontsize=10,
        ha='center', color='#1a5580', fontweight='bold',
        bbox=dict(fc='none', ec='none'))

ax.set_xlim(-R_se - 14, R_se + 14)
ax.set_ylim(-R_se - 14, R_se + 14)
ax.set_title(
    f'Motor completo  |  $Q_s$ = {Q_s}  /  $Q_r$ = {Q_r}  |  '
    f'$g$ = 0,5 mm  |  P = 6  |  M250-50A',
    fontsize=12, color='#111', pad=8)

leg_m = [mpatches.Patch(fc=IRON,  ec=EDG,      label='Ferro M250-50A'),
         mpatches.Patch(fc=CU,    ec=EDG,       label='Cobre (estator)'),
         mpatches.Patch(fc=ALU,   ec='#1a5580', label='Alumínio (rotor)'),
         mpatches.Patch(fc=SHAFT, ec=EDG,       label='Eixo (Ø42 H7)')]
ax.legend(handles=leg_m, loc='lower right', fontsize=9, framealpha=0.92)

out_m = '/home/ribb/Área de trabalho/ufmg/trab_femm/motor_geometry_new.png'
fig_m.savefig(out_m, dpi=160, bbox_inches='tight', facecolor=BG)
print(f'Salvo: {out_m}')

plt.show()
print('Concluído.')
