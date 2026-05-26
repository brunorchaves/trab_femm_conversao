"""
draw_rotor.py — Disco do Rotor (estilo referência).

Perfil da ranhura (lanceta/gota):
  abertura = 0.5 mm   (pescoço estreito no topo)
  corpo    = 2.0 mm   (largura máxima do corpo)
  total    = 15.0 mm  (profundidade total)
  ponta    = R 0.4 mm (raio, diâmetro = 0.8 mm)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches

# ── Parâmetros ────────────────────────────────────────────────────────────────
R_re     = 57.0     # face externa do rotor (mm)
R_ri     = 30.0     # coroa interna
R_shaft  = 21.0     # furo do eixo (φ42 H7)
Q_r      = 56       # número de barras/ranhuras

# Perfil da ranhura
w_open   = 0.5      # largura da abertura (mm)
w_body   = 2.0      # largura máxima do corpo (mm)
h_total  = 15.0     # profundidade total (mm)
R_tip    = 0.4      # raio da ponta (mm)  →  diâmetro = 0.8 mm
h_bridge = 0.5      # altura do pescoço estreito (mm)
h_trans  = 2.0      # transição pescoço→corpo (mm)

R_bar_bot = R_re - h_total   # = 42.0 mm

# Rasgo de chaveta
KW_DEG   = 10.0
KW_DEPTH = 3.5

BG        = '#0c0c12'
IRON      = '#f0ede6'
BAR_CLR   = '#4a9fd4'
BAR_EDGE  = '#1a6090'
BORE_CLR  = '#0c0c12'
DIM       = '#c8d8e8'


# ── Perfil da ranhura (frame base: profundidade=X decrescente, tangencial=Y) ──

def _right_wall_xy():
    """
    Parede direita da ranhura no frame base (slot centrado em +X).
    x = posição radial (decresce de R_re para dentro)
    y = offset tangencial (lado positivo)

    Seções:
      Bridge  : x = R_re → R_re-h_bridge,  y = w_open/2 = 0.25
      Abertura: x decresce mais h_trans,    y abre de 0.25 → w_body/2 = 1.0
      Corpo   : y = 1.0 até perto do fundo
      Afunila : y volta de 1.0 → R_tip = 0.4  (chord da semicircunf. da ponta)
    """
    segs = []

    # 1. Bridge (estreito)
    x0, x1 = R_re, R_re - h_bridge
    n = 4
    segs.append((np.linspace(x0, x1, n), np.full(n, w_open/2)))

    # 2. Transição pescoço → corpo (alarga de 0.25 → 1.0)
    x0, x1 = R_re - h_bridge, R_re - h_bridge - h_trans
    n = 20
    xs = np.linspace(x0, x1, n)
    ys = np.linspace(w_open/2, w_body/2, n)
    segs.append((xs, ys))

    # 3. Corpo largo (2 mm) → afunila gradualmente até a ponta
    x_body_end = R_bar_bot + R_tip    # = 42.4 mm
    x0 = R_re - h_bridge - h_trans   # ≈ 54.5 mm
    n = 60
    xs = np.linspace(x0, x_body_end, n)
    # afunila suavemente de w_body/2 até R_tip (= metade do chord)
    t = np.linspace(0, 1, n)
    # curva cúbica suave: rápida no início, mais acentuada no fim
    ys = w_body/2 * (1 - t**2) + R_tip * t**2
    segs.append((xs, ys))

    xs_all = np.concatenate([s[0] for s in segs])
    ys_all = np.concatenate([s[1] for s in segs])
    return xs_all, ys_all


def bar_polygon(n_bar, n_top=30, n_tip=50):
    """Polígono completo da ranhura n_bar no referencial do motor."""
    theta = n_bar * 2 * np.pi / Q_r
    c, s  = np.cos(theta), np.sin(theta)

    xr, yr = _right_wall_xy()   # parede direita (y > 0)
    xl, yl = xr[::-1], -yr[::-1]   # parede esquerda (y < 0, percorrida de volta)

    # Arco superior ao longo de R_re: de P2 (−w_open/2) a P1 (+w_open/2)
    a2 = np.arcsin( (w_open/2) / R_re)
    t_top = np.linspace(-a2, +a2, n_top)
    top_x = R_re * np.cos(t_top)
    top_y = R_re * np.sin(t_top)

    # Semicircunferência da ponta (centro em (R_bar_bot+R_tip, 0))
    cx_tip = R_bar_bot + R_tip   # = 42.4 mm
    t_tip  = np.linspace(-np.pi/2, -3*np.pi/2, n_tip)   # CW (de +R_tip a -R_tip)
    tip_x  = cx_tip + R_tip * np.cos(t_tip)
    tip_y  =          R_tip * np.sin(t_tip)

    # Montar: arco topo → parede direita → ponta → parede esquerda
    px_b = np.concatenate([top_x, xr, tip_x, xl])
    py_b = np.concatenate([top_y, yr, tip_y, yl])

    # Rotacionar para o ângulo do slot
    px = c * px_b - s * py_b
    py = s * px_b + c * py_b
    return px, py


def keyway_poly(theta_c):
    hw  = np.radians(KW_DEG / 2)
    pts = [(R_shaft * np.cos(t), R_shaft * np.sin(t))
           for t in np.linspace(theta_c - hw, theta_c + hw, 20)]
    R_kw = R_shaft + KW_DEPTH
    pts += [(R_kw * np.cos(theta_c + hw), R_kw * np.sin(theta_c + hw)),
            (R_kw * np.cos(theta_c - hw), R_kw * np.sin(theta_c - hw))]
    return np.array(pts)


# ═══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(13, 10), facecolor=BG)
gs  = GridSpec(1, 2, width_ratios=[2.2, 1], figure=fig,
               left=0.02, right=0.97, bottom=0.09, top=0.92, wspace=0.04)

# ── PAINEL ESQUERDO: disco completo ──────────────────────────────────────────
ax = fig.add_subplot(gs[0])
ax.set_aspect('equal')
ax.set_facecolor(BG)
ax.axis('off')

# Disco de ferro (branco/creme)
ax.add_patch(plt.Circle((0, 0), R_re,    color=IRON,     zorder=1))
# Coroa interna
ax.add_patch(plt.Circle((0, 0), R_ri,    color=IRON,     zorder=3))
# Furo do eixo
ax.add_patch(plt.Circle((0, 0), R_shaft, color=BORE_CLR, zorder=4))

# Rasgos de chaveta
for theta_kw in [0, np.pi]:
    ax.add_patch(plt.Polygon(keyway_poly(theta_kw), closed=True,
                             facecolor=BORE_CLR, edgecolor='#333355',
                             linewidth=0.5, zorder=5))

# Mira no furo
for ang in np.linspace(0, 2*np.pi, 5)[:-1]:
    r0, r1 = R_shaft - 3, R_shaft + 3
    ax.plot([r0*np.cos(ang), r1*np.cos(ang)],
            [r0*np.sin(ang), r1*np.sin(ang)],
            color='#888', lw=0.6, zorder=6)

# Barras (ranhuras) — desenhadas sobre o ferro branco
for n in range(Q_r):
    px, py = bar_polygon(n)
    ax.add_patch(plt.Polygon(list(zip(px, py)), closed=True,
                              facecolor=BAR_CLR, edgecolor=BAR_EDGE,
                              linewidth=0.5, alpha=0.93, zorder=2))

# Cota Ø
y_dim = -R_re - 6
ax.annotate('', xy=(-R_re, y_dim), xytext=(R_re, y_dim),
            arrowprops=dict(arrowstyle='<->', color=DIM, lw=1.1))
ax.text(0, y_dim - 3, f'Ø {2*R_re:.0f} mm',
        color=DIM, fontsize=10.5, ha='center', va='top')

ax.set_xlim(-R_re - 12, R_re + 12)
ax.set_ylim(-R_re - 15, R_re + 8)
ax.text(0, -R_re - 13, f'Disco do Rotor (Q_r={Q_r})\n{Q_r} ranhuras — passo angular {360/Q_r:.2f}°',
        color=DIM, fontsize=11, ha='center', va='top', fontweight='bold')

# ── PAINEL DIREITO: perfil da ranhura (em pé, escala ampliada) ───────────────
ax2 = fig.add_subplot(gs[1])
ax2.set_aspect('equal')
ax2.set_facecolor('#14141e')
ax2.axis('off')

# Reconstrói o perfil "em pé"
# y=0 = topo (abertura), y=h_total = fundo
# x = metade da largura (lado direito)

h_br = h_bridge
h_tr = h_trans
h_body_h = h_total - h_br - h_tr - R_tip

n_s  = 80
# Seção 1: bridge
y_br = np.linspace(0, h_br, 5)
x_br = np.full_like(y_br, w_open / 2)
# Seção 2: transição (alarga)
y_op = np.linspace(h_br, h_br + h_tr, 20)
x_op = np.linspace(w_open/2, w_body/2, 20)
# Seção 3: corpo afunila até R_tip
y_bo = np.linspace(h_br + h_tr, h_total - R_tip, n_s)
t    = np.linspace(0, 1, n_s)
x_bo = w_body/2 * (1 - t**2) + R_tip * t**2
# Seção 4: semicircunferência (ponta)
cy_tip = h_total - R_tip
t_arc  = np.linspace(np.pi/2, -np.pi/2, 40)
y_arc  = cy_tip + R_tip * np.sin(t_arc)
x_arc  = R_tip  * np.cos(t_arc)

# Lado direito (top → bottom)
yr = np.concatenate([y_br, y_op[1:], y_bo[1:], y_arc])
xr = np.concatenate([x_br, x_op[1:], x_bo[1:], x_arc])

# Polígono completo do perfil
px_p = np.concatenate([xr, -xr[::-1]])
py_p = np.concatenate([yr,  yr[::-1]])

ax2.add_patch(plt.Polygon(list(zip(px_p, py_p)), closed=True,
                           facecolor=BAR_CLR, edgecolor=BAR_EDGE,
                           linewidth=1.0, alpha=0.93))

# ── Cotas ────────────────────────────────────────────────────────────────────
MX = 3.5   # margem lateral

# Abertura (topo)
ax2.annotate('', xy=(-w_open/2, -1.2), xytext=(w_open/2, -1.2),
             arrowprops=dict(arrowstyle='<->', color=DIM, lw=1.0))
ax2.text(0, -2.3, f'{w_open} mm', color=DIM, fontsize=9, ha='center')

# Corpo (largura máxima) — lado esquerdo
y_wmax = h_br + h_tr
ax2.annotate('', xy=(-MX, y_wmax), xytext=(-MX + 0, y_wmax),
             arrowprops=None)
ax2.annotate('', xy=(-w_body/2, y_wmax + 0.3), xytext=(w_body/2, y_wmax + 0.3),
             arrowprops=dict(arrowstyle='<->', color='#88ccee', lw=1.0))
ax2.text(0, y_wmax + 1.5, f'{w_body} mm', color='#88ccee', fontsize=9, ha='center')

# Altura total — lado direito
ax2.annotate('', xy=(MX, 0), xytext=(MX, h_total),
             arrowprops=dict(arrowstyle='<->', color=DIM, lw=1.0))
ax2.text(MX + 0.7, h_total/2, f'{h_total:.1f} mm',
         color=DIM, fontsize=9, ha='left', va='center')

# Altura do pescoço — lado esquerdo
ax2.annotate('', xy=(-MX, 0), xytext=(-MX, h_br + h_tr),
             arrowprops=dict(arrowstyle='<->', color='#aabbcc', lw=0.9))
ax2.text(-MX - 0.7, (h_br + h_tr)/2, f'{h_br + h_tr:.1f}',
         color='#aabbcc', fontsize=8.5, ha='right', va='center')

# R da ponta
ax2.text(R_tip + 0.4, h_total - 0.5, f'R{R_tip}',
         color=DIM, fontsize=8.5, ha='left')

# Diâmetro da ponta (0.8mm)
ax2.annotate('', xy=(-R_tip, h_total + 1.0), xytext=(R_tip, h_total + 1.0),
             arrowprops=dict(arrowstyle='<->', color=DIM, lw=0.9))
ax2.text(0, h_total + 2.0, f'{2*R_tip:.1f}', color=DIM, fontsize=8.5, ha='center')

# Linhas-guia tracejadas
for y_g, x_side in [(0, w_open/2), (h_total, R_tip), (y_wmax, w_body/2)]:
    ax2.plot([x_side, MX + 0.1],  [y_g, y_g], color='#334455', lw=0.5, ls='--')
    ax2.plot([-x_side, -MX - 0.1], [y_g, y_g], color='#334455', lw=0.5, ls='--')

ax2.set_xlim(-MX - 2.5, MX + 3.5)
ax2.set_ylim(-4, h_total + 5)
ax2.invert_yaxis()   # topo da ranhura fica em cima

# Título inset + borda
ax2.text(0, -3.5, 'Perfil da ranhura\nCotas em mm — escala ampliada',
         color=DIM, fontsize=9, ha='center', va='bottom', style='italic')
ax2.add_patch(plt.Rectangle(
    (-MX - 2, h_total + 4.5), (MX + 2.5) * 2, -(h_total + 9.5),
    fill=False, edgecolor='#445566', lw=1.0, linestyle='--',
    transform=ax2.transData))

# ── Título geral ──────────────────────────────────────────────────────────────
fig.text(0.5, 0.97, 'Disco do Rotor — Motor de Indução Trifásico',
         color=DIM, fontsize=13, ha='center', va='top', fontweight='bold')
fig.text(0.5, 0.93, f'Q_r = {Q_r} ranhuras  |  Ø_ext = {2*R_re:.0f} mm  |  '
         f'Ø_eixo = {2*R_shaft:.0f} mm H7  |  passo = {360/Q_r:.2f}°',
         color='#8899aa', fontsize=9, ha='center', va='top')

out = '/home/ribb/Área de trabalho/ufmg/trab_femm/rotor_geometry.png'
plt.savefig(out, dpi=160, bbox_inches='tight', facecolor=BG)
print(f'Salvo: {out}')
plt.show()
