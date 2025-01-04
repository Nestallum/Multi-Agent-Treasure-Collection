
from Environment import Environment
from MyAgentGold import  MyAgentGold
from MyAgentChest import MyAgentChest
from MyAgentStones import MyAgentStones
from Treasure import Treasure
from Graphics import Graphics
import random

horizon = 100

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

            elif(ligneSplit[1]=="pierres"):
                id = "agent" + str(cpt)
                agent = MyAgentStones(id, int(ligneSplit[2]), int(ligneSplit[3]), env, int(ligneSplit[4]))
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt = cpt + 1

            elif(ligneSplit[1] == "ouvr"):
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
    for a in lAg.values() :
        print(a)

    # Initialisation de l'interface graphique
    graphics = Graphics(env)

    # make the agents plan their actions (off-line phase) TO COMPLETE
    # make the agents execute their plans
    for t in range(horizon):
        if t % 10 == 0:
            env.gen_new_treasures(random.randint(0, 5), 7)

        conflict_free = False

        # Step 1: Agents declare their intentions
        # Each agent broadcasts its planned movement or stationary intention to others.
        for agent in lAg.values():
            agent.broadcast_intention()

        # Step 2: Resolve conflicts
        # Continue resolving conflicts until all agents are conflict-free.
        while not conflict_free:
            for agent in lAg.values():
                agent.resolve_conflicts()  # Each agent processes its mailbox and adjusts its path if needed

            conflict_free = True  # Assume no conflicts remain

            # Check if any agent still has unresolved messages
            for agent in lAg.values():
                if len(agent.mailBox) != 0:  # If any mailbox is not empty, there are still conflicts
                    conflict_free = False

        # Step 3: Agents take actions
        # After resolving conflicts, each agent executes its planned action for the current time step.
        for agent in lAg.values():
            agent.do_policy()

        # Update display and environment
        # Print the current state of the environment and update the graphical display.
        print(env)
        graphics.update_display(env)
    # print each agent's score
    print("\n\n")
    for agent in lAg.values():
        if (agent.getType()==0) :
            print(f"Agent ID: {agent.getId()} | Treasures Unlocked: {agent.getScore()}")
        else :
            print(f"Agent ID: {agent.getId()} | Resources Collected: {agent.getScore()}")
            
    print("\n\n******* SCORE TOTAL : {}".format(env.getScore()))

main()
