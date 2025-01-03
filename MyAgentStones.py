from MyAgent import MyAgent
import math


#inherits MyAgent

class MyAgentStones(MyAgent):

    def __init__(self, id, initX, initY, env, capacity):
        MyAgent.__init__(self, id, initX, initY, env)
        self.stone = 0 # the quantity of stone collected and not unloaded yet
        self.backPack = capacity #capacity of the agent's back pack
        self.unloaded = False

    #return quantity of stone collected and not unloaded yet
    def getTreasure(self):
        return self.stone

    #unload stone in the pack back at the current position
    def unload(self):
        self.env.unload(self)
        self.score = self.score + self.stone
        self.stone = 0

    #return the agent's type
    def getType(self):
        return 2

    # add some stone to the backpack of the agent (quantity t)
    # if the quantity exceeds the back pack capacity, the remaining is lost
    def addTreasure (self, t):
        if (self.stone+t <= self.backPack) :
            self.stone = self.stone + t
        else :
            self.stone = self.backPack


    #load the treasure at the current position
    def load(self,env):
        env.load(self)

    def __str__(self):
        res = "agent stone "+  self.id + " ("+ str(self.posX) + " , " + str(self.posY) + ")"
        return res
    
    # return next move and pop it from path
    def next_move(self, path):
        if len(path) == 0: # Arrivé à la position de la tâche
            if(self.env.posUnload == self.getPos()):
                self.unload()
                self.unloaded = True
            else :
                self.load(self.env)
            self.task_in_progress = False
        # else: # Avance sur son chemin
        #     next_x, next_y = path[0]
        #     if((next_x, next_y) == self.getPos()): # si le prochain move est sur la même case courante
        #         path.pop(0) # ne bouge pas
        #     else:
        #         move_ok = self.move(self.posX, self.posY, next_x, next_y)
        #         if(move_ok == 1): # succès
        #             path.pop(0)
        else:  # Avance sur son chemin
            next_x, next_y = path[0]
            print("AVANCE SUR SON CHEMIN")
            current_x, current_y = self.getPos()
            next_move = self.move(self.posX, self.posY, next_x, next_y)
            if next_move == 1 or (current_x,current_y) == self.task_path[0]:  # succès
                print("SUCCES")
                path.pop(0)


    def fill_tasks(self):
        treasures = []
        for x in range(len(self.env.grilleTres)):  # Parcourt les lignes
            for y in range(len(self.env.grilleTres[x])):  # Parcourt les colonnes   
                treasure = self.env.grilleTres[x][y]
                if treasure is not None and not treasure.getValue() == 0:  # Vérifie s'il y a un trésor qui n'est pas vide
                    if (x,y) not in self.other_agents_tasks: # Si le trésor n'est pas déjà affecté à un autre agent
                        if treasure.isOpen() and treasure.getType() == 2:
                            treasures.append((x, y))  # Ajoute (x, y) coordonnées du trésor à la liste
        self.tasks = treasures

    def is_other_occuped(self):
        if(not self.other_agents_tasks == []): # l'autre agent est peut être occupé
            x, y = self.other_agents_tasks[-1] # on récupère la tâche de l'autre agent
            if self.env.grilleTres[x][y] is not None and not self.env.grilleTres[x][y].getValue() == 0: # l'agent n'a pas encore ouvert le coffre
                return True
        return False
    
    def do_policy(self):
        print(self.getId(), self.task_path)
        print(self.getId(), self.task_in_progress)
        print(self.backPack)
        print(f"position : {self.getPos()}")
        self.forbidden_moves = []
        # Si l'agent a un butin > à la moitié de son backpack, il part unload
        if not self.task_in_progress and self.backPack*0.5 < self.stone :
            task = self.env.posUnload
            self.find_best_path(task)
            # self.go_to_unload()
            self.task_in_progress = True   

        # Si l'agent a unload et n'a pas de tâche, il doit soit trouver une nouvelle tâche, soit aller au garage
        elif(self.unloaded and not self.task_in_progress):
            self.unloaded = False
            self.fill_tasks() 
            task = self.task_finding()
            print(f'{self.getId()} filltask {self.tasks}')
            print(f"{self.getId()} task {task}")
            if(task is None): # Aller au garage
                # posY = int(self.getId()[-1]) % 4
                # self.find_best_path((11, posY)) # Se garer en position 0-1,2,3,4 selon l'agent (ne bloque pas l'entrée 0-5 du coffre)
                # self.task_in_progress = True 
                # self.next_move(self.task_path)

                min_distance = math.inf
                best_parking_spot = None

                for x in range(self.env.tailleX):
                    for y in range(self.env.tailleY):
                        # Vérifie que la case est vide, qu'elle ne bloque pas le dépôt, et qu'elle est à au moins 3 cases sur les deux axes
                        if (
                            self.env.grilleAgent[x][y] is None and self.env.grilleTres[x][y] is not None and self.env.grilleTres[x][y].getValue() == 0  # La case est vide
                            and (abs(x - 5) >= 3 and abs(y - 0) >= 3)  # À au moins 3 cases du dépôt (5, 0)
                        ):
                            distance = self.distance(self.posX, self.posY, x, y)
                            if distance < min_distance:
                                min_distance = distance
                                best_parking_spot = (x, y)

                if best_parking_spot:
                    self.find_best_path(best_parking_spot)  # Trouve le chemin vers le meilleur coffre
                    self.task_in_progress = True
                else:
                    posY = int(self.getId()[-1]) % 4
                    self.find_best_path((11, posY)) # Se garer en position 0-1,2,3,4 selon l'agent (ne bloque pas l'entrée 0-5 du coffre)
                    self.task_in_progress = True 

        # Continue son chemin
        if(not self.unloaded and self.task_in_progress): # Agent en cours de progression
            self.next_move(self.task_path)
        elif not self.task_in_progress:
            self.fill_tasks() # Agent libre remplit sa liste de tâche
            self.unloaded = False
            task = self.task_finding()
            if(task is None):
                print(f"Agent{self.getId} - aucune action possible.")
            else:
                self.find_best_path(task) # rempli le chemin de l'agent
                self.task_in_progress = True
                self.next_move(self.task_path) 