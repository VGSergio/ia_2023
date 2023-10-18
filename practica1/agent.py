from collections import deque
from copy import deepcopy
from queue import PriorityQueue
import time

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import Accio, SENSOR, TipusCasella


class EstatProfunditat:
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

    def __eq__(self, other: "EstatProfunditat") -> bool:
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

                directions = [
                    (0, -1),  # left
                    (0, 1),  # right
                    (-1, 0),  # top
                    (1, 0),  # down
                    (-1, 1),  # diagonal top right
                    (1, 1),  # diagonal bottom right
                    (1, -1),  # diagonal bottom left
                    (-1, -1),  # diagonal bottom left
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

    def genera_fills(self) -> list["EstatProfunditat"]:
        return [
            EstatProfunditat(
                taulell=deepcopy(self).__fer_accio(accio),
                n=self.__n,
                tipus=self.__tipus,
                pare=self,
                accions_previes=self.__accions_previes + [accio],
            )
            for accio in self.__acc_pos
            if self.__legal(accio)
        ]


class EstatAEstrella:
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
        self.__cost = pare.__cost + 1 if pare else 0
        self.__heuristica = self.__calcul_heuristica() if accions_previes else 1000
        self.__acc_pos = [
            (Accio.POSAR, (row, col)) for row in range(n) for col in range(n)
        ]

    def __hash__(self) -> int:
        return hash(self.__str__)

    def __eq__(self, other: "EstatAEstrella") -> bool:
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

    def __lt__(self, other: "EstatAEstrella") -> int:
        return self.__heuristica - other.__heuristica

    def __fer_accio(self, accio: tuple[Accio.POSAR, tuple[int, int]]) -> str:
        _, pos = accio
        taulell = self.__taulell
        taulell[pos[0]][pos[1]] = self.__tipus
        return taulell

    def __legal(self, accio: tuple[Accio.POSAR, tuple[int, int]]) -> bool:
        _, pos = accio
        return self.__taulell[pos[0]][pos[1]] == TipusCasella.LLIURE

    def __calcul_heuristica(self) -> int:
        n = self.__n
        taulell = self.__taulell
        row, col = self.__accions_previes[-1][1]
        casella = taulell[row][col]
        count = 0

        directions = [
            (0, -1),  # left
            (0, 1),  # right
            (-1, 0),  # top
            (1, 0),  # down
            (-1, 1),  # diagonal top right
            (1, 1),  # diagonal bottom right
            (1, -1),  # diagonal bottom left
            (-1, -1),  # diagonal bottom left
        ]

        for dx, dy in directions:
            x, y = row + dx, col + dy

            while max(0, row - 3) <= x < min(n, row + 4) and max(0, col - 3) <= y < min(
                n, col + 4
            ):
                if casella == taulell[x][y]:
                    count += 1
                x, y = x + dx, y + dy

        return 4 * 4 - 1 - count

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

                directions = [
                    (0, -1),  # left
                    (0, 1),  # right
                    (-1, 0),  # top
                    (1, 0),  # down
                    (-1, 1),  # diagonal top right
                    (1, 1),  # diagonal bottom right
                    (1, -1),  # diagonal bottom left
                    (-1, -1),  # diagonal bottom left
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

    def genera_fills(self) -> list["EstatAEstrella"]:
        return [
            EstatAEstrella(
                taulell=deepcopy(self).__fer_accio(accio),
                n=self.__n,
                tipus=self.__tipus,
                pare=self,
                accions_previes=self.__accions_previes + [accio],
            )
            for accio in self.__acc_pos
            if self.__legal(accio)
        ]

    def valor(self) -> int:
        return self.__cost + self.__heuristica


class AgentProfunditat(joc.Agent):
    def __init__(self, nom):
        super(AgentProfunditat, self).__init__(nom)
        self.__accions = None
        self.__oberts = None
        self.__tancats = None

    def pinta(self, display):
        pass

    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        if self.__accions is None:
            while True:
                start = time.time()
                self._cerca(
                    EstatProfunditat(
                        taulell=percepcio[SENSOR.TAULELL],
                        n=percepcio[SENSOR.MIDA][0],
                        tipus=self.jugador,
                    )
                )
                print(time.time() - start)
                self.__accions = None

        # Return the solution from the leave to the root
        return self.__accions.pop() if self.__accions else Accio.ESPERAR
        # Return the solution from the root to the leaves, but teacher method doesn't detect the solution properly
        return self.__accions.pop(0) if self.__accions else Accio.ESPERAR

    def _cerca(self, estat: EstatProfunditat):
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


class AgentAEstrella(joc.Agent):
    def __init__(self, nom):
        super(AgentAEstrella, self).__init__(nom)
        self.__accions = None
        self.__oberts = None
        self.__tancats = None

    def pinta(self, display):
        pass

    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        if self.__accions is None:
            while True:
                start = time.time()

                self._cerca(
                    EstatAEstrella(
                        taulell=percepcio[SENSOR.TAULELL],
                        n=percepcio[SENSOR.MIDA][0],
                        tipus=self.jugador,
                    )
                )

                print(time.time() - start)

        # Return the solution from the leave to the root
        return self.__accions.pop() if self.__accions else Accio.ESPERAR
        # Return the solution from the root to the leaves, but teacher method doesn't detect the solution properly
        return self.__accions.pop(0) if self.__accions else Accio.ESPERAR

    def _cerca(self, estat: EstatAEstrella):
        self.__oberts = PriorityQueue()
        self.__tancats = set()

        self.__oberts.put((estat.valor(), estat))

        while not self.__oberts.empty() and self.__accions is None:
            _, actual = self.__oberts.get()

            if self.__tancats.add(actual):
                continue

            if actual.es_meta():
                self.__accions = actual.accions_previes()
            else:
                for hijo in actual.genera_fills():
                    if hijo not in self.__tancats:
                        self.__oberts.put((hijo.valor(), hijo))
