"""
check_geometry.py — Desenha só a geometria no FEMM e salva bitmap para
comparação visual com motor_geometry_new.png (gerado pelo Python puro).

Uso:
  DISPLAY=:1 ~/femm_env/bin/python check_geometry.py
"""

import os
import femm
import geometry

FEMM_DIR = '/tmp/femm_work'
os.makedirs(FEMM_DIR, exist_ok=True)

FEM_FILE = os.path.join(FEMM_DIR, 'check_geom.fem')
BMP_FILE = '/tmp/femm_work/femm_geometry_check.bmp'

femm.openfemm(winepath='/usr/bin/wine',
              femmpath='/home/ribb/.wine/drive_c/femm42/bin/femm.exe')

femm.newdocument(0)
femm.mi_probdef(0, 'millimeters', 'planar', 1e-8, 140, 30)

print("Desenhando geometria...")
geometry.draw_all()

femm.mi_saveas(FEM_FILE)

# Zoom para ver a geometria toda antes de salvar o bitmap
femm.mi_zoom(-115, -115, 115, 115)

print(f"Salvando bitmap em {BMP_FILE} ...")
femm.mi_savebitmap(BMP_FILE)

# Copia para cwd (nome ASCII) via shutil para evitar path Wine
import shutil
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
dest = os.path.join(OUT_DIR, 'femm_geometry_check.png')
try:
    from PIL import Image
    img = Image.open(BMP_FILE)
    img.save(dest)
    print(f"PNG salvo em {dest}")
except ImportError:
    shutil.copy(BMP_FILE, '/tmp/femm_geometry_check.bmp')
    print(f"BMP disponível em /tmp/femm_geometry_check.bmp (PIL não instalado)")

femm.closefemm()
print("Pronto! Compare femm_geometry_check.png com motor_geometry_new.png")
