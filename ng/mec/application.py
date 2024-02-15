from abc import ABC
from typing import List
from mec.service import Service


class Application(ABC):

    def __init__(self, sim):
        pass

    def get_dependencies(self) -> List[Service]:
        pass

