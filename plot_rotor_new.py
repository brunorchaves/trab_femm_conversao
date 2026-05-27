"""
plot_rotor_new.py — Preview do rotor com ranhura trapezoidal semi-fechada (Q_r=56).

Parâmetros (Gemini):
  w_r_open  = 0.6 mm   (abertura no entreferro)
  h_r_neck  = 0.6 mm   (pescoço reto)
  w_r_top   = 3.1 mm   (largura superior do trapézio)
  w_r_bot   = 1.0 mm   (largura inferior / fundo)
  h_r_slot  = 22.0 mm  (profundidade total)
  R_re      = 57.0 mm  → R_bar_bot = 57.0 - 22.0 = 35.0 mm
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
rcParams['font.family'] = 'DejaVu Sans'

# ── Parâmetros ────────────────────────────────────────────────────────────────
R_re      = 57.0
R_ri      = 30.0
Q_r       = 56
w_r_open  = 0.6
h_r_neck  = 0.6
w_r_top   = 3.1
w_r_bot   = 1.0
h_r_slot  = 22.0

R_ne  = R_re - h_r_neck   # 56.4 mm  (fim do pescoço)
R_tb  = R_re - h_r_slot   # 35.0 mm  (fundo da barra)
hwo   = w_r_open / 2      # 0.30 mm
hwt   = w_r_top  / 2      # 1.55 mm
hwb   = w_r_bot  / 2      # 0.50 mm

# Paleta
IRON  = '#cdc9be'
ALU   = '#4a9fd4'
SHAFT = '#8a8a9a'
AIR   = '#e8eaf0'
EDG   = '#333333'
BG    = 'white'

# ── Perfil base da ranhura (frame local: x=radial, y=tangencial) ─────────────
# 8 nós do perfil, mais o arco de abertura (P8→P1) e arcos de face de dente
BASE = np.array([
    [R_re, +hwo],   # P1 – abertura CCW
    [R_ne, +hwo],   # P2 – fim pescoço CCW
    [R_ne, +hwt],   # P3 – ledge CCW  (início do trapézio)
    [R_tb, +hwb],   # P4 – fundo CCW
    [R_tb, -hwb],   # P5 – fundo CW
    [R_ne, -hwt],   # P6 – ledge CW
    [R_ne, -hwo],   # P7 – fim pescoço CW
    [R_re, -hwo],   # P8 – abertura CW
])


def rot(pts, theta):
    c, s = np.cos(theta), np.sin(theta)
    R = np.array([[c, -s], [s, c]])
    return (R @ pts.T).T


def bar_polygon(n, n_open=12):
    """Polígono da barra n incluindo arco de abertura (P8→P1)."""
    theta = n * 2 * np.pi / Q_r
    pts   = rot(BASE, theta)
    P1, P2, P3, P4, P5, P6, P7, P8 = pts

    # Arco de abertura: P8 → P1 CCW a R_re
    a8  = np.arctan2(P8[1], P8[0])
    a1  = np.arctan2(P1[1], P1[0])
    if a1 < a8:
        a1 += 2 * np.pi
    arc_t = np.linspace(a8, a1, n_open)
    arc_x = R_re * np.cos(arc_t)
    arc_y = R_re * np.sin(arc_t)

    # Polígono: arco abertura → pescoço dir → ledge dir → parede dir → fundo → parede esq → ledge esq → pescoço esq
    px = np.concatenate([arc_x, [P2[0], P3[0], P4[0], P5[0], P6[0], P7[0]]])
    py = np.concatenate([arc_y, [P2[1], P3[1], P4[1], P5[1], P6[1], P7[1]]])
    return px, py


def rotor_surface_arc(n1, n2, n=40):
    """Arco de face de dente entre barra n1 e barra n2 ao longo de R_re."""
    pts1 = rot(BASE, n1 * 2 * np.pi / Q_r)
    pts2 = rot(BASE, n2 * 2 * np.pi / Q_r)
    P1_n1 = pts1[0]   # P1 of bar n1
    P8_n2 = pts2[7]   # P8 of bar n2
    a1 = np.arctan2(P1_n1[1], P1_n1[0])
    a8 = np.arctan2(P8_n2[1], P8_n2[0])
    if a8 < a1:
        a8 += 2 * np.pi
    t = np.linspace(a1, a8, n)
    return R_re * np.cos(t), R_re * np.sin(t)


def dim(ax, x1, y1, x2, y2, label, lcolor='#222', fsize=8.5, tx=None, ty=None, rot_ang=0):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='<->', color=lcolor, lw=0.9, mutation_scale=8))
    if tx is None:
        tx = (x1 + x2) / 2
    if ty is None:
        ty = (y1 + y2) / 2
    ax.text(tx, ty, label, fontsize=fsize, color=lcolor, ha='center', va='center',
            rotation=rot_ang, bbox=dict(fc='white', ec='none', alpha=0.75, pad=1))


# ══════════════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), facecolor=BG)
fig.subplots_adjust(left=0.01, right=0.99, bottom=0.07, top=0.91, wspace=0.04)

# ── ESQUERDA: seção transversal completa ─────────────────────────────────────
ax = ax1
ax.set_aspect('equal')
ax.set_facecolor(BG)
ax.axis('off')

# Disco de ferro
ax.add_patch(plt.Circle((0, 0), R_re, fc=IRON, ec=EDG, lw=1.1, zorder=1))
# Eixo
ax.add_patch(plt.Circle((0, 0), R_ri, fc=SHAFT, ec=EDG, lw=0.9, zorder=3))
# Fio central (detalhe)
ax.add_patch(plt.Circle((0, 0), R_ri * 0.5, fc='#606070', ec=EDG, lw=0.5, zorder=4))

# 56 barras
for n in range(Q_r):
    px, py = bar_polygon(n, n_open=8)
    ax.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                              fc=ALU, ec='#1a5580', lw=0.4, alpha=0.93, zorder=2))

# Arcos de face de dente (para mostrar a superfície correta)
for n in range(Q_r):
    tx, ty = rotor_surface_arc(n, (n + 1) % Q_r, n=20)
    ax.plot(tx, ty, color=EDG, lw=0.5, zorder=5)

# Cotas
ax.annotate('', xy=(-R_re, -R_re - 8), xytext=(R_re, -R_re - 8),
            arrowprops=dict(arrowstyle='<->', color='#222', lw=1.0, mutation_scale=9))
ax.text(0, -R_re - 12, f'Ø {2 * R_re:.0f} mm  ($R_{{re}}$ = {R_re} mm)',
        fontsize=9.5, ha='center', color='#222',
        bbox=dict(fc='white', ec='none', alpha=0.85))
ax.annotate('', xy=(-R_ri, R_ri + 5), xytext=(R_ri, R_ri + 5),
            arrowprops=dict(arrowstyle='<->', color='#555', lw=0.9, mutation_scale=8))
ax.text(0, R_ri + 9, f'Ø {2 * R_ri:.0f} mm  (eixo)',
        fontsize=8.5, ha='center', color='#555')

# Cota da profundidade da ranhura
r_dim = R_re - h_r_slot
ax.annotate('', xy=(R_re, 0), xytext=(r_dim, 0),
            arrowprops=dict(arrowstyle='<->', color='#cc3300', lw=1.0, mutation_scale=8))
ax.text((R_re + r_dim) / 2, 3.5, f'$h_r$ = {h_r_slot:.0f} mm',
        fontsize=8.5, ha='center', color='#cc3300')

ax.set_xlim(-R_re - 16, R_re + 16)
ax.set_ylim(-R_re - 20, R_re + 16)
ax.set_title(f'Rotor — $Q_r$ = {Q_r} barras trapezoidal semi-fechadas\n'
             f'$R_{{re}}$ = {R_re} mm  |  $R_{{tb}}$ = {R_tb:.0f} mm  |  $R_{{ri}}$ = {R_ri} mm',
             fontsize=11.5, color='#111', pad=5)


# ── DIREITA: detalhe 4 barras com perfil e cotas ─────────────────────────────
ax = ax2
ax.set_aspect('equal')
ax.set_facecolor(BG)
ax.axis('off')

DB = [0, 1, 2, 3]

# Definir janela angular
theta_lo = DB[0]  * 2 * np.pi / Q_r - np.radians(4)
theta_hi = DB[-1] * 2 * np.pi / Q_r + np.radians(4)
t_arc    = np.linspace(theta_lo, theta_hi, 300)

# Ferro (fundo)
ring_x = np.concatenate([R_re * np.cos(t_arc), R_ri * np.cos(t_arc[::-1])])
ring_y = np.concatenate([R_re * np.sin(t_arc), R_ri * np.sin(t_arc[::-1])])
ax.fill(ring_x, ring_y, color=IRON, zorder=1)

# Eixo
ax.fill(np.cos(np.linspace(0, 2*np.pi, 200)) * R_ri,
        np.sin(np.linspace(0, 2*np.pi, 200)) * R_ri,
        color=SHAFT, zorder=3)

# Arcos de referência
for R, lc, ls, lw in [(R_re, EDG, '-', 1.2), (R_ne, '#228822', ':', 0.8),
                       (R_tb, '#cc3300', ':', 0.8), (R_ri, EDG, '-', 0.8)]:
    ax.plot(R * np.cos(t_arc), R * np.sin(t_arc), color=lc, ls=ls, lw=lw, zorder=5)

# Barras
shades = [ALU, '#3aafde', '#2a9fce', '#1a8fbe']
for k, n in enumerate(DB):
    px, py = bar_polygon(n, n_open=30)
    ax.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                              fc=shades[k], ec='#1a5580', lw=0.8, alpha=0.93, zorder=3))
    theta_c = n * 2 * np.pi / Q_r
    r_lbl   = (R_tb + R_re) / 2
    ax.text(r_lbl * np.cos(theta_c), r_lbl * np.sin(theta_c),
            str(n + 1), fontsize=9, color='white', ha='center', va='center',
            fontweight='bold', zorder=6)

# Arcos de face de dente no detalhe
for n in DB:
    tx, ty = rotor_surface_arc(n, (n + 1) % Q_r, n=40)
    ax.plot(tx, ty, color=EDG, lw=0.7, zorder=6)

# ── Cotas na barra 0 (theta=0, eixo +X) ─────────────────────────────────────
pts0 = rot(BASE, 0.0)
P1, P2, P3, P4, P5, P6, P7, P8 = pts0

# w_r_open: abertura no entreferro (entre P8 e P1 na direção Y)
dim(ax, R_re + 2.5, -hwo, R_re + 2.5, +hwo,
    f'$w_o$ = {w_r_open} mm', lcolor='#0055aa', fsize=7.5,
    tx=R_re + 5.5, ty=0, rot_ang=90)

# h_r_neck: profundidade do pescoço
dim(ax, R_re, hwo + 1.5, R_ne, hwo + 1.5,
    f'$h_n$ = {h_r_neck} mm', lcolor='#228822', fsize=7.5,
    tx=(R_re + R_ne) / 2, ty=hwo + 3.2)

# w_r_top: largura no topo do trapézio (entre P3 e P6 — em P2 x-coord)
dim(ax, R_ne - 1.5, -hwt, R_ne - 1.5, +hwt,
    f'$w_{{top}}$ = {w_r_top} mm', lcolor='#228822', fsize=7.5,
    tx=R_ne - 4.5, ty=0, rot_ang=90)

# w_r_bot: largura no fundo (entre P4 e P5)
dim(ax, R_tb - 1.5, -hwb, R_tb - 1.5, +hwb,
    f'$w_{{bot}}$ = {w_r_bot} mm', lcolor='#cc3300', fsize=7.5,
    tx=R_tb - 5, ty=0, rot_ang=90)

# h_r_slot: profundidade total
dim(ax, R_re, -hwt - 2, R_tb, -hwt - 2,
    f'$h_r$ = {h_r_slot:.0f} mm', lcolor='#222', fsize=8,
    tx=(R_re + R_tb) / 2, ty=-hwt - 4)

# Passo angular
theta1 = 1 * 2 * np.pi / Q_r
r_ann  = R_re + 9
arc_t2 = np.linspace(np.radians(0.5), np.radians(360 / Q_r - 0.5), 40)
ax.plot(r_ann * np.cos(arc_t2), r_ann * np.sin(arc_t2), 'k-', lw=0.9, alpha=0.6)
t_mid = (0 + theta1) / 2
ax.text(r_ann * np.cos(t_mid), r_ann * np.sin(t_mid) + 3.5,
        f'{360 / Q_r:.2f}°\n(passo)', fontsize=7.5, color='#333',
        ha='center', va='bottom')

# Labels dos raios de referência
for R, lc, txt in [(R_re, EDG, f'$R_{{re}}$ = {R_re}'),
                   (R_ne, '#228822', f'$R_{{ne}}$ = {R_ne}'),
                   (R_tb, '#cc3300', f'$R_{{tb}}$ = {R_tb:.0f}'),
                   (R_ri, EDG, f'$R_{{ri}}$ = {R_ri}')]:
    t_lbl = theta_hi * 0.85 + theta_lo * 0.15
    ax.text(R * np.cos(t_lbl) + 0.5, R * np.sin(t_lbl) + 1.2,
            txt, fontsize=7.5, color=lc, ha='left')

# Legenda
leg = [mpatches.Patch(fc=IRON,  ec=EDG,      label='Ferro (M250-50A)'),
       mpatches.Patch(fc=ALU,   ec='#1a5580', label='Alumínio (barra)'),
       mpatches.Patch(fc=SHAFT, ec=EDG,       label='Eixo')]
ax.legend(handles=leg, loc='lower right', fontsize=8.5, framealpha=0.95)

# Zoom
ax.set_xlim(R_tb - 10, R_re + 18)
ax.set_ylim(-R_re * np.sin(theta_hi) - 5, R_re * np.sin(theta_hi) + 14)
ax.set_title(f'Detalhe — 4 barras (1–4)  |  perfil trapezoidal semi-fechado',
             fontsize=11.5, color='#111', pad=5)

# ── Quadro com dados do perfil ───────────────────────────────────────────────
info = (f"Perfil da ranhura do rotor\n"
        f"Abertura: {w_r_open} mm\n"
        f"Pescoço:  {h_r_neck} mm\n"
        f"$w_{{top}}$: {w_r_top} mm\n"
        f"$w_{{bot}}$: {w_r_bot} mm\n"
        f"Profund.: {h_r_slot:.0f} mm\n"
        f"$R_{{tb}}$ = {R_tb:.0f} mm")
ax.text(0.01, 0.99, info, transform=ax.transAxes,
        fontsize=8, va='top', ha='left', color='#111',
        bbox=dict(fc='#f5f5f5', ec='#aaa', alpha=0.92, pad=6))

fig.suptitle(
    f'Rotor — Motor de Indução Trifásico  |  $Q_r$ = {Q_r}  |  '
    f'Ranhura trapezoidal semi-fechada (NOVO)',
    fontsize=12, color='#111', y=0.975)

out = '/home/ribb/Área de trabalho/ufmg/trab_femm/rotor_trapez_preview.png'
plt.savefig(out, dpi=160, bbox_inches='tight', facecolor=BG)
print(f'Salvo: {out}')
plt.show()
