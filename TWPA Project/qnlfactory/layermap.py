import gdsfactory as gf
from gdsfactory.config import PATH
from gdsfactory.generic_tech import LAYER_STACK, get_generic_pdk
from gdsfactory.generic_tech.get_klayout_pyxs import get_klayout_pyxs
from gdsfactory.technology import LayerLevel, LayerMap, LayerStack, LayerViews
from gdsfactory.typings import Layer

class QFaBLayers(LayerMap):
    SC1: Layer = (1, 0)  # Base layer metal
    SC1_E: Layer = (2, 0)  # Base layer etch (exposed silicon)
    SC1_V: Layer = (3, 0)  # Base layer flux trap holes

    JJ1: Layer = (11, 0)  # Junction high dose
    JJ1_UC: Layer = (12, 0)  # Junction low dose
    JJ1_BD: Layer = (13, 0)  # Junction bandaids
    JJ1_1: Layer = (11, 1)  # Junction high dose
    JJ1_UC_1: Layer = (12, 1)  # Junction low dose
    SE1: Layer = (15, 0)  # Shadow evaporated metal high dose
    SE1_1: Layer = (15, 1)  # Shadow evaporated metal
    SE1_UC: Layer = (16, 0)  # Shadow evaporated metal undercut / low dose

    AB1_B: Layer = (21, 0)  # Airbridge base
    AB1_E: Layer = (22, 0)  # Airbridge etch

    IND1: Layer = (31, 0)  # Indium bump liftoff
    UBM1: Layer = (32, 0)  # Under bump metal

    DSE1: Layer = (41, 0)  # Deep silicon etch

    # Second chip
    SC2: Layer = (101, 0)  # Base layer metal
    SC2_E: Layer = (102, 0)  # Base layer etch (exposed silicon)

    JJ2: Layer = (111, 0)  # Junction high dose
    JJ2_UC: Layer = (112, 0)  # Junction low dose
    JJ2_BD: Layer = (113, 0)  # Junction bandaids

    AB2_B: Layer = (121, 0)  # Airbridge base
    AB2_E: Layer = (122, 0)  # Airbridge etch

    IND2: Layer = (131, 0)  # Indium bump liftoff
    UBM2: Layer = (132, 0)  # Under bump metal

    DSE2: Layer = (141, 0)  # Deep silicon etch

    KEEPOUT: Layer = (201, 0)  # Keepout layer for flux trapping holes/bump bonds