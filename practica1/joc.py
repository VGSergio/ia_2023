import pygame

from ia_2022 import agent as agent_lib
from ia_2022 import entorn, joc
from practica1.entorn import Accio, SENSOR, TipusCasella


class Agent(agent_lib.Agent):
    random__used = set()

    def __init__(self, nom: str):
        super().__init__(long_memoria=1)

        self.__nom = nom
        self.jugador = None

    def pinta(self, display):
        pass

    def set_jugador_tipus(self, tipus: TipusCasella):
        self.jugador = tipus

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        return Accio.ESPERAR

    @property
    def nom(self):
        return self.__nom


def drawX(window, x, y):
    pygame.draw.lines(window, (255, 0, 0), True, [(x - 45, y - 45), (x + 45, y + 45)], 5)
    pygame.draw.lines(window, (255, 0, 0), True, [(x - 45, y + 45), (x + 50, y - 45)], 5)


class Casella:

    def __init__(
            self,
            tipus: TipusCasella = TipusCasella.LLIURE,
    ):
        self.tipus: TipusCasella = tipus

    def draw(self, window, x, y):
        pygame.draw.rect(
            window,
            pygame.Color(0, 0, 0),
            pygame.Rect(x * 100, y * 100, 100, 100),
            2,
        )

        if self.tipus is TipusCasella.CREU:
            drawX(window, (x * 100) + 50, (y * 100) + 50)
        if self.tipus is TipusCasella.CARA:
            pygame.draw.circle(window, (0, 0, 255), ((x * 100) + 50, (y * 100) + 50), 40, width=5)

    def posa(self, tipus):
        if self.tipus is not TipusCasella.LLIURE:
            raise Exception("Has fet trampes: aquesta casella ja està ocupada")
        self.tipus = tipus

    def __str__(self):
        if self.tipus is TipusCasella.CREU:
            return "X"
        elif self.tipus is TipusCasella.CARA:
            return "C"
        else:
            return " "


class Taulell(joc.Joc):
    def __init__(self, agents: list[Agent] | Agent, mida_taulell: tuple[int, int] = (8, 8)):
        super(Taulell, self).__init__((800, 800), agents, title="Pràctica 1")

        self.__caselles = []
        self.__mida_taulell = mida_taulell

        for x in range(mida_taulell[0]):
            caselles_col = []
            for y in range(mida_taulell[1]):
                tipus = TipusCasella.LLIURE
                caselles_col.append(Casella(tipus))
            self.__caselles.append(caselles_col)

        for agent, tipus in zip(agents, [TipusCasella.CARA, TipusCasella.CREU]):
            agent.set_jugador_tipus(tipus)

        if not isinstance(agents, list):
            agents = [agents]

        self._agents = agents
        self.torn = 0
        self.acabat = False

    def _aplica(
            self, accio: entorn.Accio, params=None, agent_actual: Agent = None
    ) -> None:
        if not self.acabat:
            if accio not in Accio:
                raise ValueError(f"Acció no existent en aquest joc: {accio}")

            if accio is not Accio.ESPERAR and not isinstance(params, tuple):
                raise ValueError("Paràmetres incorrectes")

            if accio is Accio.POSAR:
                pos_x, pos_y = params
                if not (0 <= pos_x < len(self.__caselles) and 0 <= pos_y < len(
                        self.__caselles[0])):
                    raise ValueError(f"Posició {params} fora dels límits")

                self.__caselles[pos_x][pos_y].posa(agent_actual.jugador)
                self.acabat = self.__ha_guanyat((pos_x, pos_y))

            if self.acabat:
                print(f"Agent {agent_actual.nom} ha guanyat")
            self.torn += 1

    def _draw(self) -> None:
        super(Taulell, self)._draw()
        window = self._game_window
        window.fill(pygame.Color(255, 255, 255))

        for x in range(len(self.__caselles)):
            for y in range(len(self.__caselles[0])):
                self.__caselles[x][y].draw(window, x, y)

    def __ha_guanyat(self, posicio: tuple) -> bool:
        pos_x, pos_y = posicio

        horizontal_check = self.__linear_check(pos_x, pos_y, self.agent_actual)
        vertical_check = self.__linear_check(pos_y, pos_x, self.agent_actual, reverse=True)

        diagonal_check_tl = self.__diagonal_check(pos_x, pos_y, self.agent_actual, (+1, -1))
        diagonal_check_tr = self.__diagonal_check(pos_x, pos_y, self.agent_actual, (+1, +1))

        return horizontal_check or vertical_check or diagonal_check_tl or diagonal_check_tr

    def __diagonal_check(self, pos_1, pos_2, agent, desp: tuple):
        continu = False
        count = 0
        best_lineal = 0

        for i, j in zip(
                range(pos_1 - (4 * desp[0]), pos_1 + (4 * desp[0]), desp[0]),
                range(pos_2 - (4 * desp[1]), pos_2 + (4 * desp[1]), desp[1])
        ):
            if not (0 <= i < len(self.__caselles) and 0 <= j < len(self.__caselles[0])):
                continue

            if self.__caselles[i][j].tipus is agent.jugador:
                if not continu:
                    continu = True
                count += 1
            else:
                continu = False
                if count > best_lineal:
                    best_lineal = count
                count = 0
        if count > best_lineal:
            best_lineal = count

        return best_lineal >= 4

    def __linear_check(self, pos_1, pos_2, agent, reverse=False) -> bool:
        continu = False
        count = 0
        best_lineal = 0
        for x in range(max(pos_1 - 4, 0), min(pos_1 + 4, self.__mida_taulell[0]), 1):
            if reverse:
                tipus = self.__caselles[pos_2][x].tipus
            else:
                tipus = self.__caselles[x][pos_2].tipus

            if tipus is agent.jugador:
                if not continu:
                    continu = True
                count += 1
            else:
                continu = False
                if count > best_lineal:
                    best_lineal = count
                count = 0

        if count > best_lineal:
            best_lineal = count

        return best_lineal >= 4

    @property
    def agent_actual(self):
        return self._agents[self.torn % len(self._agents)]

    def percepcio(self) -> entorn.Percepcio:
        percep_dict = {
            SENSOR.TAULELL: [[c.tipus for c in row] for row in self.__caselles],
            SENSOR.MIDA: self.__mida_taulell
        }

        return entorn.Percepcio(
            percep_dict
        )
