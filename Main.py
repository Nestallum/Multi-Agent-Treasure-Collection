
from Environment import Environment
from MyAgentGold import  MyAgentGold
from MyAgentChest import MyAgentChest
from MyAgentStones import MyAgentStones
from Treasure import Treasure
from Graphics import Graphics
import random

horizon = 200

def loadFileConfig(nameFile) :

    file = open(nameFile)
    lines = file.readlines()
    tailleEnv = lines[1].split()
    tailleX = int(tailleEnv[0])
    tailleY = int(tailleEnv[1])
    zoneDepot = lines[3].split()
    cPosDepot =  (int(zoneDepot[0]), int(zoneDepot[1]))
    dictAgent = dict()


    env = Environment(tailleX, tailleY, cPosDepot)
    cpt = 0

    for ligne in lines[4:] :
        ligneSplit = ligne.split(":")
        if(ligneSplit[0]=="tres"): # new treasure
            if(ligneSplit[1]=="or"):
                env.addTreasure(Treasure(1, int(ligneSplit[4])), int(ligneSplit[2]), int(ligneSplit[3]))
            elif(ligneSplit[1]=="pierres"):
                env.addTreasure(Treasure(2, int(ligneSplit[4])), int(ligneSplit[2]), int(ligneSplit[3]))

        elif(ligneSplit[0]=="AG") : #new agent
            if(ligneSplit[1]=="or"):
                id = "agent" + str(cpt)
                agent = MyAgentGold(id, int(ligneSplit[2]), int(ligneSplit[3]), env, int(ligneSplit[4]))
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt = cpt +1

            if(ligneSplit[1]=="pierres"):
                id = "agent" + str(cpt)
                agent = MyAgentStones(id, int(ligneSplit[2]), int(ligneSplit[3]), env, int(ligneSplit[4]))
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt = cpt + 1

            if (ligneSplit[1] == "ouvr"):
                id = "agent" + str(cpt)
                agent = MyAgentChest(id, int(ligneSplit[2]), int(ligneSplit[3]), env)
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt = cpt + 1

    file.close()
    env.addAgentSet(dictAgent)

    return (env, dictAgent)

def main():
    env, lAg = loadFileConfig("env1.txt")
    print(env)
    # # Initialiser l'interface graphique
    graphics = Graphics(env)
    
    ##############################################
    ####### TODO #################################
    ##############################################

    # make the agents plan their actions (off-line phase) TO COMPLETE


    # make the agents execute their plans
    for t in range(horizon):
        if t % 10 == 0:
            env.gen_new_treasures(random.randint(0, 5), 7)

        conflict_free = False

        # Étape 1 : Les agents déclarent leurs intentions
        for a in lAg.values():
            a.declare_intention()

        # Étape 2 : Résolution des conflits
        while not conflict_free:
            for a in lAg.values():
                a.resolve_conflicts()
            conflict_free = True  # On fait l'hypothèse qu'il n'y a plus de conflits
            for a in lAg.values():
                if len(a.mailBox) != 0:  # Si au moins un agent a un conflit
                    conflict_free = False

        # Étape 3 : Actions des agents
        for a in lAg.values():
            a.do_policy()  # Action de l'agent au temps t

        print(env)
        graphics.update_display(env)


    # print each agent's score
    print("\n\n")
    for agent in lAg.values():
        if (agent.getId()==0) :
            print(f"Agent ID: {agent.getId()} | Treasures Opened: {agent.getScore()}")
        else :
            print(f"Agent ID: {agent.getId()} | Resources Collected: {agent.getScore()}")
            
    print("\n\n******* SCORE TOTAL : {}".format(env.getScore()))

main()
