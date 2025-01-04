from MyAgent import MyAgent
import math


#inherits MyAgent

class MyAgentStones(MyAgent):

    def __init__(self, id, initX, initY, env, capacity):
        MyAgent.__init__(self, id, initX, initY, env)
        self.stone = 0 # the quantity of stone collected and not unloaded yet
        self.backPack = capacity #capacity of the agent's back pack

        self.has_unloaded = False

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
    
    def next_move(self, path):
        """
        Handle the agent's movement along its path or perform the task at the target position.

        Args:
        - path (list): The list of coordinates representing the agent's current path.

        Returns:
        - None: Updates the agent's state and progresses along the path or completes a task.
        """
        if not path:
            if self.env.posUnload == self.getPos():  # Check if the agent is at the unload position
                self.unload()
                self.has_unloaded = True
            else:
                x, y = self.getPos()
                # Check if the agent is on a closed chest
                if (
                    self.env.grilleTres[x][y] is not None and
                    self.env.grilleTres[x][y].isOpen() and
                    self.env.grilleTres[x][y].getValue() != 0
                ):
                    self.load(self.env)  # Perform the load action
            self.task_in_progress = False
        else:  # Continue moving along the path
            next_x, next_y = path[0]  # Get the next position in the path
            current_x, current_y = self.getPos()
            next_move = self.move(self.posX, self.posY, next_x, next_y)  # Move to the next position
            if next_move == 1 or (current_x, current_y) == self.task_path[0]:  # If the move is successful
                path.pop(0)  # Remove the current step from the path


    def fill_tasks(self):
        """
        Update the agent's task list with coordinates of treasures
        that are valid, unassigned, open, and of type 1.
        """
        treasures = []

        # Iterate over the treasure grid
        for x in range(len(self.env.grilleTres)):
            for y in range(len(self.env.grilleTres[x])):
                treasure = self.env.grilleTres[x][y]

                # Check if the treasure meets all the conditions
                if (
                    treasure is not None and  
                    treasure.getValue() != 0 and
                    (x, y) not in self.other_agents_tasks and
                    treasure.isOpen() and treasure.getType() == 2
                ):
                    treasures.append((x, y))

        self.tasks = treasures

    def is_other_occuped(self):
        """
        Check if the other agent is currently occupied with a task.

        Returns:
        - bool: True if the other agent has a task with a non-empty treasure; False otherwise.
        """
        if self.other_agents_tasks:
            x, y = self.other_agents_tasks[-1]  # Get the last task assigned to the other agent
            treasure = self.env.grilleTres[x][y]
            # Check if the treasure exists and has a non-zero value (not unloaded yet)
            if treasure is not None and treasure.getValue() != 0:
                return True
        return False  # No tasks or all tasks are completed
    
    def do_policy(self):
        """
        Define and execute the agent's policy for the current step, including movement,
        task management, unloading, and parking.
        """
        self.forbidden_moves = []  # Reset forbidden moves for this step

        # Step 1: Unload if the agent's stone exceeds half its backpack capacity
        if not self.task_in_progress and self.backPack * 0.5 < self.stone:
            task = self.env.posUnload
            self.find_best_path(task)
            self.task_in_progress = True

        # Step 2: If unloading, find a new task or park if no tasks are available
        elif self.has_unloaded and not self.task_in_progress:
            self.has_unloaded = False
            self.fill_tasks()
            task = self.task_finding()

            if task is None:  # No tasks available, find a parking spot
                min_distance = math.inf
                best_parking_spot = None

                for x in range(self.env.tailleX):
                    for y in range(self.env.tailleY):
                        (x_depot, y_depot) = self.env.posUnload 
                        # Check if the cell is a valid parking spot
                        if (
                            self.env.grilleAgent[x][y] is None and  # Cell is free
                            self.env.grilleTres[x][y] is not None and self.env.grilleTres[x][y].getValue() == 0 and
                            (abs(x - x_depot) >= 3 and abs(y - y_depot) >= 3)  # At least 3 cells away from (5, 0)
                        ):
                            distance = self.distance(self.posX, self.posY, x, y)
                            if distance < min_distance:
                                min_distance = distance
                                best_parking_spot = (x, y)

                if best_parking_spot:
                    # Move to the best parking spot
                    self.find_best_path(best_parking_spot)
                    self.task_in_progress = True
                else:
                    # Default parking strategy: park based on agent ID
                    posY = int(self.getId()[-1]) % 4
                    self.find_best_path((11, posY))  # Park in predefined spots
                    self.task_in_progress = True

        # Step 3: Continue progressing on the current task
        if not self.has_unloaded and self.task_in_progress:
            self.next_move(self.task_path)  # Execute the next move along the path

        # Step 4: If no task is in progress, find a new task
        elif not self.task_in_progress:
            self.fill_tasks()
            self.has_unloaded = False
            task = self.task_finding()
            if task:
                # Set the new task and begin execution
                self.find_best_path(task)
                self.task_in_progress = True
                self.next_move(self.task_path)