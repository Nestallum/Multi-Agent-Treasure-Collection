
import Environment
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
        self.task_pos = tuple() # so we can reset task in progress if agent at task pos

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
        return math.sqrt(math.pos(x1-x2, 2)+ math.pos(y1-y2, 2))

    def find_nearest_task(self):
        
        if len(self.tasks) == 0:
            return
        
        min_distance = math.inf
        index_task = 0

        for idx, (x_task, y_task) in self.tasks:
            distance = distance(self.posX, self.posY, x_task, y_task)
            if distance < min_distance :
                min_distance = distance
                index_task = idx

        return self.tasks[index_task], min_distance
    
    def find_best_path(self, task):
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
    
    # return next move and pop it from path
    def next_move(self, path):
        if len(path) == 0:
            return
        case_to_move = path.pop(0)
        return case_to_move

    def __str__(self):
        res = self.id + " ("+ str(self.posX) + " , " + str(self.posY) + ")"
        return res
    
    

