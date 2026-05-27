"""
Rotor de máquina de indução — 52 ranhuras
Baseado no desenho original (Fig. 1) de rotor de 28 ranhuras, Ø115 mm.
Mantém o formato da ranhura escalando uniformemente para caber 52 ranhuras.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Diretório do script (saídas vão aqui)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# PARÂMETROS — edite aqui para mudar o rotor
# ============================================================

# --- Geometria global do rotor ---
D_outer = 115.0          # diâmetro externo [mm] — mantido do original
R_outer = D_outer / 2

# --- Contagem de ranhuras ---
N_slots_orig = 28        # ranhuras do desenho original
N_slots = 52             # ranhuras desejadas para o novo rotor

# --- Dimensões originais da ranhura (do desenho técnico, em mm) ---
w_open_orig = 0.600      # largura da abertura (no entreferro)
w_top_orig  = 6.198      # largura no topo do trapézio
w_bot_orig  = 2.031      # largura na base (= diâmetro do arredondamento inferior)
y_bot_orig  = 22.000     # profundidade radial total
y_trap_orig = 19.400     # profundidade da seção trapezoidal
# O flare de 40° (medido da horizontal) consome ~2.6 mm radialmente, casando
# com (22 - 19.4) e levando a largura de 0.600 → 6.198.

# --- Fator de escala uniforme (mantém o formato/proporções) ---
scale = N_slots_orig / N_slots

w_open = w_open_orig * scale
w_top  = w_top_orig  * scale
w_bot  = w_bot_orig  * scale
y_bot  = y_bot_orig  * scale
y_top  = (y_bot_orig - y_trap_orig) * scale   # profundidade onde o flare termina

# ============================================================
# CONSTRUÇÃO DE UMA RANHURA
# ============================================================

def slot_polygon(angle_rad, R_outer, w_open, w_top, w_bot, y_top, y_bot, n_round=40):
    """
    Retorna os pontos (em coords mundiais) de uma ranhura posicionada
    com o eixo radial apontando para `angle_rad` (medido do eixo +x).
    Coords locais: +y = radial para fora, +x = tangencial.
    """
    pts = []
    r_bot = w_bot / 2
    y_arc_center = R_outer - y_bot + r_bot   # centro do semicírculo do fundo

    # --- Contorno em coords locais (slot orientada com abertura em +y) ---
    # Lado direito da abertura (no entreferro)
    pts.append(( w_open/2, R_outer))
    # Topo do trapézio (após flare de 40°)
    pts.append(( w_top/2,  R_outer - y_top))
    # Início do arco inferior (lado direito)
    pts.append(( w_bot/2,  y_arc_center))
    # Arco inferior (semicírculo de raio w_bot/2)
    for i in range(1, n_round):
        theta = np.pi * i / n_round
        pts.append((r_bot * np.cos(theta), y_arc_center - r_bot * np.sin(theta)))
    # Fim do arco (lado esquerdo)
    pts.append((-w_bot/2,  y_arc_center))
    # Topo do trapézio (esquerda)
    pts.append((-w_top/2,  R_outer - y_top))
    # Lado esquerdo da abertura
    pts.append((-w_open/2, R_outer))

    # --- Rotação para o ângulo desejado ---
    # Local +y → direção radial em `angle_rad`. Isso é uma rotação de (angle - pi/2).
    rot = angle_rad - np.pi/2
    c, s = np.cos(rot), np.sin(rot)
    return [(x*c - y*s, x*s + y*c) for x, y in pts]


# ============================================================
# FURO CENTRAL — bore Ø42 H7 com 2 rasgos de chaveta a 180°
# ============================================================
# Conforme detalhe do desenho original:
#   Ø42 H7   → R_bore = 21 mm
#   2x10 H7  → rasgos de 10 mm de largura tangencial (hw = 5 mm)
#   50.34    → diâmetro de pico-a-pico dos rasgos (R_kw_outer = 25.17 mm)
#   R1       → raio do filete nos cantos rasgo-bore

R_bore       = 21.00    # raio do furo central [mm]
kw_half_width = 5.00    # meia-largura tangencial do rasgo (10 mm total)
R_kw_outer   = 25.17    # extremo radial externo do rasgo (50.34/2)
r_fillet     = 1.00     # raio do filete R1

def shaft_hole_with_keyways(R_bore, hw, R_kw_outer, r_fill,
                             n_arc=240, n_fillet=15):
    """
    Furo central com dois rasgos de chaveta a 180° (no topo e na base),
    com filetes de raio `r_fill` nos quatro cantos rasgo-bore.

    Polígono é construído percorrendo o contorno no sentido CCW (anti-horário).
    """
    # Centro do círculo do filete (para canto superior-direito TR):
    # - deslocado de `hw + r_fill` em x (lado tangencial, no metal)
    # - deslocado de y_C em y (no metal abaixo do rasgo superior)
    # Restrição: distância ao centro do bore = R_bore + r_fill (filete tangencia bore externamente)
    y_C = np.sqrt((R_bore + r_fill) ** 2 - (hw + r_fill) ** 2)

    # Razão para projetar centro do filete sobre o bore (ponto de tangência)
    s = R_bore / (R_bore + r_fill)

    # Pontos de tangência em cada canto:
    tb_TR = ( s * (hw + r_fill),  s * y_C)
    tb_TL = (-s * (hw + r_fill),  s * y_C)
    tb_BR = ( s * (hw + r_fill), -s * y_C)
    tb_BL = (-s * (hw + r_fill), -s * y_C)
    tk_TR = ( hw,  y_C)
    tk_TL = (-hw,  y_C)
    tk_BR = ( hw, -y_C)
    tk_BL = (-hw, -y_C)

    # Centros dos filetes
    C_TR = ( hw + r_fill,  y_C)
    C_TL = (-(hw + r_fill),  y_C)
    C_BR = ( hw + r_fill, -y_C)
    C_BL = (-(hw + r_fill), -y_C)

    # Ângulos dos pontos de tangência sobre o bore (do centro do bore)
    ang_TR = np.arctan2(tb_TR[1], tb_TR[0])
    ang_TL = np.arctan2(tb_TL[1], tb_TL[0])
    ang_BR = np.arctan2(tb_BR[1], tb_BR[0])
    ang_BL = np.arctan2(tb_BL[1], tb_BL[0])

    def fillet_arc(C, p_start, p_end, r, n):
        """Arco do filete: do ponto p_start ao p_end, sentido CW em volta de C."""
        a0 = np.arctan2(p_start[1] - C[1], p_start[0] - C[0])
        a1 = np.arctan2(p_end[1]   - C[1], p_end[0]   - C[0])
        # Sentido CW (a0 > a1)
        if a0 < a1:
            a0 += 2 * np.pi
        return [(C[0] + r * np.cos(t), C[1] + r * np.sin(t))
                for t in np.linspace(a0, a1, n)]

    pts = []

    # --- Arco 1: bore de (R_bore, 0) CCW até tangente TR ---
    for t in np.linspace(0, ang_TR, n_arc // 4):
        pts.append((R_bore * np.cos(t), R_bore * np.sin(t)))

    # --- Filete TR: tb_TR → tk_TR ---
    pts += fillet_arc(C_TR, tb_TR, tk_TR, r_fill, n_fillet)

    # --- Rasgo superior: direita, topo, esquerda ---
    pts.append(( hw,  R_kw_outer))
    pts.append((-hw,  R_kw_outer))

    # --- Filete TL: tk_TL → tb_TL ---
    pts += fillet_arc(C_TL, tk_TL, tb_TL, r_fill, n_fillet)

    # --- Arco 2: bore de tangente TL CCW até tangente BL (passando por (-R,0)) ---
    ang_BL_ccw = ang_BL + 2 * np.pi if ang_BL < ang_TL else ang_BL
    for t in np.linspace(ang_TL, ang_BL_ccw, n_arc // 2):
        pts.append((R_bore * np.cos(t), R_bore * np.sin(t)))

    # --- Filete BL: tb_BL → tk_BL ---
    pts += fillet_arc(C_BL, tb_BL, tk_BL, r_fill, n_fillet)

    # --- Rasgo inferior: esquerda, base, direita ---
    pts.append((-hw, -R_kw_outer))
    pts.append(( hw, -R_kw_outer))

    # --- Filete BR: tk_BR → tb_BR ---
    pts += fillet_arc(C_BR, tk_BR, tb_BR, r_fill, n_fillet)

    # --- Arco 3: bore de tangente BR CCW até (R_bore, 0) ---
    for t in np.linspace(ang_BR, 0, n_arc // 4):
        pts.append((R_bore * np.cos(t), R_bore * np.sin(t)))

    return pts


# ============================================================
# PLOT
# ============================================================

fig, ax = plt.subplots(1, 1, figsize=(11, 11))

# Cor de "ferro" para o corpo do rotor
iron_color = "#c9d1d9"

# Corpo do rotor (disco preenchido)
theta = np.linspace(0, 2*np.pi, 400)
rotor_body = Polygon(list(zip(R_outer*np.cos(theta), R_outer*np.sin(theta))),
                     closed=True, facecolor=iron_color, edgecolor='black',
                     linewidth=1.5, zorder=1)
ax.add_patch(rotor_body)

# Ranhuras (recortadas — desenhadas em branco sobre o corpo)
slot_polys = []
for i in range(N_slots):
    angle = np.pi/2 + 2*np.pi * i / N_slots    # começa no topo
    pts = slot_polygon(angle, R_outer, w_open, w_top, w_bot, y_top, y_bot)
    poly = Polygon(pts, closed=True, facecolor='white', edgecolor='black',
                   linewidth=0.6, zorder=2)
    ax.add_patch(poly)
    slot_polys.append(pts)

# Furo central com 2 rasgos de chaveta + filetes R1
shaft_pts = shaft_hole_with_keyways(R_bore, kw_half_width, R_kw_outer, r_fillet)
shaft_poly = Polygon(shaft_pts, closed=True, facecolor='white',
                     edgecolor='black', linewidth=1.2, zorder=3)
ax.add_patch(shaft_poly)

# Linhas de referência (eixos)
ax.axhline(0, color='gray', linewidth=0.4, linestyle='--', alpha=0.5, zorder=0)
ax.axvline(0, color='gray', linewidth=0.4, linestyle='--', alpha=0.5, zorder=0)

# Formatação
ax.set_aspect('equal')
margin = R_outer * 0.15
ax.set_xlim(-R_outer - margin, R_outer + margin)
ax.set_ylim(-R_outer - margin, R_outer + margin)
ax.set_title(f'Rotor — {N_slots} ranhuras (Ø{D_outer:.0f} mm)\n'
             f'Formato da ranhura preservado (escala uniforme = {scale:.3f})',
             fontsize=13)
ax.set_xlabel('x [mm]')
ax.set_ylabel('y [mm]')
ax.grid(True, alpha=0.25)

# Box com dimensões
info = (
    f"GEOMETRIA DO ROTOR\n"
    f"───────────────────\n"
    f"Ø externo:        {D_outer:.2f} mm\n"
    f"Nº ranhuras:      {N_slots}\n"
    f"Passo angular:    {360/N_slots:.4f}°\n"
    f"\n"
    f"RANHURA ESCALADA\n"
    f"───────────────────\n"
    f"Abertura:         {w_open:.3f} mm\n"
    f"Topo do trapézio: {w_top:.3f} mm\n"
    f"Base (Ø arco):    {w_bot:.3f} mm\n"
    f"Profundidade:     {y_bot:.3f} mm\n"
    f"\n"
    f"FURO CENTRAL\n"
    f"───────────────────\n"
    f"Ø bore:           {2*R_bore:.2f} mm H7\n"
    f"Rasgos:           2 × {2*kw_half_width:.1f} mm @ 180°\n"
    f"Ø sobre rasgos:   {2*R_kw_outer:.2f} mm\n"
    f"Filetes:          R{r_fillet:.1f}\n"
)
ax.text(0.02, 0.02, info, transform=ax.transAxes, fontsize=8.5,
        family='monospace', verticalalignment='bottom',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                  edgecolor='gray', alpha=0.92))

plt.tight_layout()

# Salvar
out_png = os.path.join(SCRIPT_DIR, 'rotor_52_ranhuras.png')
plt.savefig(out_png, dpi=160, bbox_inches='tight')
print(f"Plot salvo em: {out_png}")

# ============================================================
# Plot extra: detalhe de uma ranhura
# ============================================================
fig2, ax2 = plt.subplots(1, 1, figsize=(6, 9))
pts_single = slot_polygon(np.pi/2, R_outer, w_open, w_top, w_bot, y_top, y_bot)
poly_single = Polygon(pts_single, closed=True, facecolor='#e0e7ee',
                      edgecolor='black', linewidth=1.2)
ax2.add_patch(poly_single)
# desenhar linha do entreferro (arco da superfície externa) por cima
arc_x = R_outer * np.cos(np.linspace(np.pi/2 - 0.05, np.pi/2 + 0.05, 50))
arc_y = R_outer * np.sin(np.linspace(np.pi/2 - 0.05, np.pi/2 + 0.05, 50))
ax2.plot(arc_x, arc_y, 'k-', linewidth=1.5)

ax2.set_aspect('equal')
ax2.set_xlim(-w_top, w_top)
ax2.set_ylim(R_outer - y_bot - 1, R_outer + 1)
ax2.set_title(f'Detalhe da ranhura (escala {scale:.3f})\n'
              f'{w_open:.3f} / {w_top:.3f} / {w_bot:.3f} mm  •  {y_bot:.3f} mm de profundidade',
              fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_xlabel('tangencial [mm]')
ax2.set_ylabel('radial [mm]')

# Anotações de dimensões
ax2.annotate('', xy=(-w_open/2, R_outer+0.3), xytext=(w_open/2, R_outer+0.3),
             arrowprops=dict(arrowstyle='<->', color='red'))
ax2.text(0, R_outer+0.5, f'{w_open:.3f}', ha='center', color='red', fontsize=9)

ax2.annotate('', xy=(-w_top/2, R_outer - y_top), xytext=(w_top/2, R_outer - y_top),
             arrowprops=dict(arrowstyle='<->', color='red'))
ax2.text(0, R_outer - y_top + 0.15, f'{w_top:.3f}', ha='center', color='red', fontsize=9)

ax2.annotate('', xy=(w_top/2 + 0.4, R_outer), xytext=(w_top/2 + 0.4, R_outer - y_bot),
             arrowprops=dict(arrowstyle='<->', color='blue'))
ax2.text(w_top/2 + 0.55, R_outer - y_bot/2, f'{y_bot:.3f}',
         color='blue', fontsize=9, rotation=90, va='center')

plt.tight_layout()
out_png2 = os.path.join(SCRIPT_DIR, 'rotor_52_detalhe_ranhura.png')
plt.savefig(out_png2, dpi=160, bbox_inches='tight')
print(f"Detalhe salvo em: {out_png2}")

plt.show()

# ============================================================
# Plot extra: detalhe do furo central
# ============================================================
fig3, ax3 = plt.subplots(1, 1, figsize=(7, 7))
poly_hole = Polygon(shaft_pts, closed=True, facecolor='white',
                    edgecolor='black', linewidth=1.5)
# Fundo metálico
bg_R = R_kw_outer + 8
ax3.add_patch(plt.Circle((0, 0), bg_R, facecolor=iron_color,
                          edgecolor='none', zorder=0))
ax3.add_patch(poly_hole)

# Cotas
# Ø42 (horizontal através do centro, fora dos rasgos)
ax3.annotate('', xy=(-R_bore, 0), xytext=(R_bore, 0),
             arrowprops=dict(arrowstyle='<->', color='red', lw=1.2))
ax3.text(0, 1.2, f'Ø{2*R_bore:.0f} H7', ha='center', color='red',
         fontsize=11, fontweight='bold')

# 50.34 (vertical, ponta-a-ponta dos rasgos)
ax3.annotate('', xy=(0, -R_kw_outer), xytext=(0, R_kw_outer),
             arrowprops=dict(arrowstyle='<->', color='blue', lw=1.2))
ax3.text(-1.0, 0, f'{2*R_kw_outer:.2f}', ha='right', va='center',
         color='blue', fontsize=11, fontweight='bold', rotation=90)

# Largura do rasgo (10)
ax3.annotate('', xy=(-kw_half_width, R_kw_outer + 2),
             xytext=(kw_half_width, R_kw_outer + 2),
             arrowprops=dict(arrowstyle='<->', color='darkgreen', lw=1.2))
ax3.text(0, R_kw_outer + 2.7, f'{2*kw_half_width:.0f} H7',
         ha='center', color='darkgreen', fontsize=10, fontweight='bold')

# R1 (indicador de filete)
ax3.annotate('R1', xy=(kw_half_width + r_fillet*0.3, np.sqrt((R_bore+r_fillet)**2 - (kw_half_width+r_fillet)**2) - r_fillet*0.3),
             xytext=(kw_half_width + 5, np.sqrt((R_bore+r_fillet)**2 - (kw_half_width+r_fillet)**2) - 2),
             arrowprops=dict(arrowstyle='->', color='purple', lw=1),
             fontsize=10, fontweight='bold', color='purple')

ax3.set_aspect('equal')
ax3.set_xlim(-bg_R, bg_R)
ax3.set_ylim(-bg_R, bg_R)
ax3.set_title('Detalhe do furo central\nØ42 H7 + 2 rasgos 10 H7 @ 180° + filetes R1',
              fontsize=11)
ax3.grid(True, alpha=0.25)
ax3.set_xlabel('x [mm]')
ax3.set_ylabel('y [mm]')

plt.tight_layout()
plt.savefig(os.path.join(SCRIPT_DIR, 'rotor_52_detalhe_furo.png'), dpi=160, bbox_inches='tight')
print("Detalhe do furo salvo em: ./rotor_52_detalhe_furo.png")