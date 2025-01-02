import math
import random
from MyAgent import MyAgent


#inherits MyAgent

class MyAgentChest(MyAgent) :
    def __init__(self, id, initX, initY, env):
        MyAgent.__init__(self, id, initX, initY, env)
        self.opened = False
        

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
        if self.opened:
            self.opened = False
            if not self.task_in_progress:  # A ouvert mais n'a pas bougé, doit se déplacer pour ne pas gêner
                # Trouver le coffre ouvert le plus proche
                min_distance = math.inf
                best_open_chest = None

                for x in range(self.env.tailleX):
                    for y in range(self.env.tailleY):
                        if (
                            self.env.grilleTres[x][y] is not None 
                            and self.env.grilleTres[x][y].getValue() == 0  # Vérifie si c'est un coffre déjà ouvert
                            and (x, y) not in self.forbidden_moves 
                            and self.env.grilleAgent[x][y] is None  # La case n'est pas interdite
                        ):
                            distance = self.distance(self.posX, self.posY, x, y)
                            if distance < min_distance:
                                min_distance = distance
                                best_open_chest = (x, y)

                if best_open_chest:
                    # Se déplacer vers le coffre déjà ouvert le plus proche
                    chest_x, chest_y = best_open_chest
                    self.move(self.posX, self.posY, chest_x, chest_y)
                else:
                    # Sinon, se déplacer d'une case aléatoire libre
                    directions = [
                        (-1, 0), (1, 0),  # North, South
                        (0, -1), (0, 1),  # West, East
                        (-1, -1), (-1, 1),  # North-West, North-East
                        (1, -1), (1, 1)    # South-West, South-East
                    ]  # Déplacements possibles

                    random.shuffle(directions)  # Mélange les directions pour ajouter de l'aléatoire

                    for dx, dy in directions:
                        new_x, new_y = self.posX + dx, self.posY + dy
                        # Vérifie si la position est valide et libre
                        if (
                            0 <= new_x < self.env.tailleX
                            and 0 <= new_y < self.env.tailleY
                            and self.env.grilleAgent[new_x][new_y] is None
                            and (new_x, new_y) not in self.forbidden_moves
                        ):
                            self.move(self.posX, self.posY, new_x, new_y)
                            break

        if self.task_in_progress:
            if len(path) == 0:  # Arrivé à la position de la tâche
                self.open()
                self.task_in_progress = False
                self.opened = True
            else:  # Avance sur son chemin
                next_x, next_y = path[0]
                current_x, current_y = self.getPos()
                next_move = self.move(self.posX, self.posY, next_x, next_y)
                if next_move == 1 or (current_x,current_y) == self.getPos():  # succès
                    path.pop(0)

    def fill_tasks(self):
        treasures = []
        for x in range(len(self.env.grilleTres)):  # Parcourt les lignes
            for y in range(len(self.env.grilleTres[x])):  # Parcourt les colonnes   
                treasure = self.env.grilleTres[x][y]
                if treasure is not None and not treasure.getValue() == 0:  # Vérifie s'il y a un trésor qui n'est pas vide
                    if (x,y) not in self.other_agents_tasks: # Si le trésor n'est pas déjà affecté à un autre agent
                        if not treasure.isOpen():
                            treasures.append((x, y))  # Ajoute (x, y) coordonnées du trésor à la liste
        self.tasks = treasures

    def is_other_occuped(self):
        if(not self.other_agents_tasks == []): # l'autre agent est peut être occupé
            x, y = self.other_agents_tasks[-1] # on récupère la tâche de l'autre agent
            if not self.env.grilleTres[x][y].isOpen(): # l'agent n'a pas encore ouvert le coffre
                return True
        return False
    
    def do_policy(self):
        if(self.task_in_progress): # Agent en cours de progression
            self.next_move(self.task_path)
        else:
            self.fill_tasks() # Agent libre remplit sa liste de tâche
            task = self.task_finding()
            if(task is None):
                self.next_move(self.task_path) # Se décale pour ne pas gêner ou reste sur place s'il n'est pas sur un coffre
            else:
                self.find_best_path(task) # rempli le chemin de l'agent
                self.task_in_progress = True
                self.next_move(self.task_path)
        self.forbidden_moves = []
                 
                     