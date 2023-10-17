from collections import deque

from ia_2022 import entorn
from quiques.agent import Barca, Estat
from quiques.entorn import AccionsBarca, SENSOR


class BarcaAmplada(Barca):
    def __init__(self):
        super(BarcaAmplada, self).__init__()
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        if self.__accions is None:
            self._cerca(
                Estat(
                    percepcio[SENSOR.LLOC],
                    percepcio[SENSOR.LLOP_ESQ],
                    percepcio[SENSOR.QUICA_ESQ],
                )
            )

        return (
            (AccionsBarca.MOURE, self.__accions.pop())
            if self.__accions
            else AccionsBarca.ATURAR
        )

    def _cerca(self, estat: Estat):
        self.__oberts = deque([estat])
        self.__tancats = set()

        while self.__oberts and self.__accions is None:
            actual = self.__oberts.popleft()

            if self.__tancats.add(actual):
                continue

            if actual.es_meta():
                self.__accions = actual.accions_previes
            else:
                self.__oberts.extend(
                    [
                        hijo
                        for hijo in actual.genera_fill()
                        if hijo.es_segur() and hijo not in self.__tancats
                    ]
                )
