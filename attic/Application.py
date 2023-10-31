# Author: Alba Jano
# Last Modified: 27.09.2022 17:20
from abc import ABC
from dataclasses import dataclass


@dataclass()
class application(ABC):
    name: str = None
    data_size_min: int = None
    data_size_max: int = None
    delay_min: int = None
    delay_max: int = None
    cycles_per_bit_min: int = None
    cycles_per_bit_max: int = None


@dataclass
class redcap_application(application):
    name = "Reduced Capability applications"
