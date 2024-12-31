import ast
import Environment
import math
from itertools import combinations
import math


class MyAgent:

    def __init__(self, id, initX, initY, env:Environment):
        self.id = id
        self.posX = initX
        self.posY = initY
        self.env = env
        self.mailBox = []
        self.tasks = []
        self.task_in_progress = False
        self.task_path = []
        self.other_agents_tasks = []
        self.forbidden_moves = []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.getId() == self.getId()
        return False

    #make the agent moves from (x1,y1) to (x2,y2)
    def move(self, x1, y1, x2, y2) :
        if x1 == self.posX and y1 == self.posY :
            #print("departure position OK")
            if self.env.move(self, x1, y1, x2, y2) :
                self.posX = x2
                self.posY = y2
                #print("deplacement OK")
                return 1
        return -1

    #return the id of the agent
    def getId(self):
        return self.id

    #return the position of the agent
    def getPos(self):
        return (self.posX, self.posY)

    # add a message to the agent's mailbox
    def receive(self, idReceiver, textContent):
        self.mailBox.append((idReceiver, textContent))

    #the agent reads a message in her mailbox (FIFO mailbox)
    #return a tuple (id of the sender, message  text content)
    def readMail (self):
        idSender, textContent = self.mailBox.pop(0)
        print("mail received from {} with content {}".format(idSender, textContent))
        return (idSender, textContent)

    #send a message to the agent whose id is idReceiver
    # the content of the message is some text
    def send(self, idReceiver, textContent):
        self.env.send(self.id, idReceiver, textContent)

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def find_nearest_task(self):
        
        if len(self.tasks) == 0:
            return
        
        min_distance = math.inf
        index_task = 0

        for idx, (x_task, y_task) in enumerate(self.tasks):
            distance = self.distance(self.posX, self.posY, x_task, y_task)
            if distance < min_distance :
                min_distance = distance
                index_task = idx

        return self.tasks[index_task], min_distance
    
    def find_best_path(self, task):
        if(task==None):
            return []
        x_task, y_task = task
        x_current, y_current = self.posX, self.posY
        path = [] 

        # Possible directions (8 directions : N, S, E, W, and diagonals)
        directions = [
            (-1, 0), (1, 0),  # North, South
            (0, -1), (0, 1),  # West, East
            (-1, -1), (-1, 1),  # North-West, North-East
            (1, -1), (1, 1)    # South-West, South-East
        ]

        while (x_current, y_current) != (x_task, y_task):
            best_distance = math.inf
            best_move = None

            for dx, dy in directions:
                x_next, y_next = x_current + dx, y_current + dy
                dist = self.distance(x_next, y_next, x_task, y_task)

                if dist < best_distance:
                    best_distance = dist
                    best_move = (x_next, y_next)

            path.append(best_move)
            x_current, y_current = best_move

        self.task_path = path


    def task_finding(self):
        env = self.env
        other = None
        
        # Aucune tâche dispo
        if len(self.tasks) == 0:
            return None

        # Au moins une tâche dispo
        # 2 possibilités : l'autre agent n'est pas dispo ou les deux sont disponibles
        # Trouver l'autre agent de même type
        for a in env.agentSet.values():
            if a.getType() == self.getType() and not self.__eq__(a):
                other = a
                break
        # Coordonnées de l'autre agent
        other_posX, other_posY = other.getPos()

        # Si l'autre est occupé on prend juste la tâche la plus proche
        if self.is_other_occuped():
            self.send(other.getId(),f"T_{self.find_nearest_task()[0]}")
            return self.find_nearest_task()[0]
        
        # Si les deux sont disponibles, il peut y avoir une ou plusieurs tâches :
        # Si une tâche à partager : Déterminer qui récupère la tâche
        if len(self.tasks) == 1:
            # Récupérer les coordonnées de la tâche unique
            task_X, task_Y = self.tasks[0]

            # Calculer les distances entre l'agent et la tâche, et entre l'autre agent et la tâche
            self_distance = self.distance(self.posX, self.posY, task_X, task_Y)
            other_distance = self.distance(other_posX, other_posY, task_X, task_Y)

            # Cas 1 : L'agent self est plus proche
            if self_distance < other_distance:
                self.send(other.getId(),f"T_{self.tasks[0]}")
                return self.tasks[0]

            # Cas 2 : Les deux agents sont à la même distance
            if self_distance == other_distance:
                # Le plus grand ID récupère la tâche
                if self.id > other.getId():
                    self.send(other.getId(),f"T_{self.tasks[0]}")
                    return self.tasks[0]

            # Cas 3 : L'autre agent est plus proche ou a un ID supérieur en cas d'égalité
              
            return None  # Aucune action pour self
        
        # Sinon, au moins 2 taches à partager
        # Initialisation pour la recherche de la meilleure combinaison
        min_distance = float('inf')
        best_task_for_self = None

        # Parcourir toutes les combinaisons de deux tâches
        for task1, task2 in combinations(self.tasks, 2):
            # Distance pour self vers task1 et other vers task2
            distance_self_to_task1 = self.distance(self.posX, self.posY, task1[0], task1[1])
            distance_other_to_task2 = self.distance(other_posX, other_posY, task2[0], task2[1])
            total_distance = distance_self_to_task1 + distance_other_to_task2

            # Distance pour self vers task2 et other vers task1
            distance_self_to_task2 = self.distance(self.posX, self.posY, task2[0], task2[1])
            distance_other_to_task1 = self.distance(other_posX, other_posY, task1[0], task1[1])
            swapped_total_distance = distance_self_to_task2 + distance_other_to_task1

            # Vérifier si cette combinaison est meilleure
            if total_distance < min_distance:
                min_distance = total_distance
                best_task_for_self = task1
                

            if swapped_total_distance < min_distance:
                min_distance = swapped_total_distance
                best_task_for_self = task2
                

        
        self.send(other.getId(),f"T_{best_task_for_self}")
        return best_task_for_self
     

    def __str__(self):
        res = self.id + " ("+ str(self.posX) + " , " + str(self.posY) + ")"
        return res
    
    def CloseAgent(self):
        list_ids = []
        for a in self.env.agentSet.values() :
            if(self.getId() != a.getId()):
                dist = self.distance(self.posX,self.posY,a.posX,a.posY)
                if(dist<=3):
                    list_ids.append(a.getId())
        return list_ids
    
    def MessagetoAll(self):
        for id in self.CloseAgent() :
            if(len(self.task_path)!=0):
                self.send(id,f"Move_{self.task_path[0]}")
            else:
                self.send(id,f"Fixe_{self.getPos()}")
    
    def readAllMail(self):
        while (len(self.mailBox) != 0) :
            id, content = self.readMail()
            if(content.split("_")[0]=="T"):
                # Utilisation de ast.literal_eval pour convertir la chaîne en tuple
                msg = ast.literal_eval(content.split("_")[1].strip())
                self.other_agents_tasks.append(msg)
                
            if(content.split("_")[0]=="Move"):
                if((len(self.task_path)!=0) ):
                    next_move_other=ast.literal_eval(content.split("_")[1].strip())
                    if(self.task_path[0]==next_move_other): # meme action
                        print("conflict") 
                        if(self.getId()<id):# plus grand id garde son coup l'autre change
                            print("conflict")
                            self.forbidden_moves.append(next_move_other)
                            self.task_path=self.conflict_handling(self.task_path[-1],self.forbidden_moves)
                            self.MessagetoAll()
                            
            # if(content.split("_")[0]=="Fixe"):
            #     if((len(self.task_path)!=0) ):
            #         next_move_other=ast.literal_eval(content.split("_")[1].strip())
            #         if(self.task_path[0]==next_move_other): # meme action
            #             print("conflict") 
            #             if(self.getId()<id):# plus grand id garde son coup l'autre change
            #                 print("conflict")
            #                 self.forbidden_moves.append(next_move_other)
            #                 self.task_path=self.conflict_handling(self.task_path[-1],self.forbidden_moves)
            #                 self.MessagetoAll()
            
    
    def conflict_handling(self,task,forbidden_moves) :
        if(task==None):
            return []
        x_task, y_task = task
        x_current, y_current = self.posX, self.posY
        path = [] 

        # Possible directions (8 directions : N, S, E, W, and diagonals)
        directions = [
            (-1, 0), (1, 0),  # North, South
            (0, -1), (0, 1),  # West, East
            (-1, -1), (-1, 1),  # North-West, North-East
            (1, -1), (1, 1)    # South-West, South-East
        ]
        
        while (x_current, y_current) != (x_task, y_task):
            best_distance = math.inf
            best_move = None

            for dx, dy in directions:
                x_next, y_next = x_current + dx, y_current + dy
                if (x_next,y_next) not in forbidden_moves :
                    dist = self.distance(x_next, y_next, x_task, y_task)

                    if dist < best_distance:
                        best_distance = dist
                        best_move = (x_next, y_next)

            path.append(best_move)
            x_current, y_current = best_move
            print(f"best_move={best_move}")
            self.task_path = path

