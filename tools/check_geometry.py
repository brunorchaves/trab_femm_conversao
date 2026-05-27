"""
check_geometry.py — Desenha só a geometria no FEMM e salva bitmap para
comparação visual com results/motor_geometry_new.png (gerado pelo Python puro).

Uso:
  DISPLAY=:1 ~/femm_env/bin/python tools/check_geometry.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import femm
import geometry

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEMM_DIR = '/tmp/femm_work'
os.makedirs(FEMM_DIR, exist_ok=True)

FEM_FILE = os.path.join(FEMM_DIR, 'check_geom.fem')
BMP_FILE = os.path.join(FEMM_DIR, 'femm_geometry_check.bmp')

femm.openfemm(winepath='/usr/bin/wine',
              femmpath='/home/ribb/.wine/drive_c/femm42/bin/femm.exe')

femm.newdocument(0)
femm.mi_probdef(0, 'millimeters', 'planar', 1e-8, 140, 30)

print("Desenhando geometria...")
geometry.draw_all()

femm.mi_saveas(FEM_FILE)
femm.mi_zoom(-115, -115, 115, 115)

print(f"Salvando bitmap em {BMP_FILE} ...")
femm.mi_savebitmap(BMP_FILE)

import shutil
dest = os.path.join(ROOT, 'results', 'femm_geometry_check.png')
os.makedirs(os.path.dirname(dest), exist_ok=True)
try:
    from PIL import Image
    Image.open(BMP_FILE).save(dest)
    print(f"PNG salvo em {dest}")
except ImportError:
    shutil.copy(BMP_FILE, dest.replace('.png', '.bmp'))
    print(f"BMP disponível em {dest.replace('.png', '.bmp')} (PIL não instalado)")

femm.closefemm()
print("Pronto! Compare results/femm_geometry_check.png com results/motor_geometry_new.png")
