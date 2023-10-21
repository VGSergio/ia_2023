from collections import deque
from typing import List, Optional, Tuple
from queue import PriorityQueue
import time

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import Accio, SENSOR, TipusCasella

# Definim un tipus per la colocació de una peça
TipusPosarPeça = Tuple[Accio, Tuple[int, int]]


class EstatBase:
    def __init__(
        self,
        taulell: List[List[TipusCasella]],
        tipus: TipusCasella,
        n: int,
        pare: Optional["EstatBase"] = None,
        accions_previes: Optional[List[TipusPosarPeça]] = None,
    ) -> None:
        self._taulell = taulell
        self._n = n
        self._tipus = tipus
        self._pare = pare
        self._accions_previes = accions_previes or []
        self._acc_pos = [
            (Accio.POSAR, (row, col)) for row in range(n) for col in range(n)
        ]

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: "EstatBase") -> bool:
        return self._taulell == other._taulell

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
                    for row in self._taulell
                ]
            )
            + "\n"
        )

    def __repr__(self) -> str:
        return str(self)

    # Devuelve una copia del estado actual actualizado con el movimiento pasado por argumento
    def __fer_accio(
        self, accio: Tuple[Accio.POSAR, Tuple[int, int]]
    ) -> List[List[TipusCasella]]:
        _, pos = accio
        taulell = [row[:] for row in self._taulell]  # Copies the grid
        taulell[pos[0]][pos[1]] = self._tipus
        return taulell

    # Comprueba que la casilla este libre
    def __legal(self, accio: Tuple[Accio.POSAR, Tuple[int, int]]) -> bool:
        _, pos = accio
        return self._taulell[pos[0]][pos[1]] == TipusCasella.LLIURE

    def _cambia_jugador(self) -> TipusCasella:
        return (
            TipusCasella.CARA if self._tipus == TipusCasella.CREU else TipusCasella.CREU
        )

    def accions_previes(self) -> List[TipusPosarPeça]:
        return self._accions_previes

    # Empezando en la esquina superior izquierda, comprueba para cada casilla si hay un grupo de 4 piezas iguales contiguas.
    # Al empezar en la esquina superior izquierda no comprobamos la parte izquierda ni superior de la casilla analizada
    def es_meta(self) -> Tuple[bool, int]:
        n = self._n
        taulell = self._taulell
        final = True
        contrari = self._cambia_jugador()

        for i in range(n):
            for j in range(n):
                casella = taulell[i][j]

                if casella == TipusCasella.LLIURE:
                    final = False
                    continue

                directions = [
                    (0, 1),  # right
                    (1, 0),  # down
                    (-1, 1),  # diagonal top right
                    (1, 1),  # diagonal bottom right
                ]

                for dx, dy in directions:
                    count = 0
                    x, y = i, j

                    while 0 <= x < n and 0 <= y < n:
                        if taulell[x][y] == self._tipus:
                            count += 1
                        if taulell[x][y] == contrari:
                            count -= 1
                        x, y = x + dx, y + dy

                    if abs(count) == 4:
                        return (True, 1 if count == 4 else -1)

        return (final, 0)

    def genera_fills(self, cambia_jugador: bool = False) -> List["EstatBase"]:
        return [
            self.__class__(
                taulell=self.__fer_accio(accio),
                n=self._n,
                tipus=self._tipus if not cambia_jugador else self._cambia_jugador(),
                pare=self,
                accions_previes=self._accions_previes + [accio],
            )
            for accio in self._acc_pos
            if self.__legal(accio)
        ]


class EstatProfunditat(EstatBase):
    def __init__(
        self,
        taulell: List[List[TipusCasella]],
        tipus: TipusCasella,
        n: int = None,
        pare: Optional[EstatBase] = None,
        accions_previes: Optional[List[TipusPosarPeça]] = None,
    ) -> None:
        super().__init__(taulell, tipus, n, pare, accions_previes)


class EstatAEstrella(EstatBase):
    def __init__(
        self,
        taulell: List[List[TipusCasella]],
        tipus: TipusCasella,
        n: int = None,
        pare: Optional[EstatBase] = None,
        accions_previes: Optional[List[TipusPosarPeça]] = None,
    ) -> None:
        super().__init__(taulell, tipus, n, pare, accions_previes)
        self.__cost = pare.__cost + 1 if pare else 0
        self.__heuristica = self._calcul_heuristica() if accions_previes else 1000

    def __lt__(self, other: "EstatAEstrella") -> int:
        return self.__heuristica - other.__heuristica

    """
        Cuenta cuentas piezas del mismo tipo hay en cada una de las direcciones 
        El máximo de piezas que puede contar es de (4 (conecta 4) - 1 (la pieza colocada)) * 8 (direcciones posibles)
        Para que la heuristica sea menor cuanto más buena sea la posición devolvemos max - count
    """

    def _calcul_heuristica(self) -> int:
        n = self._n
        taulell = self._taulell
        row, col = self._accions_previes[-1][1]
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

            while max(0, row - 3) <= x < min(n, row + 3) and max(0, col - 3) <= y < min(
                n, col + 3
            ):
                if casella == taulell[x][y]:
                    count += 1
                x, y = x + dx, y + dy

        return 3 * len(directions) - count

    def valor(self) -> int:
        return self.__cost + self.__heuristica


class EstatMinMax(EstatBase):
    def __init__(
        self,
        taulell: List[List[TipusCasella]],
        tipus: TipusCasella,
        n: int = None,
        pare: Optional[EstatBase] = None,
        accions_previes: Optional[List[TipusPosarPeça]] = None,
    ) -> None:
        super().__init__(taulell, tipus, n, pare, accions_previes)

    def minimax(self, alpha, beta, maximizingPlayer, visitedNodes: set):
        final, score = self.es_meta()
        if final or not visitedNodes.add(self):
            return score

        MAX = 10000
        if maximizingPlayer:
            max_eval = -MAX
            for fill in self.genera_fills(True):
                eval = fill.minimax(alpha, beta, not maximizingPlayer, visitedNodes)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break
            return max_eval
        else:
            min_eval = MAX
            for fill in self.genera_fills(True):
                eval = fill.minimax(alpha, beta, not maximizingPlayer, visitedNodes)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if alpha >= beta:
                    break
            return min_eval

    def millor_accio(self):
        MAX = 10000
        millor_accio = None
        millor_valor = -MAX
        visited = set()
        visited.add(self)
        for fill in self.genera_fills(True):
            eval = fill.minimax(-MAX, MAX, False, visited)
            if eval > millor_valor:
                millor_valor = eval
                millor_accio = fill._accions_previes[0]
        return millor_accio


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
    ) -> entorn.Accio | Tuple[entorn.Accio, object]:
        if self.__accions is None:
            self._cerca(
                EstatProfunditat(
                    taulell=percepcio[SENSOR.TAULELL],
                    n=percepcio[SENSOR.MIDA][0],
                    tipus=self.jugador,
                )
            )

        return self.__accions.pop(0) if self.__accions else Accio.ESPERAR

    def _cerca(self, estat: EstatProfunditat):
        self.__oberts = deque([estat])
        self.__tancats = set()

        while self.__oberts and self.__accions is None:
            actual = self.__oberts.popleft()

            if self.__tancats.add(actual):
                continue

            if actual.es_meta()[0]:
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
    ) -> entorn.Accio | Tuple[entorn.Accio, object]:
        if self.__accions is None:
            self._cerca(
                EstatAEstrella(
                    taulell=percepcio[SENSOR.TAULELL],
                    n=percepcio[SENSOR.MIDA][0],
                    tipus=self.jugador,
                )
            )

        return self.__accions.pop(0) if self.__accions else Accio.ESPERAR

    def _cerca(self, estat: EstatAEstrella):
        self.__oberts = PriorityQueue()
        self.__tancats = set()

        self.__oberts.put((estat.valor(), estat))

        while not self.__oberts.empty() and self.__accions is None:
            _, actual = self.__oberts.get()

            if self.__tancats.add(actual):
                continue

            if actual.es_meta()[0]:
                self.__accions = actual.accions_previes()
            else:
                for hijo in actual.genera_fills():
                    if hijo not in self.__tancats:
                        self.__oberts.put((hijo.valor(), hijo))


class AgentMinMax(joc.Agent):
    def __init__(self, nom):
        super(AgentMinMax, self).__init__(nom)

    def pinta(self, display):
        pass

    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | Tuple[entorn.Accio, object]:
        estat_actual = EstatMinMax(
            taulell=percepcio[SENSOR.TAULELL],
            n=percepcio[SENSOR.MIDA][0],
            tipus=self.jugador,
        )
        millor_accio = estat_actual.millor_accio()
        print(f"{self.jugador}, {millor_accio}")
        return millor_accio if millor_accio else Accio.ESPERAR
