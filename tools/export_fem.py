"""
export_fem.py — Gera os 3 arquivos .fem completos (geometria + materiais +
enrolamentos) em models/, prontos para abrir e resolver no FEMM GUI.

Uso:
  DISPLAY=:1 ~/femm_env/bin/python tools/export_fem.py
"""

import os, sys, shutil, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import femm
import geometry
import materials

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT, 'models')
FEMM_DIR  = '/tmp/femm_work'
os.makedirs(FEMM_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

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
    NI_fase = BG1_TGT * G_M * P * math.pi / (6 * MU0 * cfg['kw1'])
    I_pk = NI_fase / cfg['N_fase']

    print(f"\nConfig {label}  |  I_pk = {I_pk:.3f} A")

    femm.newdocument(0)
    femm.mi_probdef(0, 'millimeters', 'planar', 1e-8, 140, 30)

    print("  Geometria...")
    geometry.draw_all()

    print("  Materiais e enrolamentos...")
    materials.setup_all(cfg['config'], N_C, I_pk, -I_pk/2, -I_pk/2, I_pk)

    tmp_fem   = os.path.join(FEMM_DIR,   f'motor_config_{label}.fem')
    model_fem = os.path.join(MODELS_DIR, f'motor_config_{label}.fem')

    femm.mi_saveas(tmp_fem)
    shutil.copy(tmp_fem, model_fem)
    print(f"  Salvo: {model_fem}")

    femm.mi_close()

femm.closefemm()
print("\nPronto! Modelos em models/:")
for label in CONFIGS:
    print(f"  motor_config_{label}.fem")
