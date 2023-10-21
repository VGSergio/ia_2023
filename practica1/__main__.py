import sys

sys.path.append("C:\\Users\\Sergio\\Desktop\\IA\\ia_2023")

from practica1 import agent, joc


def main():
    quatre = joc.Taulell([agent.AgentProfunditat("CPU_1")])
    # quatre = joc.Taulell([agent.AgentAEstrella("CPU_1")])
    # quatre = joc.Taulell([agent.AgentMinMax("CPU_1"), agent.AgentMinMax("CPU_2")])
    quatre.comencar()


if __name__ == "__main__":
    main()
