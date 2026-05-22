"""
solver.py — Mesh, solve, and extract B_g(θ) along the air gap arc.
"""

import math
import csv
import femm
from geometry import GEO

N_POINTS = 720   # points around air gap arc (0.5 deg resolution)


def run(femfile: str):
    """Save, mesh and solve the current FEMM problem."""
    femm.mi_saveas(femfile)
    femm.mi_createmesh()
    femm.mi_analyze(1)      # 1 = run without showing progress dialog
    femm.mi_loadsolution()


def extract_Bg() -> list[tuple[float, float, float]]:
    """Sample B_r at N_POINTS equally spaced angles along R_ag.

    Returns list of (theta_deg, Br, Bt) tuples.
    theta_deg : mechanical degrees [0, 360)
    Br        : radial component of B (T) — positive outward
    Bt        : tangential component (T)
    """
    R = GEO['R_ag']
    results = []
    for i in range(N_POINTS):
        theta = 2 * math.pi * i / N_POINTS
        x = R * math.cos(theta)
        y = R * math.sin(theta)
        Bx, By = femm.mo_getb(x, y)
        Br =  Bx * math.cos(theta) + By * math.sin(theta)
        Bt = -Bx * math.sin(theta) + By * math.cos(theta)
        results.append((math.degrees(theta), Br, Bt))
    return results


def save_Bg(data: list, filepath: str):
    """Write B_g data to CSV."""
    with open(filepath, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['theta_deg', 'Br_T', 'Bt_T'])
        w.writerows(data)


def load_Bg(filepath: str) -> list[tuple[float, float, float]]:
    """Read B_g CSV back into a list of (theta_deg, Br, Bt)."""
    rows = []
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append((float(row['theta_deg']),
                         float(row['Br_T']),
                         float(row['Bt_T'])))
    return rows
