import sys
sys.path.append("C:\\Users\\Sergio\\Desktop\\ia_2023")

from aspirador import agent, joc


def main():
    aspirador = agent.AspiradorMemoria()
    hab = joc.Casa([aspirador])
    hab.comencar()


if __name__ == "__main__":
    main()
