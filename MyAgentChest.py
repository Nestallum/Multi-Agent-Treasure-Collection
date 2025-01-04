from MyAgent import MyAgent
import math

#inherits MyAgent

class MyAgentChest(MyAgent) :
    def __init__(self, id, initX, initY, env):
        MyAgent.__init__(self, id, initX, initY, env)

        self.has_opened = False # Check if the treasure has been opened
        

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
    
    def next_move(self, path):
        """
        Determine the next move for the agent based on its current state and path.

        Args:
        - path (list): A list of coordinates representing the agent's current path.

        Returns:
        - None: Updates the agent's position and task status.
        """
        # If the agent was previously marked as "opened", it means it completed its previous task.
        if self.has_opened and not self.task_in_progress:
            self.has_opened = False
            # Find the closest free cell to move on
            min_distance = math.inf
            closest_free_cell = None
            
            for x in range(self.env.tailleX):
                for y in range(self.env.tailleY):
                    # Check if the cell is valid and free
                    if (
                        0 <= x < self.env.tailleX and
                        0 <= y < self.env.tailleY and
                        self.env.grilleTres[x][y] is None and
                        self.env.grilleAgent[x][y] is None and
                        (x, y) != self.env.posUnload and
                        (x, y) not in self.forbidden_moves
                    ):
                        distance = self.distance(self.posX, self.posY, x, y)
                        if distance < min_distance:
                            min_distance = distance
                            closest_free_cell = (x, y)

            if closest_free_cell:
                # Move to the closest free cell
                current_x, current_y = self.getPos()
                task = closest_free_cell
                self.find_best_path(task)  # Find a path to the target
                self.task_in_progress = True
                path = self.task_path
            else:
                # If no free cell is available, find the closest opened chest
                min_distance = math.inf
                closest_opened_chest = None
                for x in range(self.env.tailleX):
                    for y in range(self.env.tailleY):
                        # Check if the cell has an opened chest
                        if (
                            0 <= x < self.env.tailleX and
                            0 <= y < self.env.tailleY and
                            self.env.grilleTres[x][y] is not None and
                            self.env.grilleTres[x][y].getValue() == 0 and
                            self.env.grilleAgent[x][y] is None and
                            (x, y) != self.env.posUnload and
                            (x, y) not in self.forbidden_moves
                        ):
                            distance = self.distance(self.posX, self.posY, x, y)
                            if distance < min_distance:  # Find the closest opened chest
                                min_distance = distance
                                closest_opened_chest = (x, y)
                if closest_opened_chest:
                    # Move to the closest opened chest
                    current_x, current_y = self.getPos()
                    task = closest_opened_chest
                    self.find_best_path(task)  # Find a path to the target
                    self.task_in_progress = True
                    path = self.task_path

        if self.task_in_progress:
            if not path:  # Arrived at the task position
                (x, y) = self.getPos()
                if self.env.grilleTres[x][y] is not None and not self.env.grilleTres[x][y].isOpen():
                    self.open()
                    self.score += 1
                    self.has_opened = True
                self.task_in_progress = False
            else:  # Continue along the path
                next_x, next_y = path[0]
                current_x, current_y = self.getPos()
                next_move = self.move(self.posX, self.posY, next_x, next_y)
                if next_move == 1 or (current_x, current_y) == self.task_path[0]:  # Move successful
                    path.pop(0)  # Remove the current step from the path

    def fill_tasks(self):
        """
        Populate the agent's task list (`self.tasks`) with coordinates of unopened treasures
        that are not yet assigned to other agents.
        """
        self.tasks = [
            (x, y)
            for x in range(len(self.env.grilleTres))
            for y in range(len(self.env.grilleTres[x]))
            if (
                (treasure := self.env.grilleTres[x][y]) is not None and
                treasure.getValue() != 0 and
                not treasure.isOpen() and
                (x, y) not in self.other_agents_tasks
            )
        ]

    def is_other_occuped(self):
        """
        Check if the other agent is currently occupied with an unopened treasure.

        Returns:
        - bool: True if the other agent has a task and the treasure is not opened yet; False otherwise.
        """
        if self.other_agents_tasks:  # Verify if the other agent has assigned tasks
            x, y = self.other_agents_tasks[-1]  # Get the last task assigned
            if not self.env.grilleTres[x][y].isOpen():  # Check if the treasure is still unopened
                return True
        return False  # No tasks or all tasks completed

    def do_policy(self):
        """
        Execute the agent's policy for the current step: 
        progress on a task, find a new task, or adjust its position.
        """
        if self.task_in_progress:  # Agent is currently working on a task
            self.next_move(self.task_path)  # Continue to the next step in the path
        else:  # Agent is free and needs a new task
            self.fill_tasks()  # Populate the task list
            task = self.task_finding()  # Find the next task
            if task is None:
                # No task found: move to avoid blocking or stay in place
                self.next_move(self.task_path)
            else:
                # A task is found: calculate the best path and start the task
                self.find_best_path(task)
                self.task_in_progress = True
                self.next_move(self.task_path)

        # Clear forbidden moves for the next step
        self.forbidden_moves = []

                 
                     