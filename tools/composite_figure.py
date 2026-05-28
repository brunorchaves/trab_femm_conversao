"""
composite_figure.py — Figura composta alta qualidade para o relatório
Layout: (a) campo |B| em cima (largura total), (b) estator + (c) rotor em baixo
Espelha motor_details.png com texto nítido e renderização matplotlib.
"""
import os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
from PIL import Image

_ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RESULTS = os.path.join(_ROOT, 'results')
_RELAT   = os.path.join(_ROOT, 'relatorio_corrigido')

rcParams['font.family'] = 'DejaVu Sans'
rcParams['font.size']   = 10

# ── Palette ───────────────────────────────────────────────────────────────────
IRON  = '#d4cfc5'
CU    = '#c0391a'
ALU   = '#5aabda'
AIR   = '#dce8f5'
EDG   = '#2a2a2a'
BG    = 'white'

# ── Stator parameters ─────────────────────────────────────────────────────────
R_se      = 91.4
R_si      = 57.5
Q_s       = 36
w_open    = 2.8
h_neck    = 0.6
h_wedge   = 0.548
h_slot    = 18.5
w_body    = 5.444
R_bot_arc = 3.885

_hw = w_open / 2
_hb = w_body / 2
_Rn = R_si + h_neck
_Rw = R_si + h_neck + h_wedge
_Rb = R_si + h_slot
_ARC_CX = R_si + h_slot - R_bot_arc  # 72.115

_CORNER = (_Rw, _hb)
_dx = _ARC_CX - _CORNER[0]
_dy = 0.0 - _CORNER[1]
_D  = math.hypot(_dx, _dy)
_L  = math.sqrt(_D**2 - R_bot_arc**2)
_base  = math.atan2(_dy, _dx)
_alpha = math.asin(R_bot_arc / _D)
_Tx = _CORNER[0] + _L * math.cos(_base - _alpha)
_Ty = _CORNER[1] + _L * math.sin(_base - _alpha)
if _Ty < 0:
    _Tx = _CORNER[0] + _L * math.cos(_base + _alpha)
    _Ty = _CORNER[1] + _L * math.sin(_base + _alpha)

BASE_S = [
    (R_si, +_hw), (_Rn, +_hw), (_Rw, +_hb), (_Tx, +_Ty), (_Rb, 0.0),
    (_Tx, -_Ty),  (_Rw, -_hb), (_Rn, -_hw), (R_si, -_hw),
]

# ── Rotor parameters ──────────────────────────────────────────────────────────
R_re      = 57.0
R_ri      = 21.0
Q_r       = 28
_W_OPEN_R = 0.600
_W_TOP_R  = 6.198
_R_BOT_R  = 2.031 / 2.0   # 1.0155
_Y_FLARE  = 2.600
_Y_BOT    = 22.000
_R_NE     = R_re - _Y_FLARE        # 54.4
_R_ARC    = R_re - _Y_BOT + _R_BOT_R  # 36.0155
_HALF_DEG_R = np.degrees(np.arcsin(_W_OPEN_R / 2 / R_re))

BASE_R = [
    (R_re,   +_W_OPEN_R / 2),
    (_R_NE,  +_W_TOP_R  / 2),
    (_R_ARC, +_R_BOT_R),
    (_R_ARC, -_R_BOT_R),
    (_R_NE,  -_W_TOP_R  / 2),
    (R_re,   -_W_OPEN_R / 2),
]

# ── Geometry helpers ──────────────────────────────────────────────────────────
def rot_pts(pts, theta):
    c, s = np.cos(theta), np.sin(theta)
    return [(c*x - s*y, s*x + c*y) for x, y in pts]

def slot_bottom_arc_s(Pstart, Pend, cxa, cya, n=60):
    a0 = np.arctan2(Pstart[1]-cya, Pstart[0]-cxa)
    a1 = np.arctan2(Pend[1]-cya,   Pend[0]-cxa)
    if a1 <= a0: a1 += 2*np.pi
    t = np.linspace(a0, a1, n)
    return cxa + R_bot_arc*np.cos(t), cya + R_bot_arc*np.sin(t)

def stator_slot_poly(i, n_arc=100):
    theta = i * 2*np.pi / Q_s
    pts   = rot_pts(BASE_S, theta)
    P1,P2,P3,P4,P5,P6,P7,P8,P9 = pts
    c, s  = np.cos(theta), np.sin(theta)
    cxa, cya = c*_ARC_CX, s*_ARC_CX
    a9 = np.arctan2(P9[1], P9[0])
    a1a= np.arctan2(P1[1], P1[0])
    if a1a < a9: a1a += 2*np.pi
    t = np.linspace(a9, a1a, max(4, n_arc//4))
    ox, oy = R_si*np.cos(t), R_si*np.sin(t)
    bx1,by1 = slot_bottom_arc_s(P6,P5,cxa,cya, n_arc//2)
    bx2,by2 = slot_bottom_arc_s(P5,P4,cxa,cya, n_arc//2)
    arc_x = np.concatenate([bx2[::-1], bx1[::-1]])
    arc_y = np.concatenate([by2[::-1], by1[::-1]])
    return (np.concatenate([ox,[P2[0],P3[0]],arc_x,[P7[0],P8[0]]]),
            np.concatenate([oy,[P2[1],P3[1]],arc_y,[P7[1],P8[1]]]))

def rotor_bar_poly(n, n_arc=120):
    theta = n * 2*np.pi / Q_r
    pts   = rot_pts(BASE_R, theta)
    P1,P2,P3,P4,P5,P6 = pts
    cx,cy = (P3[0]+P4[0])/2, (P3[1]+P4[1])/2
    rb    = np.hypot(P3[0]-cx, P3[1]-cy)
    a3    = np.arctan2(P3[1]-cy, P3[0]-cx)
    tb    = np.linspace(a3, a3+np.pi, n_arc)
    bx,by = cx+rb*np.cos(tb), cy+rb*np.sin(tb)
    a6  = np.arctan2(P6[1], P6[0])
    a1a = np.arctan2(P1[1], P1[0])
    if a1a < a6: a1a += 2*np.pi
    top = np.linspace(a6, a1a, max(4, n_arc//20))
    ox,oy = R_re*np.cos(top), R_re*np.sin(top)
    return (np.concatenate([ox,[P1[0],P2[0],P3[0]],bx,[P4[0],P5[0],P6[0]]]),
            np.concatenate([oy,[P1[1],P2[1],P3[1]],by,[P4[1],P5[1],P6[1]]]))

def dim(ax, x1,y1,x2,y2, label, lcolor='#222', fsize=9.5,
        tx=None, ty=None, rot=0):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle='<->', color=lcolor, lw=1.1,
                                mutation_scale=10))
    if tx is None: tx=(x1+x2)/2
    if ty is None: ty=(y1+y2)/2
    ax.text(tx, ty, label, fontsize=fsize, color=lcolor,
            ha='center', va='center', rotation=rot,
            bbox=dict(fc='white', ec='none', alpha=0.92, pad=2))


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA COMPOSTA
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(13, 11), facecolor=BG)
gs  = fig.add_gridspec(2, 2,
                        height_ratios=[1.15, 1],
                        hspace=0.07, wspace=0.05,
                        left=0.02, right=0.98,
                        bottom=0.02, top=0.98)

ax_a = fig.add_subplot(gs[0, :])
ax_b = fig.add_subplot(gs[1, 0])
ax_c = fig.add_subplot(gs[1, 1])

for ax in [ax_a, ax_b, ax_c]:
    ax.axis('off')
    ax.set_facecolor(BG)


# ── (a) Density plot screenshot ───────────────────────────────────────────────
img_path = os.path.join(_RELAT, 'density_plot_screenshot.png')
if os.path.exists(img_path):
    img = np.array(Image.open(img_path))
    ax_a.imshow(img, aspect='auto', interpolation='lanczos')
ax_a.text(0.01, 0.97, 'a)', transform=ax_a.transAxes,
          fontsize=16, fontweight='bold', va='top', color='#111')


# ── (b) Stator slot detail ────────────────────────────────────────────────────
ax_b.set_aspect('equal')
ax_b.set_title('Detalhe ranhuras do estator  (slots 1–3)', fontsize=10, pad=5, color='#111')
ax_b.text(0.02, 0.97, '(b)', transform=ax_b.transAxes,
          fontsize=12, fontweight='bold', va='top', color='#111')

DS    = [0, 1, 2]
a_lo  = (DS[0]  - 1.0) * 2*np.pi / Q_s
a_hi  = (DS[-1] + 2.2) * 2*np.pi / Q_s
t_out = np.linspace(a_lo, a_hi, 400)

# Iron ring
iron_x = np.concatenate([R_se*np.cos(t_out), R_si*np.cos(t_out[::-1])])
iron_y = np.concatenate([R_se*np.sin(t_out), R_si*np.sin(t_out[::-1])])
ax_b.fill(iron_x, iron_y, color=IRON, zorder=1)
ax_b.fill(np.append(R_si*np.cos(t_out), 0),
          np.append(R_si*np.sin(t_out), 0), color=AIR, alpha=0.45, zorder=0)

# Reference arcs
for R, lc, ls, lw in [(R_se, EDG, '-', 1.5), (R_si, '#0044cc', '--', 1.1),
                       (_Rn, '#1a7a1a', ':', 0.9), (_Rb, '#bb2200', ':', 0.9)]:
    ax_b.plot(R*np.cos(t_out), R*np.sin(t_out), color=lc, ls=ls, lw=lw, zorder=5)

# Slots — cores: vermelho, azul, verde (igual ao motor_details.png)
slot_colors = [CU, '#3878c8', '#2aaa55']
for k, i in enumerate(DS):
    px, py = stator_slot_poly(i)
    ax_b.add_patch(plt.Polygon(list(zip(px,py)), closed=True,
                               fc=slot_colors[k], ec=EDG, lw=0.8, alpha=0.93, zorder=3))
    theta_c = i * 2*np.pi / Q_s
    r_lbl   = (_Rw + _Rb) / 2
    ax_b.text(r_lbl*np.cos(theta_c), r_lbl*np.sin(theta_c),
              str(i+1), fontsize=11, color='white', ha='center', va='center',
              fontweight='bold', zorder=6)

# Cotas — slot 0
dim(ax_b, R_si+0.6, -_hw, R_si+0.6, +_hw,
    f'$w_o$={w_open} mm', lcolor='#0044cc', fsize=9,
    tx=R_si+4.8, ty=0, rot=90)
dim(ax_b, _Rw-0.8, -_hb, _Rw-0.8, +_hb,
    f'$w_b$={w_body} mm', lcolor='#bb2200', fsize=9,
    tx=_Rw-5.2, ty=0, rot=90)
dim(ax_b, R_si, -4.0, _Rb, -4.0,
    f'$h_s$={h_slot} mm', lcolor='#222', fsize=9,
    tx=(R_si+_Rb)/2, ty=-6.2)
ax_b.text(_Rb+1.0, 2.8,
          f'$R_{{bot}}$={R_bot_arc} mm', fontsize=8.5, color='#bb2200', ha='left')

# Crop justo (igual ao motor_details.png)
ax_b.set_xlim(53, 86)
ax_b.set_ylim(-11, 25)

leg_s = [mpatches.Patch(fc=IRON, ec=EDG, label='Ferro (M250-50A)'),
         mpatches.Patch(fc=CU,   ec=EDG, label='Cobre')]
ax_b.legend(handles=leg_s, loc='lower right', fontsize=8.5, framealpha=0.97)


# ── (c) Rotor bar detail ──────────────────────────────────────────────────────
ax_c.set_aspect('equal')
ax_c.set_title('Detalhe barras do rotor  (barras 1–3)', fontsize=10, pad=5, color='#111')
ax_c.text(0.02, 0.97, '(c)', transform=ax_c.transAxes,
          fontsize=12, fontweight='bold', va='top', color='#111')

DB     = [0, 1, 2]
a_lo_r = (DB[0]  - 1.0) * 2*np.pi / Q_r
a_hi_r = (DB[-1] + 2.2) * 2*np.pi / Q_r
t_arc  = np.linspace(a_lo_r, a_hi_r, 400)

# Iron ring
ring_x = np.concatenate([R_re*np.cos(t_arc), R_ri*np.cos(t_arc[::-1])])
ring_y = np.concatenate([R_re*np.sin(t_arc), R_ri*np.sin(t_arc[::-1])])
ax_c.fill(ring_x, ring_y, color=IRON, zorder=1)

for R, lc, ls, lw in [
    (R_re,   EDG,       '-',  1.5),
    (_R_NE,  '#1a7a1a', ':',  1.0),
    (_R_ARC, '#bb2200', ':',  0.9),
    (R_ri,   '#777',    '-',  0.7),
]:
    ax_c.plot(R*np.cos(t_arc), R*np.sin(t_arc), color=lc, ls=ls, lw=lw, zorder=5)

bar_colors = [ALU, '#2a9fd0', '#1a8fc0']
for k, n in enumerate(DB):
    px, py = rotor_bar_poly(n)
    ax_c.add_patch(plt.Polygon(list(zip(px,py)), closed=True,
                               fc=bar_colors[k % len(bar_colors)],
                               ec='#1a5580', lw=0.9, alpha=0.95, zorder=3))
    theta_c = n * 2*np.pi / Q_r
    r_lbl   = (_R_NE + _R_ARC) / 2
    ax_c.text(r_lbl*np.cos(theta_c), r_lbl*np.sin(theta_c),
              str(n+1), fontsize=11, color='white', ha='center', va='center',
              fontweight='bold', zorder=6)

# Cotas — barra 0
dim(ax_c, R_re+2.5, -_W_OPEN_R/2, R_re+2.5, +_W_OPEN_R/2,
    f'$w_o$={_W_OPEN_R} mm', lcolor='#0044cc', fsize=9,
    tx=R_re+7.0, ty=0, rot=90)
dim(ax_c, _R_NE-1.0, -_W_TOP_R/2, _R_NE-1.0, +_W_TOP_R/2,
    f'$w_{{top}}$={_W_TOP_R:.3f} mm', lcolor='#1a7a1a', fsize=9,
    tx=_R_NE-6.8, ty=0, rot=90)

off_t = np.radians(-4.5)
dim(ax_c,
    (_R_ARC-_R_BOT_R)*np.cos(off_t), (_R_ARC-_R_BOT_R)*np.sin(off_t),
    R_re*np.cos(off_t), R_re*np.sin(off_t),
    f'$h_r$={_Y_BOT:.1f} mm', lcolor='#222', fsize=9,
    tx=((R_re+_R_ARC-_R_BOT_R)/2)*np.cos(off_t) - 5,
    ty=((R_re+_R_ARC-_R_BOT_R)/2)*np.sin(off_t), rot=90)

# Labels de raio (lado direito do arco, igual ao motor_details.png)
for R, lc, txt, frac in [
    (R_re,   EDG,       f'$R_{{re}}$={R_re:.1f} mm', 0.88),
    (_R_NE,  '#1a7a1a', f'$R_{{ne}}$={_R_NE:.1f} mm',   0.72),
    (_R_ARC, '#bb2200', f'$R_{{arc}}$={_R_ARC:.2f} mm',  0.55),
]:
    t_lbl = a_hi_r*frac + a_lo_r*(1-frac)
    ax_c.text(R*np.cos(t_lbl)+0.6, R*np.sin(t_lbl)+0.8,
              txt, fontsize=8.5, color=lc, ha='left', zorder=7)

ax_c.text(_R_ARC-_R_BOT_R-1.2, 1.5,
          f'$r_{{bot}}$={_R_BOT_R:.4f} mm', fontsize=8.5, color='#bb2200', ha='right')

# Crop justo
xmin_r = (_R_ARC-_R_BOT_R)*np.cos(a_hi_r) - 4
xmax_r = R_re + 18
ymin_r = R_re*np.sin(a_lo_r) - 4
ymax_r = R_re*np.sin(a_hi_r) + 18
ax_c.set_xlim(xmin_r, xmax_r)
ax_c.set_ylim(ymin_r, ymax_r)

leg_r = [mpatches.Patch(fc=IRON, ec=EDG,      label='Ferro (M250-50A)'),
         mpatches.Patch(fc=ALU,  ec='#1a5580', label='Alumínio (barra)')]
ax_c.legend(handles=leg_r, loc='lower right', fontsize=8.5, framealpha=0.97)


# ── Salvar ────────────────────────────────────────────────────────────────────
out = os.path.join(_RESULTS, 'motor_composite_figure.png')
fig.savefig(out, dpi=200, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Salvo: {out}')

import os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
from PIL import Image

_ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RESULTS = os.path.join(_ROOT, 'results')
_RELAT   = os.path.join(_ROOT, 'relatorio_corrigido')

rcParams['font.family'] = 'DejaVu Sans'

# ── Palette ───────────────────────────────────────────────────────────────────
IRON  = '#cdc9be'
CU    = '#b84020'
ALU   = '#4a9fd4'
AIR   = '#e8eaf0'
SHAFT = '#8a8a9a'
EDG   = '#333333'
BG    = 'white'

# ── Stator parameters ────────────────────────────────────────────────────────
R_se      = 91.4
R_si      = 57.5
Q_s       = 36
w_open    = 2.8
h_neck    = 0.6
h_wedge   = 0.548
h_slot    = 18.5
w_body    = 5.444
R_bot_arc = 3.885

_hw = w_open / 2
_hb = w_body / 2
_Rn = R_si + h_neck
_Rw = R_si + h_neck + h_wedge
_Rb = R_si + h_slot
_ARC_CX = R_si + h_slot - R_bot_arc  # 72.115
_CORNER = (_Rw, _hb)
_dx = _ARC_CX - _CORNER[0]
_dy = 0.0 - _CORNER[1]
_D = math.hypot(_dx, _dy)
_L = math.sqrt(_D**2 - R_bot_arc**2)
_base = math.atan2(_dy, _dx)
_alpha = math.asin(R_bot_arc / _D)
_Tx = _CORNER[0] + _L * math.cos(_base - _alpha)
_Ty = _CORNER[1] + _L * math.sin(_base - _alpha)
if _Ty < 0:
    _Tx = _CORNER[0] + _L * math.cos(_base + _alpha)
    _Ty = _CORNER[1] + _L * math.sin(_base + _alpha)

BASE_S = [
    (R_si, +_hw), (_Rn, +_hw), (_Rw, +_hb), (_Tx, +_Ty), (_Rb, 0.0),
    (_Tx, -_Ty),  (_Rw, -_hb), (_Rn, -_hw), (R_si, -_hw),
]

# ── Rotor parameters ─────────────────────────────────────────────────────────
R_re   = 57.0
R_ri   = 21.0
Q_r    = 28
_KW_HW      = 5.00
_KW_R_OUTER = 25.17
_KW_FILLET  = 1.00
_W_OPEN_R = 0.600
_W_TOP_R  = 6.198
_R_BOT_R  = 2.031 / 2.0
_Y_FLARE  = 2.600
_Y_BOT    = 22.000
_R_NE     = R_re - _Y_FLARE
_R_ARC    = R_re - _Y_BOT + _R_BOT_R
_HALF_DEG_R = np.degrees(np.arcsin(_W_OPEN_R / 2 / R_re))
_PITCH_R    = 360.0 / Q_r

BASE_R = [
    (R_re,  +_W_OPEN_R / 2),
    (_R_NE, +_W_TOP_R  / 2),
    (_R_ARC, +_R_BOT_R),
    (_R_ARC, -_R_BOT_R),
    (_R_NE, -_W_TOP_R  / 2),
    (R_re,  -_W_OPEN_R / 2),
]


# ── Geometry helpers ──────────────────────────────────────────────────────────
def rot_pts(pts, theta):
    c, s = np.cos(theta), np.sin(theta)
    return [(c * x - s * y, s * x + c * y) for x, y in pts]


def slot_bottom_arc_s(Pstart, Pend, cx_arc, cy_arc, n=60):
    a_start = np.arctan2(Pstart[1] - cy_arc, Pstart[0] - cx_arc)
    a_end   = np.arctan2(Pend[1]   - cy_arc, Pend[0]   - cx_arc)
    if a_end <= a_start:
        a_end += 2 * np.pi
    t = np.linspace(a_start, a_end, n)
    return cx_arc + R_bot_arc * np.cos(t), cy_arc + R_bot_arc * np.sin(t)


def stator_slot_poly(i, n_arc=60):
    theta = i * 2 * np.pi / Q_s
    pts = rot_pts(BASE_S, theta)
    P1, P2, P3, P4, P5, P6, P7, P8, P9 = pts
    c, s = np.cos(theta), np.sin(theta)
    cx_arc, cy_arc = c * _ARC_CX, s * _ARC_CX
    a9 = np.arctan2(P9[1], P9[0])
    a1 = np.arctan2(P1[1], P1[0])
    if a1 < a9:
        a1 += 2 * np.pi
    t_op = np.linspace(a9, a1, max(4, n_arc // 4))
    ox = R_si * np.cos(t_op)
    oy = R_si * np.sin(t_op)
    bx1, by1 = slot_bottom_arc_s(P6, P5, cx_arc, cy_arc, n_arc // 2)
    bx2, by2 = slot_bottom_arc_s(P5, P4, cx_arc, cy_arc, n_arc // 2)
    arc_x = np.concatenate([bx2[::-1], bx1[::-1]])
    arc_y = np.concatenate([by2[::-1], by1[::-1]])
    px = np.concatenate([ox, [P2[0], P3[0]], arc_x, [P7[0], P8[0]]])
    py = np.concatenate([oy, [P2[1], P3[1]], arc_y, [P7[1], P8[1]]])
    return px, py


def rotor_bar_poly(n, n_arc=80):
    theta = n * 2 * np.pi / Q_r
    pts = rot_pts(BASE_R, theta)
    P1, P2, P3, P4, P5, P6 = pts
    cx = (P3[0] + P4[0]) / 2
    cy = (P3[1] + P4[1]) / 2
    r_b = np.hypot(P3[0] - cx, P3[1] - cy)
    a3 = np.arctan2(P3[1] - cy, P3[0] - cx)
    t_bot = np.linspace(a3, a3 + np.pi, n_arc)
    bx = cx + r_b * np.cos(t_bot)
    by = cy + r_b * np.sin(t_bot)
    a6 = np.arctan2(P6[1], P6[0])
    a1 = np.arctan2(P1[1], P1[0])
    if a1 < a6:
        a1 += 2 * np.pi
    t_op = np.linspace(a6, a1, max(4, n_arc // 20))
    ox = R_re * np.cos(t_op)
    oy = R_re * np.sin(t_op)
    xs = np.concatenate([ox, [P1[0], P2[0], P3[0]], bx, [P4[0], P5[0], P6[0]]])
    ys = np.concatenate([oy, [P1[1], P2[1], P3[1]], by, [P4[1], P5[1], P6[1]]])
    return xs, ys


def dim(ax, x1, y1, x2, y2, label, lcolor='#222', fsize=8,
        tx=None, ty=None, rot=0):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='<->', color=lcolor, lw=0.9,
                                mutation_scale=8))
    if tx is None: tx = (x1 + x2) / 2
    if ty is None: ty = (y1 + y2) / 2
    ax.text(tx, ty, label, fontsize=fsize, color=lcolor, ha='center',
            va='center', rotation=rot,
            bbox=dict(fc='white', ec='none', alpha=0.75, pad=1))


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA COMPOSTA: (a) em cima, (b)+(c) em baixo
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(14, 16), facecolor=BG)
gs  = fig.add_gridspec(2, 2,
                        height_ratios=[1.1, 1],
                        hspace=0.08, wspace=0.06,
                        left=0.02, right=0.98,
                        bottom=0.03, top=0.95)

ax_a = fig.add_subplot(gs[0, :])   # linha 0, colunas 0+1 (largura total)
ax_b = fig.add_subplot(gs[1, 0])   # linha 1, coluna 0
ax_c = fig.add_subplot(gs[1, 1])   # linha 1, coluna 1

panel_info = [
    (ax_a, '(a)', 'Campo magnético $|B|$ — Config. I  (FEMM 4.2)'),
    (ax_b, '(b)', 'Detalhe ranhuras do estator  (slots 1–3)'),
    (ax_c, '(c)', 'Detalhe barras do rotor  (barras 1–3)'),
]

for ax, lbl, ttl in panel_info:
    ax.set_facecolor(BG)
    ax.axis('off')
    ax.set_title(ttl, fontsize=10.5, color='#111', pad=4)
    ax.text(0.01, 0.99, lbl, transform=ax.transAxes,
            fontsize=13, fontweight='bold', color='#111',
            va='top', ha='left')


# ── (a) density plot screenshot ───────────────────────────────────────────────
img_path = os.path.join(_RELAT, 'density_plot_screenshot.png')
if os.path.exists(img_path):
    img = np.array(Image.open(img_path))
    ax_a.imshow(img, aspect='auto', interpolation='lanczos')
    ax_a.set_xlim(0, img.shape[1])
    ax_a.set_ylim(img.shape[0], 0)
else:
    ax_a.text(0.5, 0.5, 'density_plot_screenshot.png\nnão encontrado',
              ha='center', va='center', transform=ax_a.transAxes, fontsize=10)


# ── (b) stator slot detail ────────────────────────────────────────────────────
ax_b.set_aspect('equal')
DS = [0, 1, 2]
a_lo = (DS[0]  - 0.85) * 2 * np.pi / Q_s
a_hi = (DS[-1] + 1.85) * 2 * np.pi / Q_s
t_out = np.linspace(a_lo, a_hi, 300)

iron_x = np.concatenate([R_se * np.cos(t_out), R_si * np.cos(t_out[::-1])])
iron_y = np.concatenate([R_se * np.sin(t_out), R_si * np.sin(t_out[::-1])])
ax_b.fill(iron_x, iron_y, color=IRON, zorder=1)
ax_b.fill(np.append(R_si * np.cos(t_out), 0),
          np.append(R_si * np.sin(t_out), 0), color=AIR, alpha=0.6, zorder=0)

for R, lc, ls, lw in [(R_se, EDG, '-', 1.2), (R_si, '#0055aa', '--', 0.9),
                       (_Rn, '#228822', ':', 0.8), (_Rw, '#884400', ':', 0.8),
                       (_Rb, '#cc3300', ':', 0.8)]:
    ax_b.plot(R * np.cos(t_out), R * np.sin(t_out), color=lc, ls=ls, lw=lw, zorder=5)

slot_colors = [CU, '#3a7ec8', '#2aaa55']
for k, i in enumerate(DS):
    px, py = stator_slot_poly(i, n_arc=80)
    ax_b.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                               fc=slot_colors[k], ec=EDG, lw=0.7, alpha=0.9, zorder=3))
    theta_c = i * 2 * np.pi / Q_s
    r_lbl = (_Rw + _Tx) / 2
    ax_b.text(r_lbl * np.cos(theta_c), r_lbl * np.sin(theta_c),
              str(i + 1), fontsize=9, color='white', ha='center', va='center',
              fontweight='bold', zorder=6)

# Cotas
dim(ax_b, R_si + 0.8, -_hw, R_si + 0.8, +_hw,
    f'$w_o$={w_open} mm', lcolor='#0055aa', fsize=7.5,
    tx=R_si + 4.0, ty=0, rot=90)
dim(ax_b, R_si, _hw + 1.2, _Rn, _hw + 1.2,
    f'$h_n$={h_neck} mm', lcolor='#228822', fsize=7.5,
    tx=(R_si + _Rn) / 2, ty=_hw + 2.3)
dim(ax_b, _Rw - 0.8, -_hb, _Rw - 0.8, +_hb,
    f'$w_b$={w_body} mm', lcolor='#884400', fsize=7.5,
    tx=_Rw - 4.5, ty=0, rot=90)
dim(ax_b, R_si, -2.0, _Rb, -2.0,
    f'$h_s$={h_slot} mm', lcolor='#222', fsize=7.5,
    tx=(R_si + _Rb) / 2, ty=-3.5)
ax_b.text(_Rb + 1.2, 2.0, f'$R_{{bot}}$={R_bot_arc} mm', fontsize=7, color='#cc3300')

xs_d = [p[0] for i in DS for p in rot_pts(BASE_S, i * 2 * np.pi / Q_s)]
ys_d = [p[1] for i in DS for p in rot_pts(BASE_S, i * 2 * np.pi / Q_s)]
mg = 6
ax_b.set_xlim(min(xs_d) - mg, R_se + mg + 8)
ax_b.set_ylim(min(ys_d) - mg - 1, max(ys_d) + mg + 5)

leg_s = [mpatches.Patch(fc=IRON, ec=EDG, label='Ferro (M250-50A)'),
         mpatches.Patch(fc=CU,   ec=EDG, label='Cobre')]
ax_b.legend(handles=leg_s, loc='lower right', fontsize=7.5, framealpha=0.9)


# ── (c) rotor bar detail ──────────────────────────────────────────────────────
ax_c.set_aspect('equal')
DB = [0, 1, 2]
_dh_r  = np.radians(_HALF_DEG_R)
a_lo_r = (DB[0]  - 0.9) * 2 * np.pi / Q_r
a_hi_r = (DB[-1] + 0.9) * 2 * np.pi / Q_r
t_arc  = np.linspace(a_lo_r, a_hi_r, 300)

ring_x = np.concatenate([R_re * np.cos(t_arc), R_ri * np.cos(t_arc[::-1])])
ring_y = np.concatenate([R_re * np.sin(t_arc), R_ri * np.sin(t_arc[::-1])])
ax_c.fill(ring_x, ring_y, color=IRON, zorder=1)

for R, lc, ls, lw in [
    (R_re,  EDG,       '-',  1.2),
    (_R_NE, '#228822', ':',  0.8),
    (_R_ARC,'#cc3300', ':',  0.7),
    (R_ri,  SHAFT,     '-',  1.0),
]:
    ax_c.plot(R * np.cos(t_arc), R * np.sin(t_arc), color=lc, ls=ls, lw=lw, zorder=5)

bar_colors = [ALU, '#2a9fd0', '#1a8fc0']
for k, n in enumerate(DB):
    px, py = rotor_bar_poly(n, n_arc=120)
    ax_c.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                               fc=bar_colors[k % len(bar_colors)],
                               ec='#1a5580', lw=0.9, alpha=0.95, zorder=3))
    theta_c = n * 2 * np.pi / Q_r
    r_lbl = (_R_NE + _R_ARC) / 2
    ax_c.text(r_lbl * np.cos(theta_c), r_lbl * np.sin(theta_c),
              str(n + 1), fontsize=9, color='white', ha='center', va='center',
              fontweight='bold', zorder=6)

# Cotas
dim(ax_c, R_re + 2.0, -_W_OPEN_R/2, R_re + 2.0, +_W_OPEN_R/2,
    f'$w_o$={_W_OPEN_R:.3f} mm', lcolor='#0055aa', fsize=7.5,
    tx=R_re + 5.5, ty=0, rot=90)
dim(ax_c, _R_NE - 0.8, -_W_TOP_R/2, _R_NE - 0.8, +_W_TOP_R/2,
    f'$w_{{top}}$={_W_TOP_R:.3f} mm', lcolor='#228822', fsize=7.5,
    tx=_R_NE - 5.0, ty=0, rot=90)
off_t = np.radians(-3.5)
dim(ax_c,
    (_R_ARC - _R_BOT_R) * np.cos(off_t), (_R_ARC - _R_BOT_R) * np.sin(off_t),
    R_re * np.cos(off_t), R_re * np.sin(off_t),
    f'$h_r$={_Y_BOT:.1f} mm', lcolor='#222', fsize=7.5,
    tx=((R_re + _R_ARC - _R_BOT_R) / 2) * np.cos(off_t) - 4,
    ty=((R_re + _R_ARC - _R_BOT_R) / 2) * np.sin(off_t), rot=90)
ax_c.text(_R_ARC - _R_BOT_R - 1.0, 1.0,
          f'$r_{{bot}}$={_R_BOT_R:.3f} mm', fontsize=7, color='#cc3300', ha='right')

for R, lc, txt, frac in [
    (R_re,  EDG,       f'$R_{{re}}$={R_re} mm', 0.82),
    (_R_NE, '#228822', f'$R_{{ne}}$={_R_NE:.1f} mm', 0.70),
    (_R_ARC,'#cc3300', f'$R_{{arc}}$={_R_ARC:.2f} mm', 0.57),
]:
    t_lbl = a_hi_r * frac + a_lo_r * (1 - frac)
    ax_c.text(R * np.cos(t_lbl) + 0.5, R * np.sin(t_lbl) + 1.0,
              txt, fontsize=7.5, color=lc, ha='left')

xmin = (_R_ARC - _R_BOT_R) * np.cos(a_hi_r) - 4
xmax = R_re + 18
ymin = R_re * np.sin(a_lo_r) - 4
ymax = R_re * np.sin(a_hi_r) + 18
ax_c.set_xlim(xmin, xmax)
ax_c.set_ylim(ymin, ymax)

leg_r = [mpatches.Patch(fc=IRON, ec=EDG,      label='Ferro (M250-50A)'),
         mpatches.Patch(fc=ALU,  ec='#1a5580', label='Alumínio (barra)')]
ax_c.legend(handles=leg_r, loc='lower right', fontsize=7.5, framealpha=0.9)


# ── Salvar painéis separados + figura composta ────────────────────────────────

# Painel (a) — density plot separado
fig_a, ax_fa = plt.subplots(1, 1, figsize=(7, 7), facecolor=BG)
ax_fa.axis('off')
if os.path.exists(img_path):
    img2 = np.array(Image.open(img_path))
    ax_fa.imshow(img2, aspect='auto', interpolation='lanczos')
fig_a.savefig(os.path.join(_RESULTS, 'panel_a_field.png'), dpi=180, bbox_inches='tight', facecolor=BG)
plt.close(fig_a)
print(f'Salvo: {os.path.join(_RESULTS, "panel_a_field.png")}')

# Painel (b) — estator separado (reusa ax_b: salvar só a região)
extent_b = ax_b.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
out_b = os.path.join(_RESULTS, 'panel_b_stator.png')
fig.savefig(out_b, dpi=180, bbox_inches=extent_b.expanded(1.02, 1.05), facecolor=BG)
print(f'Salvo: {out_b}')

# Painel (c) — rotor separado
extent_c = ax_c.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
out_c = os.path.join(_RESULTS, 'panel_c_rotor.png')
fig.savefig(out_c, dpi=180, bbox_inches=extent_c.expanded(1.02, 1.05), facecolor=BG)
print(f'Salvo: {out_c}')

# Figura composta (mantém para referência)
fig.suptitle(
    'Motor de Indução Trifásico — $Q_s$=36 / $Q_r$=28 / $p$=3  |  '
    'Campo FEM e geometria das ranhuras',
    fontsize=12, color='#111', y=0.97)
out = os.path.join(_RESULTS, 'motor_composite_figure.png')
fig.savefig(out, dpi=180, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Salvo: {out}')
