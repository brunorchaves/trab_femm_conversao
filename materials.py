"""
materials.py — Material definitions, circuits, and block-label assignment.
"""

import femm
from geometry import (GEO, region_label_pos,
                      stator_slot_label_pos, stator_tooth_label_pos,
                      rotor_bar_label_pos, rotor_iron_label_pos)
from winding import slot_layers

_BH_M250 = [
    (0,      0.000), (50,     0.400), (100,    0.850), (200,    1.100),
    (500,    1.350), (1000,   1.520), (2500,   1.590), (5000,   1.690),
    (10000,  1.810), (30000,  1.950), (100000, 2.100),
]


def setup_materials():
    femm.mi_addmaterial('M250-50A', 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)
    for H, B in _BH_M250:
        femm.mi_addbhpoint('M250-50A', B, H)
    # Aluminium: conductivity 35.4 MS/m (FEMM units = MS/m)
    femm.mi_addmaterial('Aluminio', 1, 1, 0, 0, 35.4, 0, 0, 1, 0, 0, 0, 0, 0)
    femm.mi_addmaterial('Cobre',    1, 1, 0, 0, 58.0, 0, 0, 1, 0, 0, 0, 0, 0)
    femm.mi_getmaterial('Air')


def setup_boundary():
    femm.mi_addboundprop('A=0', 0, 0, 0, 0, 0, 0, 0, 0, 0)
    R = GEO['R_bound']
    # Select the two 180-deg outer arcs by their midpoints
    for theta in (90, 270):
        import math
        x = R * math.cos(math.radians(theta))
        y = R * math.sin(math.radians(theta))
        femm.mi_selectarcsegment(x, y)
    femm.mi_setarcsegmentprop(5, 'A=0', 0, 0)
    femm.mi_clearselected()


def setup_circuits(config, I_A, I_B, I_C):
    if config in (1, 2):
        femm.mi_addcircprop('PhaseA', I_A, 1)
        femm.mi_addcircprop('PhaseB', I_B, 1)
        femm.mi_addcircprop('PhaseC', I_C, 1)
    else:  # Config III: single unit-current source, turns carry all amplitude
        femm.mi_addcircprop('NC3', 1.0, 1)


def _label(x, y, mat, circuit='<None>', turns=0):
    femm.mi_addblocklabel(x, y)
    femm.mi_selectlabel(x, y)
    femm.mi_setblockprop(mat, 1, 0, circuit, 0, 0, turns)
    femm.mi_clearselected()


def assign_regions():
    """Label every non-winding region."""
    # Large-scale regions
    _label(*region_label_pos('outer_air'),   'Air')
    _label(*region_label_pos('stator_yoke'), 'M250-50A')
    _label(*region_label_pos('airgap'),      'Air')
    _label(*region_label_pos('rotor_yoke'),  'M250-50A')
    _label(*region_label_pos('shaft'),       'Air')

    # 72 stator teeth (between slot lines, same radial band as slots)
    for n in range(GEO['Q_s']):
        _label(*stator_tooth_label_pos(n), 'M250-50A')

    # 28 rotor bars + 28 rotor inter-bar iron regions
    for n in range(GEO['Q_r']):
        _label(*rotor_bar_label_pos(n),   'Aluminio')
        _label(*rotor_iron_label_pos(n),  'M250-50A')


def assign_windings(config: int, N_c: int, I_pk: float = 1.0):
    """Place conductor labels for all 72 stator slots.

    Configs I & II: use PhaseA/B/C circuits, standard turns.
    Config III: net amp-turns per slot via a single 'NC3' unit-current circuit.
    This avoids two block labels in the same region (duplicate-label warning).
    """
    _circ = {'A': 'PhaseA', 'B': 'PhaseB', 'C': 'PhaseC'}

    for n in range(GEO['Q_s']):
        if config == 1:
            ph, sg = slot_layers(n + 1, 1)[0]
            x, y = stator_slot_label_pos(n, 1, 0)
            _label(x, y, 'Cobre', _circ[ph], sg * N_c)

        elif config == 2:
            ph, sg = slot_layers(n + 1, 2)[0]
            x, y = stator_slot_label_pos(n, 2, 0)
            _label(x, y, 'Cobre', _circ[ph], sg * N_c * 2)

        else:  # config 3 — one block per slot, turns = net amp-turns
            from winding import net_current_factor
            net = net_current_factor(n + 1, 3)
            turns = int(round(net * N_c * I_pk))   # amp-turns (circuit I=1A)
            x, y = stator_slot_label_pos(n, 1, 0)  # single centred label
            _label(x, y, 'Cobre', 'NC3', turns)


def setup_all(config, N_c, I_A, I_B, I_C, I_pk=1.0):
    setup_materials()
    setup_boundary()
    setup_circuits(config, I_A, I_B, I_C)
    assign_regions()
    assign_windings(config, N_c, I_pk)
