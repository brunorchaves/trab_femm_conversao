"""
winding.py — Slot-to-circuit assignment for all 3 stator winding configurations.
No FEMM dependency. All tables computed from first principles.

Machine: 36-slot, 6-pole, 3-phase induction motor
  P=6, p=3, m=3, q=2, Q_s=36, alpha=30 deg elec/slot
"""

from __future__ import annotations

# ── Phase belt (upper layer) ──────────────────────────────────────
# One electrical period = 12 slots (Q_s / p = 36 / 3).
# Belt order per period: A+, C-, B+, A-, C+, B-  (each belt = q=2 slots)
_BELT_12: list[tuple[str, int]] = (
    [('A', +1)] * 2 +  # slots  1– 2  → +A
    [('C', -1)] * 2 +  # slots  3– 4  → -C
    [('B', +1)] * 2 +  # slots  5– 6  → +B
    [('A', -1)] * 2 +  # slots  7– 8  → -A
    [('C', +1)] * 2 +  # slots  9–10  → +C
    [('B', -1)] * 2    # slots 11–12  → -B
)  # length = 12


def _upper(n: int) -> tuple[str, int]:
    """(phase, sign) for the upper layer of 1-indexed slot n."""
    return _BELT_12[(n - 1) % 12]


def _lower_short(n: int) -> tuple[str, int]:
    """Lower layer for short-pitch β=5/6 (y1=5).

    Rule: lower(n) = −upper(n − y1), indices wrap mod 36.
    """
    ref = ((n - 5 - 1) % 36) + 1
    phase, sign = _upper(ref)
    return phase, -sign


# ── Public API ────────────────────────────────────────────────────

def slot_layers(n: int, config: int) -> list[tuple[str, int]]:
    """Return [(phase, sign), ...] for each conductor layer in slot n.

    config 1 → single layer, full pitch y1=6  (I)
    config 2 → double layer, full pitch y1=6  (II)
    config 3 → double layer, short pitch y1=5 (III, β=5/6)

    sign +1: conductor current = +i_phase; -1: current = -i_phase.
    """
    if config == 1:
        return [_upper(n)]
    elif config == 2:
        return [_upper(n), _upper(n)]          # both layers identical
    elif config == 3:
        return [_upper(n), _lower_short(n)]
    raise ValueError(f"config must be 1, 2 or 3 — got {config!r}")


def net_current_factor(n: int, config: int) -> float:
    """Net current in slot n at t=0 (peak phase A), in units of N_c × I_pk.

    Excitation: i_A = +1.0,  i_B = i_C = −0.5  (normalised to I_pk).
    """
    _val = {'A': +1.0, 'B': -0.5, 'C': -0.5}
    return sum(sign * _val[ph] for ph, sign in slot_layers(n, config))


def full_table(config: int) -> list[dict]:
    """Complete 36-slot assignment table for one config."""
    return [
        {
            'slot':       n,
            'layers':     slot_layers(n, config),
            'net_Nc_Ipk': net_current_factor(n, config),
        }
        for n in range(1, 37)
    ]


# ── Verification ─────────────────────────────────────────────────

def _verify(config: int) -> None:
    """Assert every phase has zero net conductor-side count (balanced)."""
    tally = {'A': 0, 'B': 0, 'C': 0}
    for n in range(1, 37):
        for ph, sg in slot_layers(n, config):
            tally[ph] += sg
    for ph, s in tally.items():
        assert s == 0, f"Config {config}: phase {ph} net = {s} (expected 0)"


def _print_table(config: int) -> None:
    names = {1: 'I  – simples passo pleno y1=6',
             2: 'II – dupla passo pleno y1=6',
             3: 'III– dupla passo encurtado y1=5 (β=5/6)'}
    print(f"\nConfig {names[config]}")
    print(f"{'Slot':>4}  {'Camadas':<18}  Net(Nc·Ipk)")
    print('─' * 42)
    for row in full_table(config)[:12]:
        lstr = ', '.join(f"{'+-'[s < 0]}{ph}" for ph, s in row['layers'])
        print(f"{row['slot']:>4}  {lstr:<18}  {row['net_Nc_Ipk']:>+.1f}")
    print("  (repete ×3 para ranhuras 13–36)")


if __name__ == '__main__':
    print("=" * 50)
    print("Winding self-test (Q_s=36, P=6, q=2)")
    print("=" * 50)

    for cfg in (1, 2, 3):
        _verify(cfg)
        _print_table(cfg)

    print("\n--- Config III: slots mistos (camadas diferentes) ---")
    for n in range(1, 13):
        ly = slot_layers(n, 3)
        if ly[0] != ly[1]:
            u = f"{'+-'[ly[0][1]<0]}{ly[0][0]}"
            l = f"{'+-'[ly[1][1]<0]}{ly[1][0]}"
            print(f"  Ranhura {n:2d}: sup={u}  inf={l}")

    print("\nTodos os testes passaram.")
