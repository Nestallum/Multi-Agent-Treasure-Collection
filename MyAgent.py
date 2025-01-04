import Environment
import ast
import math
import random
from itertools import combinations

class MyAgent:

    def __init__(self, id, initX, initY, env:Environment):
        self.id = id
        self.posX = initX
        self.posY = initY
        self.env = env
        self.mailBox = []

        self.tasks = []                 # Tasks waiting to be executed
        self.task_in_progress = False   # Indicates if a task is currently being executed
        self.task_path = []             # Path for the current task
        self.other_agents_tasks = []    # Tasks taken by other agents of the same type
        self.forbidden_moves = []       # Moves that are not allowed
        self.score = 0                  # Total score of the agent


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.getId() == self.getId()
        return False

    #make the agent moves from (x1,y1) to (x2,y2)
    def move(self, x1, y1, x2, y2) :
        if x1 == self.posX and y1 == self.posY :
            print("departure position OK")
            if self.env.move(self, x1, y1, x2, y2) :
                self.posX = x2
                self.posY = y2
                print("deplacement OK")
                return 1
            
        return -1

    #return the id of the agent
    def getId(self):
        return self.id

    #return the position of the agent
    def getPos(self):
        return (self.posX, self.posY)

    # return the score of the agent
    def getScore(self) :
        return self.score
    
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

    def __str__(self):
        res = self.id + " ("+ str(self.posX) + " , " + str(self.posY) + ")"
        return res
    
    def distance(self, x1, y1, x2, y2):
        """
        Calculate the Euclidean distance between two grid cells (x1, y1) and (x2, y2).
        """
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def find_nearest_task(self):
        """
        Find the nearest task to the agent based on its current position.

        Returns:
        tuple: The coordinates of the closest task.
        """
        if not self.tasks:
            return  # Exit if no tasks are available

        # Find the closest task based on the distance
        return min(self.tasks, key=lambda task: self.distance(self.posX, self.posY, *task))

    def find_best_path(self, task):
        """
        Calculate the best path from the agent's current position to the given task 
        using a greedy approach (choosing the move that minimizes distance at each step).

        Parameters:
        task (tuple): Coordinates of the target task (x, y).

        Returns:
        list: A list of coordinates representing the path to the task.
        """
        if task is None:
            return []  # Return an empty path if no task is provided

        x_task, y_task = task
        x_current, y_current = self.posX, self.posY
        path = []

        # Define possible moves: cardinal directions and diagonals
        directions = [
            (-1, 0), (1, 0),    # North, South
            (0, -1), (0, 1),    # West, East
            (-1, -1), (-1, 1),  # North-West, North-East
            (1, -1), (1, 1)     # South-West, South-East
        ]

        # Continue moving until the agent reaches the task's position
        while (x_current, y_current) != (x_task, y_task):
            best_distance = math.inf
            best_move = None 

            # Evaluate all possible moves
            for dx, dy in directions:
                x_next, y_next = x_current + dx, y_current + dy

                if 0 <= x_next < self.env.tailleX and 0 <= y_next < self.env.tailleY:
                    dist = self.distance(x_next, y_next, x_task, y_task)

                    if dist < best_distance:
                        best_distance = dist
                        best_move = (x_next, y_next) # Update if this move is closer to the target

            path.append(best_move)
            x_current, y_current = best_move

        self.task_path = path  # Store the computed path

    def task_finding(self):
        """
        Determine the best task for the agent to perform based on availability and proximity.

        Returns:
        tuple or None: Coordinates of the selected task or None if no task is assigned.
        """
        env = self.env
        other = None

        # No tasks available
        if len(self.tasks) == 0:
            return None

        # Find another agent of the same type
        for a in env.agentSet.values():
            if a.getType() == self.getType() and not self.__eq__(a):
                other = a
                break

        # Coordinates of the other agent
        other_posX, other_posY = other.getPos()

        # Case 1: The other agent is occupied
        if self.is_other_occuped():
            # Select the nearest task for the agent and notify the other agent to avoid duplication
            self.send(other.getId(), f"Task_{self.find_nearest_task()}") 
            return self.find_nearest_task()

        # Case 2: Only one task is available
        if len(self.tasks) == 1:
            task_X, task_Y = self.tasks[0]
            self_distance = self.distance(self.posX, self.posY, task_X, task_Y)
            other_distance = self.distance(other_posX, other_posY, task_X, task_Y)

            # Self is closer to the task
            if self_distance < other_distance:
                self.send(other.getId(), f"Task_{self.tasks[0]}")
                return self.tasks[0]

            # Both agents are at the same distance, resolve by agent ID
            if self_distance == other_distance:
                if int(self.id[-1]) > int(other.getId()[-1]):
                    self.send(other.getId(), f"Task_{self.tasks[0]}")
                    return self.tasks[0]

            # The other agent is closer or has a higher ID
            return None

        # Case 3: More than one task is available
        min_distance = float('inf')
        best_task_for_self = None

        # Evaluate all combinations of two tasks
        for task1, task2 in combinations(self.tasks, 2):
            # Distance from self to task1 and other to task2
            distance_self_to_task1 = self.distance(self.posX, self.posY, task1[0], task1[1])
            distance_other_to_task2 = self.distance(other_posX, other_posY, task2[0], task2[1])
            total_distance = distance_self_to_task1 + distance_other_to_task2

            # Distance from self to task2 and other to task1
            distance_self_to_task2 = self.distance(self.posX, self.posY, task2[0], task2[1])
            distance_other_to_task1 = self.distance(other_posX, other_posY, task1[0], task1[1])
            swapped_total_distance = distance_self_to_task2 + distance_other_to_task1

            # Check if this combination is better
            if total_distance < min_distance:
                min_distance = total_distance
                best_task_for_self = task1

            if swapped_total_distance < min_distance:
                min_distance = swapped_total_distance
                best_task_for_self = task2

        # Assign the best task to self and notify the other agent
        self.send(other.getId(), f"Task_{best_task_for_self}")
        return best_task_for_self

    def find_nearby_agents(self):
        """
        Find the IDs of agents within a distance of "max_range" units from the current agent.

        Returns:
        list: A list of IDs of nearby agents.
        """
        nearby_ids = []
        max_range = 3

        for agent in self.env.agentSet.values():
            if self.getId() != agent.getId():  # Exclude the current agent
                dist = self.distance(self.posX, self.posY, agent.posX, agent.posY)
                if dist <= max_range:  # Check if the agent is within the specified range
                    nearby_ids.append(agent.getId()) 

        return nearby_ids

    def broadcast_intention(self):
        """
        Broadcast the agent's intention (current, next, and final positions) to nearby agents.

        - If the agent is stationary (no path), it sends a "HoldPosition" message with its current position.
        - Otherwise, it sends a "MoveTo" message including the current position, the next move, 
        and the final destination (last move in the path).

        Returns:
        None
        """
        current_pos = self.getPos()
        next_move = self.task_path[0] if self.task_path else current_pos  # Determine the next move or stay in place

        # Notify nearby agents about the agent's intention
        for id in self.find_nearby_agents():
            if next_move == current_pos:
                # Agent remains stationary, notify others with "HoldPosition"
                self.send(id, f"HoldPosition_{current_pos}")
            else:
                # Agent is moving, include the final destination (last_move)
                last_move = self.task_path[-1]  # Get the final destination in the task path
                self.send(id, f"MoveTo_{current_pos}_{next_move}_{last_move}")

    def resolve_conflicts(self):
        """
        Resolve conflicts between agents based on their intentions (current, next, and final positions).
        
        Reads messages from the agent's mailbox and determines how to handle conflicts when multiple agents
        are moving to the same position or interfering with each other's paths.
        
        Returns:
        None
        """
        conflict = False  # Flag to indicate if a conflict was detected

        # Process all messages in the mailbox
        while len(self.mailBox) != 0:
            id, content = self.readMail()

            # Handle "Task" messages: Add other agents' tasks to the list
            if content.split("_")[0] == "Task":
                msg = ast.literal_eval(content.split("_")[1].strip())
                self.other_agents_tasks.append(msg)

            # Handle "Move" messages: Resolve conflicts related to movement
            if content.startswith("MoveTo_"):
                parts = content.split("_")
                if len(parts) == 4:  # Ensure the message is well-formed
                    current_pos_other = ast.literal_eval(parts[1])  # Current position of the other agent
                    next_move_other = ast.literal_eval(parts[2])    # Next move of the other agent
                    final_move_other = ast.literal_eval(parts[3])   # Final destination of the other agent

                # Case 1: Both agents want to move to the same position
                if self.task_path and self.task_path[0] == next_move_other:
                    wanted_case = self.task_path[0]  # The contested position
                    final_move_self = self.task_path[-1]  # The final position of the current agent

                    # Sub-case 1: The contested position is the final destination of the current agent
                    if wanted_case == final_move_self and not wanted_case == final_move_other:
                        None  # No action needed

                    # Sub-case 2: The contested position is the final destination of the other agent
                    elif not wanted_case == final_move_self and wanted_case == final_move_other:
                        conflict = True
                        self.forbidden_moves.append(next_move_other)
                        self.find_alternative_path(self.task_path[-1], self.forbidden_moves)

                    # Sub-case 3: The contested position is the final destination of both agents
                    elif wanted_case == final_move_self and wanted_case == final_move_other:
                        if self.getId() < id:  # The agent with the smaller ID waits
                            self.find_alternative_path(self.task_path[-1], self.forbidden_moves, fixed=True) # Stop temporarily

                    # Sub-case 4: The contested position is an intermediate position for both agents
                    elif not wanted_case == final_move_self and not wanted_case == final_move_other:
                        if self.getId() < id:  # The agent with the smaller ID finds an alternative path
                            conflict = True
                            self.forbidden_moves.append(next_move_other)
                            self.find_alternative_path(self.task_path[-1], self.forbidden_moves)

                # Case 2: The current agent wants to move to a position occupied by another agent
                elif self.task_path and self.task_path[0] == current_pos_other:
                    if self.getPos() == next_move_other:  # Collision: Both agents will occupy the same position
                        conflict = True
                        self.forbidden_moves.append(next_move_other)
                        self.find_alternative_path(self.task_path[-1], self.forbidden_moves)
                    else:
                        # Avoid moving to the position
                        self.find_alternative_path(self.task_path[-1], self.forbidden_moves, fixed=True) # Stop temporarily

            # Handle "Fixe" messages: Resolve conflicts with stationary agents
            elif content.startswith("HoldPosition_"):
                parts = content.split("_")
                if len(parts) == 2:  # Ensure the message is well-formed
                    fixed_position = ast.literal_eval(parts[1])  # Position of the stationary agent

                    # Case: A stationary agent blocks the path
                    if self.task_path and self.task_path[0] == fixed_position:
                        # Sub-case: The stationary agent blocks the final destination
                        if fixed_position == self.task_path[-1]:
                            self.find_alternative_path(self.task_path[-1], self.forbidden_moves, fixed=True)  # Stop temporarily
                        else:
                            # Sub-case: The stationary agent blocks an intermediate position
                            conflict = True
                            self.forbidden_moves.append(fixed_position)
                            self.find_alternative_path(self.task_path[-1], self.forbidden_moves)

            # If a conflict was resolved, broadcast the updated intention
            if conflict:
                self.broadcast_intention()


    def find_alternative_path(self, task, forbidden_moves, fixed=False):
        """
        Find an alternative path to the target position if the next move is blocked.

        If `fixed=True`, the agent stays in its current position for the first move.
        
        Args:
            task (tuple): The target position (x, y).
            forbidden_moves (list): List of forbidden positions the agent should avoid.
            fixed (bool): If True, the agent remains stationary for the first move.

        Returns:
            None: Updates the `self.task_path` attribute with the new path.
        """
        if task is None:
            return []  # No path if the task is None

        x_task, y_task = task
        x_current, y_current = self.posX, self.posY
        path = []
        first_move = True  # Track if it's the first move

        # If fixed=True, the agent stays in place for the first move
        if fixed:
            path.append(self.getPos())  # Add the current position to the path
            first_move = False

        # Possible movement directions: cardinal and diagonal
        directions = [
            (-1, 0), (1, 0),    # North, South
            (0, -1), (0, 1),    # West, East
            (-1, -1), (-1, 1),  # North-West, North-East
            (1, -1), (1, 1)     # South-West, South-East
        ]

        # While the agent hasn't reached the target
        while (x_current, y_current) != (x_task, y_task):
            valid_moves = []  # List of valid moves for the first step
            move_distances = []  # Distances corresponding to valid moves
            best_distance = math.inf
            best_move = None  # Best move to make

            # Evaluate all possible moves
            for dx, dy in directions:
                x_next, y_next = x_current + dx, y_current + dy

                if 0 <= x_next < self.env.tailleX and 0 <= y_next < self.env.tailleY:
                    if first_move and (x_next, y_next) not in forbidden_moves:
                        # Add valid first moves that are not forbidden
                        valid_moves.append((x_next, y_next))
                        move_distances.append(self.distance(x_next, y_next, x_task, y_task))
                    else:
                        # For subsequent moves, minimize the distance to the target
                        dist = self.distance(x_next, y_next, x_task, y_task)
                        if dist < best_distance:
                            best_distance = dist
                            best_move = (x_next, y_next)

            # Handle the first move logic
            if first_move:
                if valid_moves:
                    # Sort valid moves by distance to the task
                    sorted_moves = sorted(zip(valid_moves, move_distances), key=lambda x: x[1])

                    # Exclude the 3 furthest moves to discourage unnecessary backtracking (simple heuristic)
                    possible_moves = [move for move, _ in sorted_moves[:-3]] if len(sorted_moves) > 3 else valid_moves

                    # Choose a random move among the remaining valid moves
                    best_move = random.choice(possible_moves)
                else:
                    # No valid moves at all, stay in place
                    print(f"No valid move found. Agent {self.getId()} stays at {self.getPos()}.")
                    best_move = self.getPos()

                first_move = False

            else:  # Logic for subsequent moves
                if best_move is None:  # If no valid move, stay in place
                    best_move = self.getPos()

            # Update path and current position
            path.append(best_move)
            x_current, y_current = best_move

        # Update the agent's task path with the new path
        self.task_path = path
