import sys
sys.path.append("C:\\Users\\Sergio\\Desktop\\ia_2023")

from practica1 import agent, joc


def main():
    quatre = joc.Taulell([agent.AgentProfunditat("O")])
    quatre.comencar()


if __name__ == "__main__":
    main()
