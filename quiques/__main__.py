import sys
sys.path.append("C:\\Users\\Sergio\\Desktop\\ia_2023")

from quiques import agent_amplada, agent_profunditat, joc

def main():
    # barca = agent_amplada.BarcaAmplada()
    barca = agent_profunditat.BarcaProfunditat()
    illes = joc.Illes([barca])
    illes.comencar()


if __name__ == "__main__":
    main()
