"""
field_plot.py — Renderiza |B| em 2D abrindo a solução FEMM e
extraindo mo_getb em grade regular. Sem depender do bitmap do Wine.

Gera: motor_field_color_I.png, _II.png, _III.png
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import math
import femm
import os

FEMM_DIR = '/tmp/femm_work'
OUT_DIR  = '/home/ribb/Área de trabalho/ufmg/trab_femm'

# Configurações de grid
N       = 160          # pontos por eixo  (160×160 ≈ 25 600 pontos)
R_OUTER = 92.0         # limite de plot
R_SHAFT = 29.5         # descarta dentro do eixo

CONFIGS = {
    'I':   {'scale': 2.1758},
    'II':  {'scale': 2.1758},
    'III': {'scale': 2.1655},
}

CIRCLES = {          # raio (mm)  : (cor, espessura, rótulo)
    91.4 : ('#333333', 1.2, ''),          # face ext estator
    57.5 : ('#555555', 0.8, ''),          # furo estator
    57.0 : ('#555555', 0.8, ''),          # face ext rotor
    37.6 : ('#888888', 0.6, ''),          # fundo barras rotor
    30.0 : ('#aaaaaa', 0.6, ''),          # eixo
}


def draw_circles(ax):
    t = np.linspace(0, 2 * np.pi, 500)
    for R, (col, lw, _) in CIRCLES.items():
        ax.plot(R * np.cos(t), R * np.sin(t), color=col, lw=lw, zorder=5)


def render_config(label, scale):
    outfile = os.path.join(OUT_DIR,  f'motor_field_color_{label}.png')
    ansfile = os.path.join(FEMM_DIR, f'motor_config_{label}.ans')
    if not os.path.exists(ansfile):
        print(f'  AVISO: {ansfile} não encontrado — pulando Config {label}')
        return

    print(f'  Carregando solução Config {label}...')
    # Abre o .ans diretamente no modo pós-processamento
    femm.opendocument(ansfile)

    # ── Grade de amostragem ───────────────────────────────────────────────
    xs = np.linspace(-R_OUTER, R_OUTER, N)
    ys = np.linspace(-R_OUTER, R_OUTER, N)
    Bmod = np.full((N, N), np.nan)

    for j, x in enumerate(xs):
        for i, y in enumerate(ys):
            r = math.hypot(x, y)
            if R_SHAFT < r < R_OUTER:
                try:
                    bx, by = femm.mo_getb(x, y)
                    Bmod[i, j] = math.hypot(bx, by) * scale
                except Exception:
                    pass

    femm.mo_close()

    # ── Plot ──────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect('equal')
    ax.set_facecolor('#111111')

    cmap  = plt.cm.inferno
    vmax  = 2.2
    im = ax.pcolormesh(xs, ys, Bmod,
                       cmap=cmap, vmin=0, vmax=vmax,
                       shading='auto', zorder=1)

    cb = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label('|B| (T)', fontsize=10)
    cb.ax.tick_params(labelsize=8)

    draw_circles(ax)

    ax.set_xlim(-R_OUTER, R_OUTER)
    ax.set_ylim(-R_OUTER, R_OUTER)
    ax.set_xlabel('x (mm)', fontsize=9)
    ax.set_ylabel('y (mm)', fontsize=9)
    ax.set_title(f'Campo magnético |B| — Config {label}  (normalizado $B_{{g,1}}=0.9$ T)',
                 fontsize=10)
    ax.tick_params(labelsize=8)

    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  Salvo: {outfile}')


def main():
    femm.openfemm(winepath='/usr/bin/wine',
                  femmpath='/home/ribb/.wine/drive_c/femm42/bin/femm.exe')

    for label, params in CONFIGS.items():
        print(f'\nConfig {label}...')
        render_config(label, params['scale'])

    femm.closefemm()
    print('\nConcluído.')


if __name__ == '__main__':
    main()
