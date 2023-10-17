from collections import deque
from copy import deepcopy
from queue import PriorityQueue
from typing import List

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import Accio, TipusCasella, SENSOR


class _EstatBase:
    def __init__(
        self,
        taulell: List[List["TipusCasella"]],
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

    def __eq__(self, other: "_EstatBase") -> bool:
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

    def __fer_accio(
        self, accio: tuple[Accio.POSAR, tuple[int, int]]
    ) -> List[List["TipusCasella"]]:
        _, pos = accio
        taulell = self.__taulell
        taulell[pos[0]][pos[1]] = self.__tipus
        return taulell

    def __legal(self, accio: tuple[Accio.POSAR, tuple[int, int]]) -> bool:
        _, pos = accio
        return self.__taulell[pos[0]][pos[1]] == TipusCasella.LLIURE

    def accions_previes(self) -> List[tuple[Accio.POSAR, tuple[int, int]]]:
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

    def genera_fills(self) -> list["_EstatBase"]:
        return [
            deepcopy(
                _EstatBase(
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


class _EstatAEstrella(_EstatBase):
    def __init__(
        self,
        taulell: str,
        tipus: TipusCasella,
        n=None,
        pare=None,
        accions_previes=None,
    ) -> None:
        super(_EstatAEstrella).__init__(taulell, tipus, n, pare, accions_previes)
        self.__cost = pare.__cost + 1 if pare else 0
        self.__heuristica = self.__calcul_heuristica()

    def __lt__(self, other: "_EstatAEstrella") -> int:
        return self.__heuristica - other.__heuristica

    def __calcul_heuristica(self) -> int:
        n = self.__n
        taulell = self.__taulell

        count = 0
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
                    x, y = i, j

                    while 0 <= x < n and 0 <= y < n and taulell[x][y] == casella:
                        count += 1
                        x, y = x + dx, y + dy

        return count

    def valor(self) -> int:
        return self.__cost + self.__heuristica


class _AgentBase(joc.Agent):
    def __init__(self, nom):
        super(_AgentBase, self).__init__(nom)

    def pinta(self, display):
        pass


class AgentProfunditat(_AgentBase):
    def __init__(self, nom):
        super(AgentProfunditat, self).__init__(nom)
        self.__accions = None
        self.__oberts = None
        self.__tancats = None

    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        if self.__accions is None:
            self._cerca(
                _EstatBase(
                    taulell=percepcio[SENSOR.TAULELL],
                    n=percepcio[SENSOR.MIDA][0],
                    tipus=self.jugador,
                )
            )

        return self.__accions.pop(0) if self.__accions else Accio.ESPERAR

    def _cerca(self, estat: _EstatBase):
        self.__oberts = deque([estat])
        self.__tancats = set()

        while self.__oberts and self.__accions is None:
            actual = self.__oberts.popleft()

            if self.__tancats.add(actual):
                continue

            if actual.es_meta():
                self.__accions = actual.accions_previes()
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
        self.__accions = None
        self.__oberts = None
        self.__tancats = None

    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        if self.__accions is None:
            self._cerca(
                _EstatAEstrella(
                    taulell=percepcio[SENSOR.TAULELL],
                    n=percepcio[SENSOR.MIDA][0],
                    tipus=self.jugador,
                )
            )

        return self.__accions.pop(0) if self.__accions else Accio.ESPERAR

    def _cerca(self, estat: _EstatBase):
        self.__oberts = PriorityQueue()
        self.__tancats = set()

        self.__oberts.put((estat.valor(), estat))

        while not self.__oberts.empty() and self.getAccions() is None:
            _, actual = self.__oberts.get()

            if self.__tancats.add(actual):
                continue

            if actual.es_meta():
                self.setAccions(actual.accions_previes())
            else:
                for hijo in actual.genera_fills():
                    if hijo not in self.__tancats:
                        self.__oberts.put((hijo.valor(), hijo))
