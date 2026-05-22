"""
visualize.py — Solve each config and immediately save FEMM field image.

Strategy: full solve cycle (same as main.py), but right after mi_loadsolution()
save the density + contour bitmap before doing anything else.
"""

import os, math
import femm
import geometry
import materials

FEMM_DIR = '/tmp/femm_work'
OUT_DIR  = '/home/ribb/Área de trabalho/ufmg/trab_femm'

MU0     = 4 * math.pi * 1e-7
BG1_TGT = 0.9
G_M     = 0.5e-3
P       = 6
N_C     = 10

CONFIGS = {
    'I':   {'config': 1, 'kw1': 0.9577, 'N_fase': 12 * N_C},
    'II':  {'config': 2, 'kw1': 0.9577, 'N_fase': 24 * N_C},
    'III': {'config': 3, 'kw1': 0.9250, 'N_fase': 24 * N_C},
}


def _Ipk(kw1, N_fase):
    return (BG1_TGT * G_M * P * math.pi) / (6 * MU0 * kw1) / N_fase


def solve_and_capture(label, params):
    config = params['config']
    I_pk   = _Ipk(params['kw1'], params['N_fase'])
    I_A, I_B, I_C = I_pk, -I_pk / 2, -I_pk / 2

    femfile = os.path.join(FEMM_DIR, f'motor_config_{label}.fem')
    bmpfile = os.path.join(FEMM_DIR, f'motor_field_{label}.bmp')
    pngfile = os.path.join(OUT_DIR,  f'motor_field_{label}.png')

    # ── Build model ───────────────────────────────────────────
    femm.newdocument(0)
    femm.mi_probdef(0, 'millimeters', 'planar', 1e-8, 140, 30)
    geometry.draw_all()
    materials.setup_all(config, N_C, I_A, I_B, I_C, I_pk)
    femm.mi_saveas(femfile)

    # ── Solve ─────────────────────────────────────────────────
    print(f"  Resolvendo...")
    femm.mi_createmesh()
    femm.mi_analyze(1)
    femm.mi_loadsolution()   # opens FEMMVIEW with solution loaded

    # ── Render and capture ────────────────────────────────────
    # Zoom tight to the motor (stator outer = 91.4 mm)
    femm.mo_zoom(-96, -96, 96, 96)

    # |B| colormap (0–2 T) — use callfemm to avoid pyFEMM string bug
    femm.callfemm('mo_showdensityplot(1,0,0,2,2)')

    # Flux-tube lines (equipotentials of A_z)
    femm.callfemm('mo_showcontourplot(25)')

    # Save bitmap  (path sent as WINE Z: path)
    wine_bmp = 'Z:' + bmpfile.replace('/', '\\')
    femm.callfemm(f'mo_savebitmap("{wine_bmp}")')

    femm.mo_close()

    # ── Convert BMP → PNG ─────────────────────────────────────
    if os.path.exists(bmpfile):
        from PIL import Image
        Image.open(bmpfile).save(pngfile)
        os.remove(bmpfile)
        print(f"  Salvo: {pngfile}")
    else:
        print(f"  AVISO: bitmap não encontrado em {bmpfile}")


def main():
    femm.openfemm(winepath='/usr/bin/wine',
                  femmpath='/home/ribb/.wine/drive_c/femm42/bin/femm.exe')

    for label, params in CONFIGS.items():
        print(f"\nConfig {label}...")
        solve_and_capture(label, params)

    femm.closefemm()
    print("\nConcluído.")


if __name__ == '__main__':
    main()
