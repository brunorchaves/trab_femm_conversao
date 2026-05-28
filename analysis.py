"""
analysis.py — FFT and plotting of B_g results for all 3 configurations.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')   # headless — saves PNG without display

# Pole pairs (used to convert mechanical harmonics to electrical)
P_PAIRS = 3   # p = P/2 = 3

# Analytical reference values (B_g1 = 0.9 T target, Q_s=36, q=2)
_ANALYTICAL = {
    'I':   {1: 0.900, 5: 0.0482, 7: 0.0344, 11: 0.0818, 13: 0.0692},
    'II':  {1: 0.900, 5: 0.0482, 7: 0.0344, 11: 0.0818, 13: 0.0692},
    'III': {1: 0.900, 5: 0.0129, 7: 0.0092, 11: 0.0818, 13: 0.0692},
}


def compute_fft(data: list) -> dict:
    """Compute spatial FFT of B_r.

    data : list of (theta_deg, Br, Bt) from solver.extract_Bg()

    Returns dict:
      'nu_elec'  : array of electrical harmonic orders (1, 2, 3, ...)
      'amplitude': array of |B_g,ν| in T (double-sided → single-sided)
      'Bg1'      : fundamental amplitude (T)
    """
    Br = np.array([row[1] for row in data])
    N  = len(Br)

    # FFT over mechanical angle; electrical harmonic ν_e = ν_mec / p
    coeffs = np.fft.rfft(Br) * (2.0 / N)
    nu_mec = np.arange(len(coeffs))

    # Keep only harmonics that correspond to integer electrical orders
    # ν_elec = ν_mec / p  →  only multiples of p
    mask = (nu_mec % P_PAIRS == 0)
    nu_mec_sel   = nu_mec[mask]
    nu_elec_sel  = nu_mec_sel // P_PAIRS
    amp_sel      = np.abs(coeffs[mask])

    idx1 = np.where(nu_elec_sel == 1)[0]
    Bg1  = float(amp_sel[idx1[0]]) if len(idx1) > 0 else 0.0

    return {
        'nu_elec':   nu_elec_sel,
        'amplitude': amp_sel,
        'Bg1':       Bg1,
        'coeffs_full': coeffs,   # full spectrum for slot-harmonic detection
        'nu_mec_full': nu_mec,
    }


def find_slot_harmonics(fft_result: dict, threshold: float = 0.005) -> list:
    """Return (nu_mec, amplitude) pairs above threshold for slot harmonics.

    Expected stator slot harmonics (electrical): ν = 12M ± 1 → mec = 36M ± 3
    """
    coeffs = fft_result['coeffs_full']
    nu_mec = fft_result['nu_mec_full']
    amps   = np.abs(coeffs)

    # Stator slot harmonic indices (ν_mec = 36M ± 3, M=1,2,…)
    expected_mec = []
    for M in range(1, 6):
        expected_mec += [36 * M - P_PAIRS, 36 * M + P_PAIRS]

    found = []
    for nm in expected_mec:
        if 0 <= nm < len(amps) and amps[nm] > threshold:
            nu_e = nm // P_PAIRS if nm % P_PAIRS == 0 else nm / P_PAIRS
            found.append((nm, nu_e, float(amps[nm])))
    return found


def plot_Bg_spatial(data: list, config_label: str, outfile: str):
    """Plot B_r(θ) spatial distribution."""
    theta = [row[0] for row in data]
    Br    = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(theta, Br, lw=0.8, color='steelblue')
    ax.axhline(0, color='k', lw=0.5)
    ax.set_xlabel('θ mecânico (graus)')
    ax.set_ylabel('B_r  (T)')
    ax.set_title(f'Distribuição espacial de B_g — Config {config_label}')
    ax.set_xlim(0, 360)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
    print(f"  Salvo: {outfile}")


def plot_spectrum(fft_result: dict, config_label: str, outfile: str):
    """Bar chart of electrical harmonic amplitudes."""
    nu   = fft_result['nu_elec']
    amp  = fft_result['amplitude']
    Bg1  = fft_result['Bg1']

    # Show up to ν=40 (captures slot harmonics at ν=11,13,23,25,35,37)
    mask = (nu >= 1) & (nu <= 40) & (amp > 0.001)
    nu_s  = nu[mask]
    amp_s = amp[mask]

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(nu_s, amp_s, width=0.6, color='steelblue', label='FEMM')

    # Overlay analytical reference
    ref = _ANALYTICAL.get(config_label.strip(), {})
    for nu_r, amp_r in ref.items():
        ax.plot(nu_r, amp_r, 'r^', ms=8, label='Analítico' if nu_r == 1 else '')

    ax.set_xlabel('Ordem harmônica elétrica ν')
    ax.set_ylabel('|B_g,ν|  (T)')
    ax.set_title(f'Espectro de B_g — Config {config_label}  '
                 f'(B_g1 = {Bg1:.4f} T)')
    ax.set_yscale('log')
    ax.set_ylim(bottom=1e-3)
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
    print(f"  Salvo: {outfile}")


def plot_comparison(results: dict, outfile: str):
    """Grouped bar chart comparing all 3 configs at key harmonics."""
    nu_show = [1, 5, 7, 11, 13, 23, 25, 35, 37]
    configs  = ['I', 'II', 'III']
    colors   = ['steelblue', 'darkorange', 'forestgreen']
    x = np.arange(len(nu_show))
    width = 0.25

    fig, ax = plt.subplots(figsize=(11, 4.5))
    for i, (cfg, col) in enumerate(zip(configs, colors)):
        fft_r = results[cfg]['fft']
        amps  = []
        for nu in nu_show:
            idx = np.where(fft_r['nu_elec'] == nu)[0]
            amps.append(float(fft_r['amplitude'][idx[0]]) if len(idx) > 0 else 0.0)
        ax.bar(x + i * width, amps, width, label=f'Config {cfg}', color=col)

    ax.set_xticks(x + width)
    ax.set_xticklabels([str(n) for n in nu_show])
    ax.set_xlabel('Ordem harmônica elétrica ν')
    ax.set_ylabel('|B_g,ν|  (T)')
    ax.set_title('Comparação do espectro de B_g — 3 configurações de enrolamento')
    ax.set_yscale('log')
    ax.set_ylim(bottom=1e-3)
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
    print(f"  Salvo: {outfile}")


def print_summary(config_label: str, fft_result: dict):
    """Print key harmonic values to stdout."""
    nu   = fft_result['nu_elec']
    amp  = fft_result['amplitude']
    print(f"\n{'─'*50}")
    print(f"Config {config_label}  — B_g1 = {fft_result['Bg1']:.4f} T")
    print(f"{'ν':>4}  {'|B_g,ν| (T)':>12}  {'/ B_g1':>8}")
    print(f"{'─'*50}")
    for nu_target in [1, 5, 7, 11, 13, 23, 25, 35, 37]:
        idx = np.where(nu == nu_target)[0]
        if len(idx):
            a = float(amp[idx[0]])
            r = a / fft_result['Bg1'] if fft_result['Bg1'] > 0 else 0
            print(f"{nu_target:>4}  {a:>12.4f}  {r:>8.4f}")
