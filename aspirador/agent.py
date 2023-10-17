import abc

import pygame

from aspirador.entorn import AccionsAspirador, Sensor, EstatHabitacio, Localitzacio
from ia_2022 import agent
from ia_2022 import entorn


class Aspirador(agent.Agent):
    def __init__(self):
        super().__init__(long_memoria=1)

    def pinta(self, display):
        img = pygame.image.load("../assets/aspirador/sprite.png")
        img = pygame.transform.scale(img, (100, 100))
        display.blit(img, self._posicio_pintar)

    @abc.abstractmethod
    def actua(self, percepcio: entorn.Percepcio) -> entorn.Accio:
        pass


class AspiradorTaula(Aspirador):
    TAULA = {
        (Localitzacio.HABITACIO_ESQ, EstatHabitacio.NET): AccionsAspirador.DRETA,
        (Localitzacio.HABITACIO_ESQ, EstatHabitacio.BRUT): AccionsAspirador.ASPIRA,
        (Localitzacio.HABITACIO_DRET, EstatHabitacio.NET): AccionsAspirador.ESQUERRA,
        (Localitzacio.HABITACIO_DRET, EstatHabitacio.BRUT): AccionsAspirador.ASPIRA,
    }

    def actua(self, percepcio: entorn.Percepcio) -> entorn.Accio:
        return AspiradorTaula.TAULA[(percepcio[Sensor.LLOC], percepcio[Sensor.ESTAT])]


class AspiradorReflex(Aspirador):
    def actua(self, percepcio: entorn.Percepcio) -> entorn.Accio:
        if percepcio[Sensor.ESTAT] == EstatHabitacio.BRUT:
            return AccionsAspirador.ASPIRA
        else:
            if percepcio[Sensor.LLOC] == Localitzacio.HABITACIO_ESQ:
                return AccionsAspirador.DRETA
            else:
                return AccionsAspirador.ESQUERRA


class AspiradorMemoria(Aspirador):
    def actua(self, percepcio: entorn.Percepcio) -> entorn.Accio:
        memoria = self.get_memoria(1)

        if memoria is None:
            memoria = {
                Localitzacio.HABITACIO_ESQ: False,
                Localitzacio.HABITACIO_DRET: False,
            }

        if percepcio[Sensor.ESTAT] == EstatHabitacio.BRUT:
            return AccionsAspirador.ASPIRA

        memoria[percepcio[Sensor.LLOC]] = True

        self.set_memoria(memoria)

        if memoria[Localitzacio.HABITACIO_ESQ] and memoria[Localitzacio.HABITACIO_DRET]:
            return AccionsAspirador.ATURA

        if percepcio[Sensor.LLOC] == Localitzacio.HABITACIO_ESQ:
            return AccionsAspirador.DRETA
        else:
            return AccionsAspirador.ESQUERRA
