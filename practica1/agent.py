from collections import deque
from copy import deepcopy
from queue import PriorityQueue

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import Accio, SENSOR, TipusCasella


class Estat:
    def __init__(
        self,
        taulell: str,
        tipus: TipusCasella,
        n=None,
        pare=None,
        accions_previes=None,
    ) -> None:
        self.__taulell = taulell
        self.__n = n
        self.__tipus = tipus
        self.__pare = pare
        self.__accions_previes = accions_previes or []
        self.__acc_pos = [
            (Accio.POSAR, (row, col)) for row in range(n) for col in range(n)
        ]

    def __hash__(self) -> int:
        return hash(self.__str__)

    def __eq__(self, other: "Estat") -> bool:
        return self.__taulell == other.__taulell

    def __str__(self) -> str:
        return "\n" + (
            "\n".join(
                [
                    " ".join(
                        [
                            "_"
                            if col == TipusCasella.LLIURE
                            else "O"
                            if col == TipusCasella.CARA
                            else "X"
                            for col in row
                        ]
                    )
                    for row in self.__taulell
                ]
            )
            + "\n"
        )

    def __repr__(self) -> str:
        return "\n" + (
            "\n".join(
                [
                    " ".join(
                        [
                            "_"
                            if col == TipusCasella.LLIURE
                            else "O"
                            if col == TipusCasella.CARA
                            else "X"
                            for col in row
                        ]
                    )
                    for row in self.__taulell
                ]
            )
            + "\n"
        )

    def __fer_accio(self, accio: tuple[Accio.POSAR, tuple[int, int]]) -> str:
        _, pos = accio
        taulell = self.__taulell
        taulell[pos[0]][pos[1]] = self.__tipus
        return taulell

    def __legal(self, accio: tuple[Accio.POSAR, tuple[int, int]]) -> bool:
        _, pos = accio
        return self.__taulell[pos[0]][pos[1]] == TipusCasella.LLIURE

    def accions_previes(self):
        return self.__accions_previes

    def es_meta(self) -> bool:
        n = self.__n
        taulell = self.__taulell

        for i in range(n):
            for j in range(n):
                casella = taulell[i][j]

                if casella == TipusCasella.LLIURE:
                    continue

                # Check horizontal, vertical, and both diagonal directions
                directions = [
                    (0, -1),  # left
                    (0, 1),  # right
                    (-1, 0),  # up
                    (1, 0),  # down
                    (-1, 1),  # 45ª
                    (1, 1),  # 135ª
                    (1, -1),  # 225ª
                    (-1, -1),  # 315º
                ]

                for dx, dy in directions:
                    count = 0
                    x, y = i, j

                    while 0 <= x < n and 0 <= y < n and taulell[x][y] == casella:
                        count += 1
                        x, y = x + dx, y + dy

                    if count >= 4:
                        return True

        return False

    def genera_fills(self) -> list:
        return [
            deepcopy(
                Estat(
                    taulell=self.__fer_accio(accio),
                    n=self.__n,
                    tipus=self.__tipus,
                    pare=self,
                    accions_previes=self.__accions_previes + [accio],
                )
            )
            for accio in self.__acc_pos
            if self.__legal(accio)
        ]


class _AgentBase(joc.Agent):
    def __init__(self, nom):
        super(_AgentBase, self).__init__(nom)
        self.__accions = None

    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        if self.__accions is None:
            self._cerca(
                Estat(
                    taulell=percepcio[SENSOR.TAULELL],
                    n=percepcio[SENSOR.MIDA][0],
                    tipus=self.jugador,
                )
            )

        return self.__accions.pop(0) if self.__accions else Accio.ESPERAR

    def getAccions(self):
        return self.__accions

    def setAccions(self, accions):
        self.__accions = accions

    def pinta(self, display):
        pass


class AgentProfunditat(_AgentBase):
    def __init__(self, nom):
        super(AgentProfunditat, self).__init__(nom)
        self.__oberts = None
        self.__tancats = None

    def _cerca(self, estat: Estat):
        self.__oberts = deque([estat])
        self.__tancats = set()

        while self.__oberts and self.getAccions() is None:
            actual = self.__oberts.popleft()

            if self.__tancats.add(actual):
                continue

            if actual.es_meta():
                self.setAccions(actual.accions_previes())
            else:
                fills = [
                    hijo for hijo in actual.genera_fills() if hijo not in self.__tancats
                ]
                self.__oberts.extendleft(
                    reversed(fills)
                )  # reversed for proper order insertion


class AgentAEstrella(_AgentBase):
    def __init__(self, nom):
        super(AgentAEstrella, self).__init__(nom)
        self.__oberts = None
        self.__tancats = None

    def _cerca(self, estat: Estat):
        self.__oberts = deque([estat])
        self.__tancats = set()

        while self.__oberts and self.getAccions() is None:
            actual = self.__oberts.popleft()

            if self.__tancats.add(actual):
                continue

            if actual.es_meta():
                self.setAccions(actual.accions_previes())
            else:
                fills = [
                    hijo for hijo in actual.genera_fills() if hijo not in self.__tancats
                ]
                self.__oberts.extendleft(
                    reversed(fills)
                )  # reversed for proper order insertion
