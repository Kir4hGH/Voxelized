from enum import Enum


class ExportMode(Enum):
    """
    Enum of export type

    values:
    DEPENDENT = writes only the textures which is needed to voxelize. Fully dependent from an old pack

    SEMI_DEPENDENT = writes all the textures of every voxelized element. Still dependent from an old pack

    INDEPENDENT = Default option. Writes a new pack with voxelized old pack's elements and rest of its content

    FULL = Writes every single minecraft element into new pack
    """
    DEPENDENT = "dependent"
    SEMI_DEPENDENT = "semi-dependent"
    INDEPENDENT = "independent"  # default
    FULL = "full"
