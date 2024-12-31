from MyAgent import MyAgent


#inherits MyAgent

class MyAgentChest(MyAgent) :
    def __init__(self, id, initX, initY, env):
        MyAgent.__init__(self, id, initX, initY, env)

    # open a chest
    def open(self):
        self.env.open(self, self.posX, self.posY)

    # the agent do not hold some treasure
    def getTreasure(self):
        return 0
    
    #return the agent's type
    def getType(self):
        return 0

    def __str__(self):

        res = "agent Chest "+ self.id + " (" + str(self.posX) + " , " + str(self.posY) + ")"
        return res
    
    # return next move and pop it from path
    def next_move(self, path):
        if len(path) == 0: # Arrivé à la position de la tâche
            self.open()
            self.task_in_progress = False
        else: # Avance sur son chemin
            next_x, next_y = path[0]
            move_ok = self.move(self.posX, self.posY, next_x, next_y)
            if(move_ok == 1): # succès
                path.pop(0)

    def fill_tasks(self):
        treasures = []
        for x in range(len(self.env.grilleTres)):  # Parcourt les lignes
            for y in range(len(self.env.grilleTres[x])):  # Parcourt les colonnes   
                treasure = self.env.grilleTres[x][y]
                if treasure is not None and not treasure.getValue() == 0:  # Vérifie s'il y a un trésor qui n'est pas vide
                    if (x,y) not in self.other_agents_tasks: # Si le trésor n'est pas déjà affecté à un autre agent
                        if not treasure.isOpen() and self.getType() == 0:
                            treasures.append((x, y))  # Ajoute (x, y) coordonnées du trésor à la liste
        self.tasks = treasures

    def is_other_occuped(self):
        if(not self.other_agents_tasks == []): # l'autre agent est peut être occupé
            x, y = self.other_agents_tasks[-1] # on récupère la tâche de l'autre agent
            if not self.env.grilleTres[x][y].isOpen(): # l'agent n'a pas encore ouvert le coffre
                return True
        return False