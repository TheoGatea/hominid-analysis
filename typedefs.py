from dataclasses import dataclass
from enum import Enum

class IncisorSize(Enum):
    SMALL = 0 
    BIG = 1 
    MEGADONY = 2 
    VERY_SMALL = 3 
    MED_LARGE = 4 

class JawShape(Enum):
    U_SHAPE = 0
    MODERN = 1
    CONICAL = 2
    V_SHAPE = 3

class CanineSize(Enum):
    SMALL = 0 
    BIG = 1

class CanineShape(Enum):
    CONICAL = 0
    INCISIFORM = 1

class EnamelType(Enum):
    THICK = 0
    MED_THICK = 1
    VERY_THICK = 2
    MED_THIN = 3
    THIN = 4

class DietType(Enum):
    OMNIVORE = 0
    DRY_FRUIT = 1
    HARD_FRUIT = 2
    CARNIVORE = 3
    SOFT_FRUIT = 4

class HipShape(Enum):
    WIDE = 0
    SLIM = 1
    MODERN = 2
    VERY_MODERN = 3

@dataclass
class Hominid:
    species: str
    incisor_sz: IncisorSize
    jaw_shape: JawShape
    canine_size: CanineSize
    canine_shape: CanineShape
    enamel: EnamelType
    diet: DietType
    hip: HipShape

