""" Mòdul que conté l'agent per jugar al joc de les monedes.

Percepcions:
    ClauPercepcio.MONEDES
Solució:
    " XXXC"
"""

from queue import PriorityQueue

from ia_2022 import agent, entorn
from monedes.entorn import AccionsMoneda, SENSOR

SOLUCIO = " XXXC"


class Estat:
    __acc_pos: list[tuple[AccionsMoneda, int]] = [
        (acc, i)
        for acc in AccionsMoneda
        for i in range(len(SOLUCIO))
        if acc != AccionsMoneda.RES
    ]

    def __init__(
        self,
        config: str,
        pare=None,
        accions_previes=None,
    ) -> None:
        self.__config = config
        self.__pare = pare
        self.__accions_previes = accions_previes or []
        self.__cost = pare.__cost + 1 if pare else 0
        self.__heuristica = self.__calcul_heuristica()

    def __hash__(self) -> int:
        return hash(self.__config)

    def __eq__(self, other: "Estat") -> bool:
        return self.__config == other.__config

    def __str__(self) -> str:
        return f"{self.__config}"

    def __repr__(self) -> str:
        return f"{self.__config}"

    def __lt__(self, other: "Estat") -> int:
        return self.__heuristica - other.__heuristica

    def __legal(self, accio: tuple[AccionsMoneda, int]) -> bool:
        accioMoneda, idx_moneda = accio
        dist = abs(idx_moneda - self.__config.index(" "))

        match accioMoneda:
            case AccionsMoneda.GIRAR:
                return dist != 0
            case AccionsMoneda.DESPLACAR:
                return dist == 1
            case AccionsMoneda.BOTAR:
                return dist == 2

    def __fer_accio(self, accio: tuple[AccionsMoneda, int]) -> str:
        accioMoneda, idx_moneda = accio
        configuracio = list(self.__config)

        if accioMoneda in (AccionsMoneda.GIRAR, AccionsMoneda.BOTAR):
            configuracio[idx_moneda] = "C" if configuracio[idx_moneda] == "X" else "X"

        if accioMoneda in (AccionsMoneda.DESPLACAR, AccionsMoneda.BOTAR):
            idx_blanc = self.__config.index(" ")
            configuracio[idx_blanc], configuracio[idx_moneda] = (
                configuracio[idx_moneda],
                configuracio[idx_blanc],
            )

        return "".join(configuracio)

    def __calcul_heuristica(self) -> int:
        dist_blanc = abs(self.__config.index(" ") - SOLUCIO.index(" "))
        dist_caract = abs(self.__config.count("C") - SOLUCIO.count("C")) + abs(
            self.__config.count("X") - SOLUCIO.count("X")
        )
        return dist_blanc + dist_caract

    def accions_previes(self):
        return self.__accions_previes

    def es_meta(self) -> bool:
        return self.__config == SOLUCIO

    def genera_fills(self) -> list:
        return [
            Estat(
                config=self.__fer_accio(accio),
                pare=self,
                accions_previes=self.__accions_previes + [accio],
            )
            for accio in self.__acc_pos
            if self.__legal(accio)
        ]

    def valor(self) -> int:
        return self.__cost + self.__heuristica


class AgentMoneda(agent.Agent):
    def __init__(self):
        super().__init__(long_memoria=0)
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    def pinta(self, display):
        print(self._posicio_pintar)

    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        if self.__accions is None:
            self._cerca(Estat(percepcio[SENSOR.MONEDES]))

        return self.__accions.pop(0) if self.__accions else AccionsMoneda.RES

    def _cerca(self, estat: Estat):
        self.__oberts = PriorityQueue()
        self.__tancats = set()

        self.__oberts.put((estat.valor(), estat))

        while not self.__oberts.empty() and self.__accions is None:
            _, actual = self.__oberts.get()

            if actual in self.__tancats:
                continue

            self.__tancats.add(actual)

            if actual.es_meta():
                self.__accions = actual.accions_previes()
            else:
                for hijo in actual.genera_fills():
                    if hijo not in self.__tancats:
                        self.__oberts.put((hijo.valor(), hijo))
