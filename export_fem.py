"""
export_fem.py — Gera os 3 arquivos .fem completos (geometria + materiais +
enrolamentos) no diretório do repositório, prontos para abrir e resolver no
FEMM GUI interativamente.

Uso:
  DISPLAY=:1 ~/femm_env/bin/python export_fem.py
"""

import os
import math
import femm
import geometry
import materials

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
FEMM_DIR = '/tmp/femm_work'
os.makedirs(FEMM_DIR, exist_ok=True)

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

femm.openfemm(winepath='/usr/bin/wine',
              femmpath='/home/ribb/.wine/drive_c/femm42/bin/femm.exe')

for label, cfg in CONFIGS.items():
    kw1    = cfg['kw1']
    N_fase = cfg['N_fase']
    config = cfg['config']

    NI_fase = BG1_TGT * G_M * P * math.pi / (6 * MU0 * kw1)
    I_pk = NI_fase / N_fase
    I_A  =  I_pk
    I_B  = -I_pk / 2
    I_C  = -I_pk / 2

    print(f"\nConfig {label}  |  I_pk = {I_pk:.3f} A")

    femm.newdocument(0)
    femm.mi_probdef(0, 'millimeters', 'planar', 1e-8, 140, 30)

    print("  Geometria...")
    geometry.draw_all()

    print("  Materiais e enrolamentos...")
    materials.setup_all(config, N_C, I_A, I_B, I_C, I_pk)

    # Salva em /tmp (ASCII) e depois copia para o repo
    tmp_fem  = os.path.join(FEMM_DIR, f'motor_config_{label}.fem')
    repo_fem = os.path.join(WORK_DIR, f'motor_config_{label}.fem')

    femm.mi_saveas(tmp_fem)

    import shutil
    shutil.copy(tmp_fem, repo_fem)
    print(f"  Salvo: {repo_fem}")

    femm.mi_close()

femm.closefemm()
print("\nPronto! Arquivos .fem salvos no repositório:")
for label in CONFIGS:
    print(f"  motor_config_{label}.fem")
