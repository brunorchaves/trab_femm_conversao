"""
linear_iron_test.py — Config I com ferro linear (µ_r = 5000, sem saturação).

Objetivo: isolar o efeito Carter (geométrico, abertura de ranhura) dos
efeitos de saturação. Com µ_r constante, FEMM reproduz as hipóteses do
modelo analítico (µ_ferro >> 1). Os erros residuais são puramente de Carter.

Gera: Bg_linear_I.png, Bg_spectrum_linear_I.png
Imprime tabela comparativa: ke, analítico, FEMM_real, FEMM_linear.
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import femm
import numpy as np

import geometry
import solver
import analysis

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK_DIR = os.path.join(ROOT, 'results')
FEMM_DIR = '/tmp/femm_work'
os.makedirs(FEMM_DIR, exist_ok=True)
os.makedirs(WORK_DIR, exist_ok=True)

MU0     = 4 * math.pi * 1e-7
BG1_TGT = 0.9
G_M     = 0.5e-3
P       = 6
N_C     = 10
KW1     = 0.9577
N_FASE  = 12 * N_C   # Config I: camada simples
MU_R_LINEAR = 5000   # µ_r constante — sem saturação

# Corrente analítica para Config I
NI_fase = BG1_TGT * G_M * P * math.pi / (6 * MU0 * KW1)
I_pk    = NI_fase / N_FASE
I_A, I_B, I_C = I_pk, -I_pk/2, -I_pk/2

# Valores analíticos de referência (B_g1 = 0.9 T)
ANALYTICAL = {1: 0.900, 5: 0.0386, 7: 0.0212, 11: 0.0108, 13: 0.0091}
NU_SHOW    = [1, 5, 7, 11, 13, 23, 25]


def setup_materials_linear():
    """M250-50A como material LINEAR de µ_r = MU_R_LINEAR (sem curva B-H)."""
    femm.mi_addmaterial('M250-50A', MU_R_LINEAR, MU_R_LINEAR,
                        0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)
    femm.mi_addmaterial('Aluminio', 1, 1, 0, 0, 35.4, 0, 0, 1, 0, 0, 0, 0, 0)
    femm.mi_addmaterial('Cobre',    1, 1, 0, 0, 58.0, 0, 0, 1, 0, 0, 0, 0, 0)
    femm.mi_getmaterial('Air')


def setup_boundary():
    import materials as mat
    mat.setup_boundary()


def setup_circuits_I():
    femm.mi_addcircprop('PhaseA', I_A, 1)
    femm.mi_addcircprop('PhaseB', I_B, 1)
    femm.mi_addcircprop('PhaseC', I_C, 1)


def assign_regions_and_windings():
    import materials as mat
    from geometry import (region_label_pos, stator_slot_label_pos,
                          rotor_bar_label_pos, rotor_iron_label_pos, GEO)

    def _lbl(x, y, m, circuit='<None>', turns=0):
        femm.mi_addblocklabel(x, y)
        femm.mi_selectlabel(x, y)
        femm.mi_setblockprop(m, 1, 0, circuit, 0, 0, turns)
        femm.mi_clearselected()

    _lbl(*region_label_pos('outer_air'),   'Air')
    _lbl(*region_label_pos('stator_yoke'), 'M250-50A')
    _lbl(*region_label_pos('airgap'),      'Air')
    _lbl(*region_label_pos('rotor_yoke'),  'M250-50A')
    _lbl(*region_label_pos('shaft'),       'Air')

    for n in range(GEO['Q_r']):
        _lbl(*rotor_bar_label_pos(n),  'Aluminio')
        _lbl(*rotor_iron_label_pos(n), 'M250-50A')

    from winding import slot_layers
    _circ = {'A': 'PhaseA', 'B': 'PhaseB', 'C': 'PhaseC'}
    for n in range(GEO['Q_s']):
        ph, sg = slot_layers(n + 1, 1)[0]
        x, y   = stator_slot_label_pos(n, 1, 0)
        _lbl(x, y, 'Cobre', _circ[ph], sg * N_C)


def run_linear():
    femfile  = os.path.join(FEMM_DIR, 'motor_linear_I.fem')
    csv_file = os.path.join(WORK_DIR, 'Bg_linear_I.csv')

    femm.newdocument(0)
    femm.mi_probdef(0, 'millimeters', 'planar', 1e-8, 140, 30)

    print("  Desenhando geometria...")
    geometry.draw_all()

    print(f"  Materiais: ferro LINEAR µ_r = {MU_R_LINEAR} (sem saturação)...")
    setup_materials_linear()
    setup_boundary()
    setup_circuits_I()
    assign_regions_and_windings()

    print("  Resolvendo...")
    solver.run(femfile)

    print("  Extraindo B_g(θ)...")
    bg_data = solver.extract_Bg()
    solver.save_Bg(bg_data, csv_file)
    femm.mo_close()

    fft = analysis.compute_fft(bg_data)

    # ke scale
    Bg1 = fft['Bg1']
    ke  = BG1_TGT / Bg1
    print(f"  B_g1 bruto = {Bg1:.5f} T   ke = {ke:.4f}")
    bg_data = [(th, br * ke, bt * ke) for th, br, bt in bg_data]
    fft     = analysis.compute_fft(bg_data)
    solver.save_Bg(bg_data, csv_file)

    return fft, ke


def load_real_results():
    """Carrega CSV da Config I com ferro real (M250-50A B-H)."""
    csv_file = os.path.join(WORK_DIR, 'Bg_config_I.csv')
    if not os.path.exists(csv_file):
        return None, None
    bg_data = solver.load_Bg(csv_file)
    fft = analysis.compute_fft(bg_data)
    return fft, bg_data


def print_table(fft_linear, ke_linear, fft_real):
    print()
    print("=" * 75)
    print(f"  Diagnóstico ferro linear (µ_r = {MU_R_LINEAR})  vs  ferro real M250-50A")
    print(f"  Config I — B_g1 normalizado = {BG1_TGT} T")
    print("=" * 75)
    hdr_lin = f'Linear (ke={ke_linear:.2f})'
    print(f"  {'ν':>3}  {'Analítico':>10}  {'Real (ke=2.0)':>14}  "
          f"{hdr_lin:>18}  {'Erro real':>10}  {'Erro linear':>12}")
    print("  " + "-" * 73)

    nu_arr  = fft_linear['nu_elec']
    amp_lin = fft_linear['amplitude']

    nu_r_arr = fft_real['nu_elec'] if fft_real else None
    amp_real = fft_real['amplitude'] if fft_real else None

    for nu in NU_SHOW:
        # Linear iron result
        idx_l = np.where(nu_arr == nu)[0]
        b_lin = float(amp_lin[idx_l[0]]) if len(idx_l) else 0.0

        # Real iron result
        b_real = 0.0
        if nu_r_arr is not None:
            idx_r = np.where(nu_r_arr == nu)[0]
            b_real = float(amp_real[idx_r[0]]) if len(idx_r) else 0.0

        # Analytic
        b_ana = ANALYTICAL.get(nu, None)

        if b_ana:
            err_real  = (b_real  - b_ana) / b_ana * 100
            err_lin   = (b_lin   - b_ana) / b_ana * 100
            print(f"  {nu:>3}  {b_ana*1000:>8.1f} mT  {b_real*1000:>12.1f} mT  "
                  f"{b_lin*1000:>14.1f} mT  "
                  f"{err_real:>+8.0f}%  {err_lin:>+10.0f}%")
        else:
            print(f"  {nu:>3}  {'(ranhura)':>10}  {b_real*1000:>12.1f} mT  "
                  f"{b_lin*1000:>14.1f} mT")

    print("=" * 75)
    print(f"  ke real = 2.00   ke linear = {ke_linear:.4f}")
    print(f"  Diferença de ke: {(2.00 - ke_linear)/ke_linear*100:+.1f}%  "
          f"(residual = puro Carter com µ_ferro infinito)")


def main():
    print(f"\n{'='*55}")
    print(f"Teste ferro linear — Config I  |  I_pk = {I_pk:.3f} A")
    print(f"{'='*55}")

    femm.openfemm(winepath='/usr/bin/wine',
                  femmpath='/home/ribb/.wine/drive_c/femm42/bin/femm.exe')

    fft_linear, ke_linear = run_linear()
    fft_real, _           = load_real_results()

    femm.closefemm()

    print_table(fft_linear, ke_linear, fft_real)

    # Salva spectrum plot
    analysis.plot_spectrum(fft_linear, 'I_linear',
        os.path.join(WORK_DIR, 'Bg_spectrum_linear_I.png'))
    print(f"\nSalvo: Bg_spectrum_linear_I.png")


if __name__ == '__main__':
    main()
