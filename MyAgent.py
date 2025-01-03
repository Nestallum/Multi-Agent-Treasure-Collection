import ast
import Environment
import math
from itertools import combinations
import math
import random
import numpy as np

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
        self.score = 0

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

    def getScore(self) :
        return self.score
    # add a message to the agent's mailbox
    def receive(self, idReceiver, textContent):
        self.mailBox.append((idReceiver, textContent))

    #the agent reads a message in her mailbox (FIFO mailbox)
    #return a tuple (id of the sender, message  text content)
    def readMail (self):
        idSender, textContent = self.mailBox.pop(0)
        # print("mail received from {} with content {}".format(idSender, textContent))
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

        if(task == None):
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
                # Vérifie si la position est valide et libre
                if 0 <= x_next < self.env.tailleX and 0 <= y_next < self.env.tailleY:
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
            self.send(other.getId(),f"Task_{self.find_nearest_task()[0]}")
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
                self.send(other.getId(),f"Task_{self.tasks[0]}")
                return self.tasks[0]

            # Cas 2 : Les deux agents sont à la même distance
            if self_distance == other_distance:
                # Le plus grand ID récupère la tâche
                if int(self.id[-1]) > int(other.getId()[-1]):
                    self.send(other.getId(),f"Task_{self.tasks[0]}")
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
        
        self.send(other.getId(),f"Task_{best_task_for_self}")
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

    
    def declare_intention(self):
        """
        Déclare l'intention de l'agent (position actuelle, prochaine position, position finale) à tous les agents proches.
        Si l'agent n'a pas de chemin (reste sur place), envoie un message "Fixe".
        """
        current_pos = self.getPos()
        next_move = self.task_path[0] if self.task_path else current_pos
    
        for id in self.CloseAgent():
            if next_move == current_pos:
                # Si l'agent reste sur place
                self.send(id, f"Fixe_{current_pos}")
            else:
                last_move = self.task_path[-1]
                # Sinon, envoie le prochain mouvement et le mouvement final
                self.send(id, f"Move_{current_pos}_{next_move}_{last_move}")


    def resolve_conflicts(self):
        conflict = False

        while len(self.mailBox) != 0:
            id, content = self.readMail()

            if(content.split("_")[0]=="Task"): # Lis les mails task des autres agents et les ajoute à sa liste other agent task
                msg = ast.literal_eval(content.split("_")[1].strip())
                self.other_agents_tasks.append(msg)

            # Vérifie le format du message
            if content.startswith("Move_"):
                parts = content.split("_")
                if len(parts) == 4:  # Vérifie que le message est bien formé
                    current_pos_other = ast.literal_eval(parts[1])  # Position actuelle de l'autre agent
                    next_move_other = ast.literal_eval(parts[2])    # Prochain mouvement de l'autre agent
                    final_move_other = ast.literal_eval(parts[3])   # Dernier mouvement de l'autre agent

                if self.task_path and self.task_path[0] == next_move_other: # Cas 1 : les deux veulent aller au même endroit
                    wanted_case = self.task_path[0]
                    final_move_self = self.task_path[-1]
                    # Cas 1 : La case convoitée est la case finale de l'agent courant
                    if wanted_case == final_move_self and not wanted_case == final_move_other:
                        None
                    # Cas 2 : La case convoitée est la case finale de l'autre agent
                    elif not wanted_case == final_move_self and wanted_case == final_move_other:
                        conflict = True
                        self.forbidden_moves.append(next_move_other)
                        self.find_alternative_path(self.task_path[-1], self.forbidden_moves) # On le contourne
                    # Cas 3 : La case convoitée est la case finale des deux agents
                    elif wanted_case == final_move_self and wanted_case == final_move_other:
                        if self.getId() < id: # Le plus petit id attend, l'autre va à sa case finale
                            self.find_alternative_path(self.task_path[-1], self.forbidden_moves, fixed=True)
                    # Cas 4 : La case convoitée est une case intermédiaire de leur chemin
                    elif not wanted_case == final_move_self and not wanted_case == final_move_other:
                        if self.getId() < id: # Le plus petit id contourne, l'autre continue sa route
                            conflict = True
                            self.forbidden_moves.append(next_move_other)
                            self.find_alternative_path(self.task_path[-1], self.forbidden_moves)


                elif self.task_path and self.task_path[0] == current_pos_other: # Cas 2 : L'agent courant veut aller sur une case occupée d'un agent non fixe
                    if self.getPos() == next_move_other: # Ils vont se rentrer dedans
                        conflict = True
                        self.forbidden_moves.append(next_move_other)
                        self.find_alternative_path(self.task_path[-1], self.forbidden_moves)
                    else:
                        self.find_alternative_path(self.task_path[-1], self.forbidden_moves, fixed=True) 

            elif content.startswith("Fixe_"):
                parts = content.split("_")
                if len(parts) == 2:  # Vérifie que le message est bien formé
                    fixed_position = ast.literal_eval(parts[1])

                    if self.task_path and self.task_path[0] == fixed_position: # Cas : Un agent fixe bloque notre chemin
                            if fixed_position == self.task_path[-1]: # L'agent fixe bloque notre destination finale
                                print("DANS LE CAS---------------------------------------------------------------------------------")
                                self.find_alternative_path(self.task_path[-1], self.forbidden_moves, fixed=True) # On s'arrête pour le prochain coup
                            else : # L'agent bloque une case intermédiaire du chemin, on contourne
                                conflict = True
                                self.forbidden_moves.append(fixed_position)
                                self.find_alternative_path(self.task_path[-1], self.forbidden_moves)

            if conflict:
                self.declare_intention()

    # def find_alternative_path(self, task, forbidden_moves, fixed=False):
    #     """
    #     Trouve un chemin alternatif si le prochain mouvement est bloqué.
    #     Si `fixed=True`, l'agent reste sur place pour le premier mouvement.
    #     Args:
    #         task (tuple): La position cible.
    #         forbidden_moves (list): Les mouvements interdits.
    #         fixed (bool): Si True, le premier mouvement est fixé à la position actuelle de l'agent.
    #     """

    #     if task is None:
    #         return []

    #     x_task, y_task = task
    #     x_current, y_current = self.posX, self.posY
    #     path = []   
    #     first_move = True  # Flag to track if it's the first move

    #     if fixed:
    #         path.append(self.getPos())
    #         first_move = False  # On ne change pas le first move car on restera sur place

    #     # Possible directions (8 directions: N, S, E, W, and diagonals)
    #     directions = [
    #         (-1, 0), (1, 0),  # North, South
    #         (0, -1), (0, 1),  # West, East
    #         (-1, -1), (-1, 1),  # North-West, North-East
    #         (1, -1), (1, 1)    # South-West, South-East
    #     ]

    #     while (x_current, y_current) != (x_task, y_task):
    #         valid_moves = []
    #         best_distance = math.inf
    #         best_move = None

    #         for dx, dy in directions:
    #             x_next, y_next = x_current + dx, y_current + dy
    #             if 0 <= x_next < self.env.tailleX and 0 <= y_next < self.env.tailleY:
    #                 if first_move:
    #                     # Ajoute uniquement les cases valides qui ne sont pas interdites
    #                     if (x_next, y_next) not in forbidden_moves:
    #                         valid_moves.append((x_next, y_next))
    #                 else:
    #                     # Minimise la distance pour les mouvements suivants
    #                     dist = self.distance(x_next, y_next, x_task, y_task)
    #                     if dist < best_distance:
    #                         best_distance = dist
    #                         best_move = (x_next, y_next)

    #         if first_move:
    #             if valid_moves:
    #                 # Choisit un mouvement aléatoire parmi les cases valides
    #                 best_move = random.choice(valid_moves)
    #             else:
    #                 # Si aucune case valide n'est trouvée, reste sur place
    #                 print(f"Aucun mouvement valide trouvé. L'agent {self.getId()} reste sur place à {self.getPos()}.")
    #                 best_move = self.getPos()

    #             first_move = False

    #         if best_move is None:
    #             raise ValueError("No valid moves available to reach the task.")

    #         path.append(best_move)
    #         x_current, y_current = best_move
            
    #     self.task_path = path


    def find_alternative_path(self, task, forbidden_moves, fixed=False):
        """
        Trouve un chemin alternatif si le prochain mouvement est bloqué.
        Si `fixed=True`, l'agent reste sur place pour le premier mouvement.
        Args:
            task (tuple): La position cible.
            forbidden_moves (list): Les mouvements interdits.
            fixed (bool): Si True, le premier mouvement est fixé à la position actuelle de l'agent.
        """
        if task is None:
            return []

        x_task, y_task = task
        x_current, y_current = self.posX, self.posY
        path = []
        first_move = True  # Flag to track if it's the first move

        if fixed:
            path.append(self.getPos())
            first_move = False  # On ne change pas le first move car on restera sur place

        # Possible directions (8 directions: N, S, E, W, and diagonals)
        directions = [
            (-1, 0), (1, 0),  # North, South
            (0, -1), (0, 1),  # West, East
            (-1, -1), (-1, 1),  # North-West, North-East
            (1, -1), (1, 1)    # South-West, South-East
        ]

        while (x_current, y_current) != (x_task, y_task):
            valid_moves = []
            move_distances = []
            best_distance = math.inf

            for dx, dy in directions:
                x_next, y_next = x_current + dx, y_current + dy
                if 0 <= x_next < self.env.tailleX and 0 <= y_next < self.env.tailleY:
                    if  first_move and (x_next, y_next) not in forbidden_moves:
                        # Ajouter à la liste des mouvements valides
                        valid_moves.append((x_next, y_next))
                        move_distances.append(self.distance(x_next, y_next, x_task, y_task))
                    else:
                        # Minimise la distance pour les mouvements suivants
                        dist = self.distance(x_next, y_next, x_task, y_task)
                        if dist < best_distance:
                            best_distance = dist
                            best_move= (x_next, y_next)

            if first_move:
                if valid_moves:
                    # Trier les mouvements par distance à la tâche (du plus proche au plus éloigné)
                    sorted_moves = sorted(zip(valid_moves, move_distances), key=lambda x: x[1])

                    # Exclure les 3 mouvements qui éloignent le plus de la tâche
                    possible_moves = [move for move, _ in sorted_moves[:-3]] if len(sorted_moves) > 3 else valid_moves

                    if possible_moves:
                        # Choisit un mouvement aléatoire parmi les mouvements restants
                        best_move = random.choice(possible_moves)
                    else:
                        # Si aucun mouvement valide n'est trouvé, reste sur place
                        print(f"Aucun mouvement valide trouvé. L'agent {self.getId()} reste sur place à {self.getPos()}.")
                        best_move = self.getPos()
                else:
                    # Si aucune case valide n'est trouvée, reste sur place
                    print(f"Aucun mouvement valide trouvé. L'agent {self.getId()} reste sur place à {self.getPos()}.")
                    best_move = self.getPos()

                first_move = False

            else: # Autre move que first move
                if best_move is None:
                    best_move = self.getPos()

            path.append(best_move)
            x_current, y_current = best_move

        self.task_path = path


    # def find_alternative_path(self, task, forbidden_moves, fixed=False):
    #     """
    #     Trouve un chemin alternatif si le prochain mouvement est bloqué.
    #     Si `fixed=True`, l'agent reste sur place pour le premier mouvement.
    #     Args:
    #         task (tuple): La position cible.
    #         forbidden_moves (list): Les mouvements interdits.
    #         fixed (bool): Si True, le premier mouvement est fixé à la position actuelle de l'agent.
    #     """
    #     if task is None:
    #         return []

    #     x_task, y_task = task
    #     x_current, y_current = self.posX, self.posY
    #     path = []

    #     # Ajoute la position actuelle si `fixed` est activé
    #     if fixed:
    #         path.append(self.getPos())

    #     # Directions possibles
    #     directions = [
    #         (-1, 0), (1, 0),  # North, South
    #         (0, -1), (0, 1),  # West, East
    #         (-1, -1), (-1, 1),  # North-West, North-East
    #         (1, -1), (1, 1)    # South-West, South-East
    #     ]

    #     first_move = True

    #     while (x_current, y_current) != (x_task, y_task):
    #         valid_moves = []
    #         for dx, dy in directions:
    #             x_next, y_next = x_current + dx, y_current + dy
    #             if (
    #                 0 <= x_next < self.env.tailleX
    #                 and 0 <= y_next < self.env.tailleY
    #                 and (first_move and (x_next, y_next) not in forbidden_moves)
    #             ):
    #                 valid_moves.append((x_next, y_next))

    #         if first_move:
    #             # Trier et exclure les mouvements éloignés
    #             if valid_moves:
    #                 sorted_moves = sorted(valid_moves, key=lambda move: self.distance(move[0], move[1], x_task, y_task))
    #                 valid_moves = sorted_moves[:-3] if len(sorted_moves) > 3 else sorted_moves
    #                 best_move = random.choice(valid_moves) if valid_moves else self.getPos()
    #             else:
    #                 best_move = self.getPos()
    #             first_move = False
    #         else:
    #             # Minimise la distance pour les mouvements suivants
    #             best_move = min(
    #                 valid_moves,
    #                 key=lambda move: self.distance(move[0], move[1], x_task, y_task),
    #                 default=self.getPos()
    #             )

    #         if best_move == self.getPos():
    #             break  # Si on reste sur place, on arrête la boucle

    #         path.append(best_move)
    #         x_current, y_current = best_move

    #     self.task_path = path
