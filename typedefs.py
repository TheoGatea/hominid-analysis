from dataclasses import dataclass
from enum import Enum

class DietType(Enum):
    OMNIVORE = 0
    DRY_FRUIT = 1
    HARD_FRUIT = 2
    CARNIVORE = 3
    SOFT_FRUIT = 4
    
    # returns DietType corresponding to data, throws if bad input
    @staticmethod
    def from_str(data: str):
        match data:
            case "dry fruits":
                return DietType.DRY_FRUIT
            case "soft fruits":
                return DietType.SOFT_FRUIT
            case "omnivore":
                return DietType.OMNIVORE
            case "carnivorous":
                return DietType.CARNIVORE
            case "hard fruits":
                return DietType.HARD_FRUIT
            case _:
                raise NotImplementedError(f"no diet type {data} possible")

class TechType(Enum):
    M_1 = 0 
    M_2 = 1 
    M_3 = 2
    M_4 = 3
    PRIMITIVE = 4
    NO_TECH = 5

    # returns TechType corresponding to data, throws if bad input
    @staticmethod
    def from_str(data: str):
        match data:
            case "primitive":
                return TechType.PRIMITIVE
            case "mode 1":
                return TechType.M_1
            case "mode 2":
                return TechType.M_2
            case "mode 3":
                return TechType.M_3
            case "mode 4":
                return TechType.M_4
            case _:
                raise NotImplementedError(f"no tech type {data} possible")

    def to_string(self):
        match self:
            case self.PRIMITIVE:
                return "primitive"
            case self.M_1:
                return "mode 1"
            case self.M_2:
                return "mode 2"
            case self.M_3:
                return "mode 3"
            case self.M_4:
                return "mode 4"
            case self.NO_TECH:
                return "no tech"

    def __lt__(self, other) -> bool:
        return self.value < other.value


@dataclass
class Hominid:
    species: str
    cranial_cap: float
    height: float
    tech_type: TechType
    diet: DietType
    skull_body_ratio: float

