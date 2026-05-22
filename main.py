"""
main.py — Orchestrates the 3-configuration FEMM simulation.

Runs Configs I, II, III sequentially:
  1. Opens FEMM via Wine
  2. Draws motor geometry
  3. Assigns materials, circuits, and windings
  4. Meshes and solves
  5. Extracts B_g(θ) along air gap arc
  6. Saves CSV + plots
  7. Prints harmonic summary

Usage:
  DISPLAY=:1 ~/femm_env/bin/python main.py
"""

import os
import math
import femm

import geometry
import materials
import solver
import analysis

# ── Working directories ───────────────────────────────────────────
# FEMM/Wine cannot handle non-ASCII chars (Á in "Área") in file paths.
# .fem and .ans files go to /tmp/femm_work/ (clean ASCII path).
# CSV and PNG outputs go to the project directory.
WORK_DIR  = os.path.dirname(os.path.abspath(__file__))
FEMM_DIR  = '/tmp/femm_work'
os.makedirs(FEMM_DIR, exist_ok=True)

# ── Calibration constants ─────────────────────────────────────────
MU0      = 4 * math.pi * 1e-7
BG1_TGT  = 0.9          # T  — target fundamental flux density
G_M      = 0.5e-3        # m  — air gap
P        = 6             # poles
N_C      = 10            # turns per coil side (per layer)

def _Ipk(kw1: float, N_fase: int) -> float:
    """Peak phase current for target B_g1."""
    NI_fase = BG1_TGT * G_M * P * math.pi / (6 * MU0 * kw1)
    return NI_fase / N_fase

# Config I  : N_fase = 12 coils × N_C turns = 12*N_C
# Config II : N_fase = 24 coils × N_C turns = 24*N_C  (two layers)
# Config III: same coil count as II but β=5/6 → different kw1
CONFIGS = {
    'I':   {'config': 1, 'kw1': 0.9577, 'N_fase': 12 * N_C},
    'II':  {'config': 2, 'kw1': 0.9577, 'N_fase': 24 * N_C},
    'III': {'config': 3, 'kw1': 0.9250, 'N_fase': 24 * N_C},
}


def run_one(label: str, cfg_params: dict) -> dict:
    """Run a single configuration end-to-end. Returns fft result dict."""
    config  = cfg_params['config']
    I_pk    = _Ipk(cfg_params['kw1'], cfg_params['N_fase'])
    I_A     =  I_pk
    I_B     = -I_pk / 2
    I_C     = -I_pk / 2

    print(f"\n{'='*55}")
    print(f"Config {label}  |  N_c={N_C}  I_pk={I_pk:.3f} A")
    print(f"{'='*55}")

    femfile  = os.path.join(FEMM_DIR,  f'motor_config_{label}.fem')
    csv_file = os.path.join(WORK_DIR,  f'Bg_config_{label}.csv')

    # ── Build model ───────────────────────────────────────────────
    femm.newdocument(0)
    femm.mi_probdef(0, 'millimeters', 'planar', 1e-8, 140, 30)

    print("  Desenhando geometria...")
    geometry.draw_all()

    print("  Atribuindo materiais e enrolamentos...")
    materials.setup_all(config, N_C, I_A, I_B, I_C, I_pk)

    # ── Solve ─────────────────────────────────────────────────────
    print("  Resolvendo...")
    solver.run(femfile)

    # ── Extract ───────────────────────────────────────────────────
    print("  Extraindo B_g(θ)...")
    bg_data = solver.extract_Bg()
    solver.save_Bg(bg_data, csv_file)

    femm.mo_close()

    # ── Analyse ───────────────────────────────────────────────────
    print("  Calculando FFT...")
    fft_result = analysis.compute_fft(bg_data)

    # Auto-scale: multiply all B values so B_g1 = 0.9 T
    Bg1_actual = fft_result['Bg1']
    kc = BG1_TGT / Bg1_actual if Bg1_actual > 0 else 1.0
    if abs(kc - 1.0) > 0.02:
        print(f"  Fator de escala aplicado: {kc:.4f}  "
              f"(B_g1 bruto={Bg1_actual:.4f} T → normalizado={BG1_TGT} T)")
        # Rescale bg_data and recompute fft
        bg_data  = [(th, br * kc, bt * kc) for th, br, bt in bg_data]
        fft_result = analysis.compute_fft(bg_data)
        solver.save_Bg(bg_data, csv_file)  # overwrite with scaled data

    analysis.print_summary(label, fft_result)

    analysis.plot_Bg_spatial(bg_data, label,
        os.path.join(WORK_DIR,  f'Bg_spatial_{label}.png'))
    analysis.plot_spectrum(fft_result, label,
        os.path.join(WORK_DIR,  f'Bg_spectrum_{label}.png'))

    slot_h = analysis.find_slot_harmonics(fft_result)
    if slot_h:
        print(f"  Harmônicos de ranhura detectados:")
        for nm, ne, amp in slot_h:
            print(f"    ν_mec={nm}  ν_elec={ne:.1f}  |B|={amp:.4f} T")

    return {'fft': fft_result, 'bg_data': bg_data}


def main():
    femm.openfemm(winepath='/usr/bin/wine',
                  femmpath='/home/ribb/.wine/drive_c/femm42/bin/femm.exe')

    all_results = {}
    for label, params in CONFIGS.items():
        all_results[label] = run_one(label, params)

    # ── Comparison plot ───────────────────────────────────────────
    analysis.plot_comparison(all_results,
        os.path.join(WORK_DIR,  'Bg_comparison.png'))

    femm.closefemm()
    print("\nConcluído. Arquivos gerados em:", WORK_DIR)


if __name__ == '__main__':
    main()
