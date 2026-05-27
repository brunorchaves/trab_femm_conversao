"""
motor_3d.py — Vista 3D em corte do motor de indução trifásico.
Mostra todas as regiões concêntricas com cores e rótulos.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401

# ── Dimensões (mm) ────────────────────────────────────────────────────────────
R_shaft   = 30.0    # raio do eixo (interior)
R_bar_bot = 37.6    # fundo das barras do rotor
R_re      = 57.0    # face externa do rotor
R_si      = 57.5    # furo do estator
R_se      = 91.4    # face externa do estator
L         = 140.0   # comprimento do pacote (mm)
Q_r       = 56      # barras do rotor
Q_s       = 72      # ranhuras do estator
w_r_top   = 2.75    # largura da barra no topo (mm)
w_open    = 2.8     # abertura da ranhura (mm)

BG        = '#0d1117'   # fundo escuro

# ── Helpers de geometria 3D ───────────────────────────────────────────────────

def surf_cyl(ax, R, z0, z1, t0=0, t1=np.pi, nt=80, color='gray', alpha=0.85):
    """Superfície cilíndrica lateral entre ângulos t0..t1."""
    theta = np.linspace(t0, t1, nt)
    z     = np.array([z0, z1])
    T, Z  = np.meshgrid(theta, z)
    ax.plot_surface(R*np.cos(T), R*np.sin(T), Z,
                    color=color, alpha=alpha, linewidth=0, antialiased=True)


def surf_disk(ax, R_in, R_out, z, t0=0, t1=np.pi, nr=18, nt=80,
              color='gray', alpha=0.85):
    """Face anular horizontal em z."""
    r     = np.linspace(R_in, R_out, nr)
    theta = np.linspace(t0, t1, nt)
    T, Rv = np.meshgrid(theta, r)
    Z     = np.full_like(T, z)
    ax.plot_surface(Rv*np.cos(T), Rv*np.sin(T), Z,
                    color=color, alpha=alpha, linewidth=0, antialiased=True)


def surf_flat(ax, R_in, R_out, z0, z1, theta, nr=18,
              color='gray', alpha=0.85):
    """Face plana de corte (retângulo radial em θ fixo)."""
    r     = np.linspace(R_in, R_out, nr)
    z     = np.linspace(z0, z1, 2)
    Rv, Z = np.meshgrid(r, z)
    ax.plot_surface(Rv*np.cos(theta), Rv*np.sin(theta), Z,
                    color=color, alpha=alpha, linewidth=0, antialiased=True)


def shell(ax, R_in, R_out, z0, z1, color, alpha=0.78):
    """Casca cilíndrica completa (meia-volta, corte em θ=0 e θ=π)."""
    surf_cyl (ax, R_out, z0, z1, color=color, alpha=alpha)
    if R_in > 0:
        surf_cyl(ax, R_in,  z0, z1, color=color, alpha=alpha)
    surf_disk(ax, R_in, R_out, z0, color=color, alpha=alpha)
    surf_disk(ax, R_in, R_out, z1, color=color, alpha=alpha)
    surf_flat(ax, R_in, R_out, z0, z1, theta=0,    color=color, alpha=alpha)
    surf_flat(ax, R_in, R_out, z0, z1, theta=np.pi, color=color, alpha=alpha)


# ── Barras do rotor ───────────────────────────────────────────────────────────

def draw_rotor_bars(ax, color='#b8c4ce', alpha=0.92):
    half = np.arcsin(w_r_top / 2 / R_re)
    for n in range(Q_r):
        tc = n * 2 * np.pi / Q_r
        t1 = tc - half
        t2 = tc + half
        # apenas meia-vista visível
        t1c = max(t1, 0)
        t2c = min(t2, np.pi)
        if t2c <= t1c:
            continue
        nt = max(6, int((t2c - t1c) / (2*np.pi/Q_r) * 10))
        # superfície externa e interna da barra
        surf_cyl (ax, R_re,      0, L, t0=t1c, t1=t2c, nt=nt, color=color, alpha=alpha)
        surf_cyl (ax, R_bar_bot, 0, L, t0=t1c, t1=t2c, nt=nt, color=color, alpha=alpha)
        # paredes laterais
        for t_side in [t1c, t2c]:
            surf_flat(ax, R_bar_bot, R_re, 0, L, theta=t_side, color=color, alpha=alpha)
        # faces topo/fundo
        for zf in [0, L]:
            surf_disk(ax, R_bar_bot, R_re, zf, t0=t1c, t1=t2c, nt=nt,
                      color=color, alpha=alpha)


# ── Ranhuras do estator (simplificadas) ───────────────────────────────────────

def draw_stator_slots(ax, color='#d4843e', alpha=0.90):
    half = np.arcsin(w_open / 2 / R_si)
    R_bot_slot = R_si + 19.0   # ≈ fundo das ranhuras
    for n in range(Q_s):
        tc = n * 2 * np.pi / Q_s
        t1 = max(tc - half, 0)
        t2 = min(tc + half, np.pi)
        if t2 <= t1:
            continue
        nt = max(4, int((t2-t1) / (2*np.pi/Q_s) * 8))
        # Paredes da ranhura como faixa fina
        for R_sl in [R_si + 1, R_bot_slot - 1]:
            surf_cyl(ax, R_sl, 0, L, t0=t1, t1=t2, nt=nt,
                     color=color, alpha=alpha)
        for t_side in [t1, t2]:
            surf_flat(ax, R_si + 1, R_bot_slot - 1, 0, L, theta=t_side,
                      color=color, alpha=alpha)
        for zf in [0, L]:
            surf_disk(ax, R_si + 1, R_bot_slot - 1, zf, t0=t1, t1=t2,
                      nt=nt, color=color, alpha=alpha)


# ── Figura principal ──────────────────────────────────────────────────────────

fig = plt.figure(figsize=(15, 9), facecolor=BG)
ax  = fig.add_subplot(111, projection='3d', computed_zorder=False)
ax.set_facecolor(BG)

# ── 1. Eixo (cinza claro — aço no motor real, Air no FEMM) ───────────────────
shell(ax, 0, R_shaft, 0, L, color='#9eaab4', alpha=0.70)

# ── 2. Coroa do rotor (ferro M250-50A) ────────────────────────────────────────
shell(ax, R_shaft, R_bar_bot, 0, L, color='#4a5568', alpha=0.82)

# ── 3. Ferro entre barras (M250-50A) — desenhado primeiro como fundo ──────────
shell(ax, R_bar_bot, R_re, 0, L, color='#3a4455', alpha=0.80)

# ── 4. Barras de alumínio do rotor ────────────────────────────────────────────
draw_rotor_bars(ax)

# ── 5. Entreferro (Air, 0.5 mm) ───────────────────────────────────────────────
shell(ax, R_re, R_si, 0, L, color='#63b3ed', alpha=0.50)

# ── 6. Ferro do estator (M250-50A) — semi-transparente para ver interior ───────
shell(ax, R_si, R_se, 0, L, color='#5a6a7a', alpha=0.38)

# ── 7. Ranhuras com cobre ─────────────────────────────────────────────────────
draw_stator_slots(ax)

# ── Arestas de destaque nos raios críticos ────────────────────────────────────
for R_edge, col in [(R_shaft,   '#9eaab4'),
                    (R_bar_bot, '#6b7a8d'),
                    (R_re,      '#63b3ed'),
                    (R_si,      '#4fc3f7'),
                    (R_se,      '#90a4ae')]:
    t = np.linspace(0, np.pi, 200)
    for zz in [0, L]:
        ax.plot(R_edge*np.cos(t), R_edge*np.sin(t), np.full_like(t, zz),
                color=col, lw=0.8, alpha=0.9)

# ── Rótulos flutuantes (texto 3D) ─────────────────────────────────────────────
labels = [
    # (x, y, z, texto, cor, ha)
    (-R_se-5, R_shaft/2,            L*0.5,  'EIXO\n(aço / Air no FEMM)\nR = 0→30 mm',         '#b0bec5', 'right'),
    (-R_se-5, (R_shaft+R_bar_bot)/2,L*0.6,  'COROA ROTOR\n(ferro M250-50A)\n30→37,6 mm',       '#90a4ae', 'right'),
    (-R_se-5, (R_bar_bot+R_re)/2,   L*0.7,  '56 BARRAS Al\n+ ferro entre barras\n37,6→57 mm',  '#b8c4ce', 'right'),
    ( R_se+5, (R_re+R_si)/2,        L*0.5,  'ENTREFERRO\nAir — 0,5 mm\n57→57,5 mm',            '#63b3ed', 'left'),
    ( R_se+5, (R_si+R_se)/2,        L*0.7,  'ESTATOR\n72 ranhuras (Cobre)\n+ ferro M250-50A\n57,5→91,4 mm', '#d4843e', 'left'),
]
for x0, y0, z0, txt, col, ha in labels:
    # ponto de ancoragem na face de corte
    x_anc = 0
    y_anc = abs(y0) if y0 > 0 else abs(y0)
    ax.plot([x0, x_anc], [y0, y_anc], [z0, z0],
            color=col, lw=0.7, alpha=0.6, linestyle='--')
    ax.text(x0, y0, z0, txt, color=col, fontsize=7.5,
            ha=ha, va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0d1117',
                      edgecolor=col, alpha=0.90, linewidth=0.9))

# ── Seta e rótulo para o comprimento L ───────────────────────────────────────
ax.plot([-R_se-8]*2, [0]*2, [0, L], color='#e2e8f0', lw=1.2)
ax.text(-R_se-12, 0, L/2, 'L = 140 mm', color='#e2e8f0',
        fontsize=8, ha='right', va='center', rotation=90)

# ── Configuração dos eixos ────────────────────────────────────────────────────
ax.set_xlim(-R_se - 30, R_se + 30)
ax.set_ylim(-5, R_se + 10)
ax.set_zlim(-15, L + 30)
ax.set_xlabel('x (mm)', color='#718096', fontsize=8, labelpad=6)
ax.set_ylabel('y (mm)', color='#718096', fontsize=8, labelpad=6)
ax.set_zlabel('z (mm)', color='#718096', fontsize=8, labelpad=6)
ax.tick_params(colors='#718096', labelsize=6)
for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
    pane.fill = False
    pane.set_edgecolor('#2d3748')
ax.grid(False)
ax.view_init(elev=22, azim=-60)

fig.suptitle(
    'Motor de Indução Trifásico — Vista 3D em Corte\n'
    r'P=6, Q$_s$=72, Q$_r$=56, g=0.5 mm, L=140 mm',
    color='#e2e8f0', fontsize=12, y=0.97
)

out = '/home/ribb/Área de trabalho/ufmg/trab_femm/motor_3d.png'
plt.savefig(out, dpi=160, bbox_inches='tight', facecolor=BG)
print(f'Salvo: {out}')
plt.show()
