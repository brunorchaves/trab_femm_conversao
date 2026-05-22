"""
draw_slots.py — Visualização da geometria das ranhuras do estator.

Dois painéis:
  Esquerda : seção transversal completa (72 ranhuras)
  Direita  : detalhe de 3 ranhuras adjacentes com cotas
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Parâmetros (iguais ao geometry.py) ───────────────────────────────────────
R_se    = 91.4
R_si    = 57.5
Q_s     = 72
w_open  = 2.8
h_neck  = 0.6
h_slot  = 18.5
w_bot   = 5.444   # largura do fundo (especificação do prof.)

_hw      = w_open / 2        # 1.400 mm  (meia-abertura)
_hb      = w_bot  / 2        # 2.722 mm  (meia-largura do fundo do corpo)
_Rn      = R_si + h_neck     # 58.100 mm (fim do pescoço)
_Rb      = R_si + h_slot     # 76.000 mm (fim do corpo reto)
R_bot_arc = 3.885            # mm — raio do arco do fundo (especificação)

BASE = [
    (R_si, +_hw),   # P1 – abertura CCW
    (_Rn,  +_hw),   # P2 – fim pescoço CCW   (Cartesiano y = +1.4 mm)
    (_Rb,  +_hb),   # P3 – fundo corpo CCW   (Cartesiano y = +2.722 mm)
    (_Rb,  -_hb),   # P4 – fundo corpo CW    (Cartesiano y = -2.722 mm)
    (_Rn,  -_hw),   # P5 – fim pescoço CW
    (R_si, -_hw),   # P6 – abertura CW
]

# ── Ângulos dos arcos ─────────────────────────────────────────────────────────
_HALF_DEG  = np.degrees(np.arcsin(_hw / R_si))
_SLOT_ARC  = 2.0 * _HALF_DEG                                  # ≈ 2.788° abertura
_TOOTH_ARC = 360.0 / Q_s - _SLOT_ARC                          # ≈ 2.212° dente
_BOT_ARC   = 2.0 * np.degrees(np.arcsin(_hb / R_bot_arc))     # ≈ 89.0° fundo


# ── Helpers ───────────────────────────────────────────────────────────────────

def rot(pt, theta):
    c, s = np.cos(theta), np.sin(theta)
    return (c * pt[0] - s * pt[1], s * pt[0] + c * pt[1])


def slot_pts(i):
    theta = i * 2.0 * np.pi / Q_s
    return [rot(p, theta) for p in BASE]


def arc_xy(R, a_start, a_end, n=60):
    """Arco CCW de a_start a a_end (rad) no raio R."""
    while a_end < a_start:
        a_end += 2 * np.pi
    t = np.linspace(a_start, a_end, n)
    return R * np.cos(t), R * np.sin(t)


def rounded_bottom_arc(P3, P4, R_arc, n=80):
    """Arco do fundo da ranhura: R_arc curvando para a coroa (afastando do furo).

    Funciona para qualquer orientação da ranhura (slot rotacionado).
    O centro do arco fica DENTRO da ranhura (entre P3/P4 e o furo),
    e o arco bulge para fora (em direção à coroa).
    """
    # Metade da corda (distância do midpoint a P3/P4)
    mx, my = (P3[0] + P4[0]) / 2.0, (P3[1] + P4[1]) / 2.0
    half_chord = np.hypot(P3[0] - mx, P3[1] - my)

    if R_arc <= half_chord + 1e-9:
        return np.array([P3[0], P4[0]]), np.array([P3[1], P4[1]])

    d = np.sqrt(R_arc**2 - half_chord**2)

    # Direção radial do midpoint (para o centro do motor)
    r_m = np.hypot(mx, my)
    # Unidade em direção ao furo (inward)
    ux, uy = -mx / r_m, -my / r_m

    # Centro do arco: afasta do midpoint na direção do FURO (inward)
    # → o arco curva para FORA (coroa)
    cx = mx + d * ux
    cy = my + d * uy

    # Ângulos de P3 e P4 em torno do centro
    a3 = np.arctan2(P3[1] - cy, P3[0] - cx)
    a4 = np.arctan2(P4[1] - cy, P4[0] - cx)

    # Arco CW de P3 → P4 passando pelo ponto mais externo (longe do centro)
    if a4 > a3:
        a4 -= 2 * np.pi
    t = np.linspace(a3, a4, n)
    return cx + R_arc * np.cos(t), cy + R_arc * np.sin(t)


def slot_polygon(i, n_arc=40):
    """Polígono fechado da ranhura i (CCW, excluindo ferro)."""
    P1, P2, P3, P4, P5, P6 = slot_pts(i)

    # Arco de abertura: P6 → P1 (CCW a R_si)
    a6 = np.arctan2(P6[1], P6[0])
    a1 = np.arctan2(P1[1], P1[0])
    bx, by = arc_xy(R_si, a6, a1, n_arc)

    # Arco do fundo: P3 → P4 com raio R3.885 (curvado para a coroa)
    fx, fy = rounded_bottom_arc(P3, P4, R_bot_arc, n=n_arc)

    px = np.concatenate([bx, [P2[0], P3[0]], fx, [P5[0], P6[0]]])
    py = np.concatenate([by, [P2[1], P3[1]], fy, [P5[1], P6[1]]])
    return px, py


def circle_arc(R, a_start, a_end, n=200):
    return arc_xy(R, a_start, a_end, n)


# ── Figura ────────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.5))

# ═══════════════════════════════════════════════════════════════════════════════
# PAINEL ESQUERDO — seção transversal completa
# ═══════════════════════════════════════════════════════════════════════════════
ax = ax1
ax.set_aspect('equal')
ax.set_facecolor('#f0f0f0')

# Ferro do estator (cinza)
stator_patch = plt.Circle((0, 0), R_se, color='#c0c0c0', zorder=1)
ax.add_patch(stator_patch)

# Furo do estator (branco = entreferro + rotor)
bore_patch = plt.Circle((0, 0), R_si, color='white', zorder=2)
ax.add_patch(bore_patch)

# Todas as ranhuras (azul)
for i in range(Q_s):
    px, py = slot_polygon(i, n_arc=15)
    poly = plt.Polygon(list(zip(px, py)), closed=True,
                       facecolor='#3a7ec8', edgecolor='none', alpha=0.85, zorder=3)
    ax.add_patch(poly)

# Círculos de referência
for R, lc, ls, lw, lbl in [
    (R_si, '#0055aa', '--', 0.9, f'R_si = {R_si} mm'),
    (_Rn,  '#008800', ':',  0.8, f'R_nk = {_Rn} mm'),
    (_Rb,  '#cc3300', ':',  0.8, f'R_b  = {_Rb} mm'),
    (R_se, 'black',   '-',  1.2, f'R_se = {R_se} mm'),
]:
    t = np.linspace(0, 2 * np.pi, 500)
    ax.plot(R * np.cos(t), R * np.sin(t), color=lc, ls=ls, lw=lw, label=lbl, zorder=4)

ax.legend(loc='lower right', fontsize=7)
ax.set_xlim(-105, 105)
ax.set_ylim(-105, 105)
ax.set_title(f'Seção transversal completa — {Q_s} ranhuras semifechadas', fontsize=11)
ax.set_xlabel('x (mm)')
ax.set_ylabel('y (mm)')
ax.grid(False)

# ═══════════════════════════════════════════════════════════════════════════════
# PAINEL DIREITO — detalhe de 3 ranhuras (slots 0, 1, 2)
# ═══════════════════════════════════════════════════════════════════════════════
ax = ax2
ax.set_aspect('equal')
ax.set_facecolor('#f8f8f8')

DETAIL_SLOTS = [0, 1, 2]

# Arco de ferro do estator na região de detalhe
a_start = -1 * 2 * np.pi / Q_s
a_end   = (max(DETAIL_SLOTS) + 1.5) * 2 * np.pi / Q_s
cx, cy  = circle_arc(R_se, a_start, a_end)
fx, fy  = circle_arc(R_si, a_end, a_start)    # reverso → fecha o polígono
iron_x  = np.concatenate([cx, fx, [cx[0]]])
iron_y  = np.concatenate([cy, fy, [cy[0]]])
ax.fill(iron_x, iron_y, color='#c8c8c8', zorder=1, label='Ferro (M250-50A)')

# Ranhuras
colors = ['#3a7ec8', '#e07030', '#28a050']
for k, i in enumerate(DETAIL_SLOTS):
    px, py = slot_polygon(i, n_arc=60)
    poly = plt.Polygon(list(zip(px, py)), closed=True,
                       facecolor=colors[k], edgecolor='black', linewidth=0.8,
                       alpha=0.75, zorder=3,
                       label=f'Ranhura {i}' if k < 2 else 'Ranhura 2')
    ax.add_patch(poly)

# Contorno das ranhuras (bordas em preto)
for i in DETAIL_SLOTS:
    px, py = slot_polygon(i, n_arc=60)
    ax.plot(np.append(px, px[0]), np.append(py, py[0]),
            'k-', linewidth=0.7, zorder=5)

# Arcos de referência
for R, lc, ls in [(R_si, '#0055aa', '--'), (_Rn, '#008800', ':'),
                   (_Rb, '#cc3300', ':'), (R_se, 'black', '-')]:
    cx2, cy2 = circle_arc(R, a_start, a_end)
    ax.plot(cx2, cy2, color=lc, ls=ls, lw=0.9, zorder=4)

# ── Cotas para ranhura 0 (slot no eixo +X) ───────────────────────────────────
P1, P2, P3, P4, P5, P6 = slot_pts(0)
ann_kw = dict(fontsize=7.5, ha='center',
              arrowprops=dict(arrowstyle='<->', color='dimgray', lw=0.9))

# w_open — largura da abertura (y-direction at P1,P6)
ax.annotate('', xy=(R_si + 0.3, _hw), xytext=(R_si + 0.3, -_hw),
            arrowprops=dict(arrowstyle='<->', color='#0055aa', lw=1.0))
ax.text(R_si + 1.2, 0, f'w_o={w_open}', fontsize=6.5, color='#0055aa',
        va='center', rotation=90)

# h_neck — profundidade do pescoço
ax.annotate('', xy=(R_si + h_neck / 2, _hw + 0.6),
            xytext=(R_si, _hw + 0.6),
            arrowprops=dict(arrowstyle='<->', color='#008800', lw=1.0))
ax.text((R_si + _Rn) / 2, _hw + 1.4, f'h_n={h_neck}', fontsize=6.5,
        color='#008800', ha='center')

# w_bottom — largura do fundo do corpo reto
ax.annotate('', xy=(_Rb - 0.5, +_hb), xytext=(_Rb - 0.5, -_hb),
            arrowprops=dict(arrowstyle='<->', color='#cc3300', lw=1.0))
ax.text(_Rb - 2.2, 0, f'w_b={w_bot}', fontsize=6.5, color='#cc3300',
        va='center', rotation=90)

# h_slot — profundidade total
ax.annotate('', xy=(_Rb + 0.8, 0), xytext=(R_si, 0),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.0))
ax.text((R_si + _Rb) / 2, -1.5, f'h_s={h_slot} mm', fontsize=6.5,
        color='black', ha='center')

# Rótulos dos pontos P1..P6
for label, pt, offset in [
    ('P1', P1, (+1.5, +0.8)), ('P2', P2, (+1.5, +0.8)),
    ('P3', P3, (+0.5, +1.0)), ('P4', P4, (+0.5, -1.4)),
    ('P5', P5, (+1.5, -1.0)), ('P6', P6, (+1.5, -0.8)),
]:
    ax.plot(*pt, 'ko', markersize=3, zorder=7)
    ax.text(pt[0] + offset[0], pt[1] + offset[1], label,
            fontsize=6.5, color='black', fontweight='bold', zorder=8)

# Zoom na região de 3 ranhuras
margin = 3.0
P0 = slot_pts(0)
Pk = slot_pts(max(DETAIL_SLOTS))
x_all = [p[0] for pts in [slot_pts(i) for i in DETAIL_SLOTS] for p in pts]
y_all = [p[1] for pts in [slot_pts(i) for i in DETAIL_SLOTS] for p in pts]
ax.set_xlim(R_si - margin, R_se + margin)
ax.set_ylim(min(y_all) - margin, max(y_all) + margin)

ax.set_title('Detalhe — 3 ranhuras semiclosed (slots 0–2)', fontsize=11)
ax.set_xlabel('x (mm)')
ax.set_ylabel('y (mm)')
ax.legend(loc='upper right', fontsize=7)

plt.suptitle(
    f'Geometria do estator — Motor de indução trifásico\n'
    f'Q_s={Q_s}, R_si={R_si} mm, R_se={R_se} mm, '
    f'w_open={w_open} mm, h_slot={h_slot} mm, w_bot={w_bot} mm',
    fontsize=9
)

plt.tight_layout(rect=[0, 0, 1, 0.93])
out = '/home/ribb/Área de trabalho/ufmg/trab_femm/slot_geometry.png'
plt.savefig(out, dpi=160, bbox_inches='tight')
print(f'Salvo: {out}')
plt.show()
