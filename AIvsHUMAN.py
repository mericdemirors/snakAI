import random
import copy
import keyboard
from time import sleep
import time

TABLE_ROW,TABLE_COLUMN = 11,13
TABLE = [[0 for _ in range(TABLE_COLUMN)] for _ in range(TABLE_ROW)]

APPLE_ROW, APPLE_COLUMN = -1, -1
MOVE_TIME = 0.5

def put_apple():
    """puts apple randomly in a empyt place
    """
    global APPLE_ROW, APPLE_COLUMN
    while True:
        APPLE_ROW, APPLE_COLUMN = random.randint(0, TABLE_ROW-1), random.randint(0, TABLE_COLUMN-1)
        if TABLE[APPLE_ROW][APPLE_COLUMN] == 0:
            TABLE[APPLE_ROW][APPLE_COLUMN] = -1
            return

def render_table(snakes, snake_render_dict):
    """renders table
        '_' : empty place = 0
        'ǒ' : apple = -1
    Args:
        snakes (list): list of Snakes on the table
        snake_render_dict (dictionary): dictionary to hold snake representation characters
    """
    print()
    for r in range(TABLE_ROW):
        for c in range(TABLE_COLUMN):
            print(".",end="")
            rc_not_in_snake_body_flag = True
            for snake in snakes:
                if [r,c] in snake.body:
                    if [r,c] == snake.body[0]:
                        print(snake_render_dict[snake.name]["head"], end="")
                        rc_not_in_snake_body_flag = False
                    else:
                        print(snake_render_dict[snake.name]["tail"], end="")
                        rc_not_in_snake_body_flag = False
            if rc_not_in_snake_body_flag:
                print({0:'_', -1:'ǒ'}[TABLE[r][c]], end="")
        print()

def render_cost_table(cost_table):
    """renders cost table

    Args:
        cost_table (numpy.ndarray): cost table to render
    """
    for r in cost_table:
        for c in r:
            print(str(c)[0:-2], end=" ")
        print()

def calculate_cost_table(goal_row, goal_column, snake):
    """calculates cost values to reach goal

    Args:
        goal_row (int): row index of goal coordinates
        goal_column (int): column index of goal coordinates
        snake (Snake, optional): snake to calculate cost for

    Returns:
        list: cost table
    """
    def calculate_cost_table_recursive(cost_table, row, column, snake):
        """recursive function to calculate cost table

        Args:
            cost_table (list): table to calculate cost on
            row (int): row index of current place
            column (int): column index of current place
            snake (Snake): snake to calculate cost for
        """
        # go to possible and can be shortened node(nonlooked nodes g cost is infinite so they all are a 'can be shortened node')
        flags = [False, False, False, False]

        # find boxes which is "in TABLE AND nonlooked or non-optimal AND (empty OR can_pass)"
        if row>0 and cost_table[row-1][column]>cost_table[row][column]+1 and is_reachable(snake, row-1, column): #north
                cost_table[row-1][column] = min_surrounding_node(cost_table, row-1, column) + 1
                flags[0] = True
        if row<TABLE_ROW-1 and cost_table[row+1][column]>cost_table[row][column]+1 and is_reachable(snake, row+1, column): #south
                cost_table[row+1][column] = min_surrounding_node(cost_table, row+1, column) + 1
                flags[1] = True
        if column<TABLE_COLUMN-1 and cost_table[row][column+1]>cost_table[row][column]+1 and is_reachable(snake, row, column+1): #east
                cost_table[row][column+1] = min_surrounding_node(cost_table, row, column+1) + 1
                flags[2] = True
        if column>0 and cost_table[row][column-1]>cost_table[row][column]+1 and is_reachable(snake, row, column-1): #west
                cost_table[row][column-1] = min_surrounding_node(cost_table, row, column-1) + 1
                flags[3] = True

        # call recursive on the boxes you just flagged(flagging means that we can continue from this box)
        if flags[0]:
            calculate_cost_table_recursive(cost_table, row-1, column, snake)
        if flags[1]:
            calculate_cost_table_recursive(cost_table, row+1, column, snake)
        if flags[2]:
            calculate_cost_table_recursive(cost_table, row, column+1, snake)
        if flags[3]:
            calculate_cost_table_recursive(cost_table, row, column-1, snake)  
    
    cost_table = [[float("inf") for _ in range(TABLE_COLUMN)] for _ in range(TABLE_ROW)]
    cost_table[goal_row][goal_column] = 0 
    calculate_cost_table_recursive(cost_table, goal_row, goal_column, snake)
    return cost_table    

def min_surrounding_node(cost_table, row, column):
    """returns the min value among surroindings

    Args:
        cost_table (list): table of costs
        row (int): row index to calculate surroinding costs
        column (int): int index to calculate surroinding costs

    Returns:
        int: min value among surroindings
    """
    n, s, e, w = float("inf"), float("inf"), float("inf"), float("inf") 
    if row>0: 
        n = cost_table[row-1][column]
    if row<TABLE_ROW-1:
        s = cost_table[row+1][column]
    if column<TABLE_COLUMN-1:
        e = cost_table[row][column+1]
    if column>0:
        w = cost_table[row][column-1]
    return min([n,s,e,w])

def is_reachable(snake, row, column):
    """returns if an index is reachable to snake or not

    Args:
        snake (Snake): snake to calculate reachability for
        row (int): row index of place
        column (int): column index of place

    Returns:
        bool: whether the snake can reach or not
    """
    if TABLE[row][column] == 0: # is place empty
        return True
    if (row, column) == (APPLE_ROW, APPLE_COLUMN): # is it apple
        return True    
    if [row, column] in snake.body: # is it so far that is definitely disappears till snakes head reaches that place(shortest paths length is longer than body parts length to end of tail)
        if (abs(snake.body[0][0]-row) + abs(snake.body[0][1]-column)) > len(snake.body) - snake.body.index([row,column]):
            return True

def wall_heuristic(snake, direction):
    """calculates a value called 'wall_heuristic' that indicates how surrounded is a place
    more surroinding means 

    Args:
        snake (Snake): snake to compute heuristic values for
        direction (string): direction

    Returns:
        int: number of walls(nonmovable places) around
    """
    head_row = snake.body[0][0]
    head_column = snake.body[0][1]

    if direction == 'n' and head_row > 0:
        return walls_around(head_row-1, head_column)
    if direction == 's' and head_row < TABLE_ROW-1:
        return walls_around(head_row+1, head_column)
    if direction == 'w' and head_column > 0:
        return walls_around(head_row, head_column-1)
    if direction == 'e' and head_column < TABLE_COLUMN-1:
        return walls_around(head_row, head_column+1)

def walls_around(row, column):
    """calculates how many walls(nonmovable places) are around in 3x3 area

    Args:
        row (int): current places row index
        column (int): current places column index

    Returns:
        int: number of walls(nonmovable places) around
    """
    count, sum = 0, 0 # count: counts how many places are inside the table
                      # sum: holds how many of these places are nonmovable

    for i in range(max(0, row-1), min(TABLE_ROW, row+2)): 
        for j in range(max(0, column-1), min(TABLE_COLUMN, column+2)):
            count = count + 1 
            if TABLE[i][j] == 1:
                sum = sum + 1
    # 9: default wall heuristic value
    # +sum: increase the value by the number of walls around
    # -decrease the value by the number of possible move places
    # higher wall heuristic means more surrounded place
    return 9 + sum - count

def find_trapping_body_parts(trapped_table, start_row, start_column):
    """finds body parts that trapped the snake

    Args:
        trapped_table (list): copy of table
        start_row (int): row index to start search
        start_column (int): column index to start search

    Returns:
        list: list of trapping body parts
    """
    def find_trapping_body_parts_recursive(trapped_table, row, column, body_parts):
        """finds body parts recursively that trapped the snake

        Args:
            trapped_table (list): copy of table
            row (int): row index of current place
            column (int): column index of current place
            body_parts (list): list of trapping body parts
        """
        # flag the checked places with -2
        if trapped_table[row][column] == 1:
            trapped_table[row][column] = -2
            body_parts.append([row, column])
            return
        
        # flag the checked places with -2
        trapped_table[row][column] = -2

        if row > 0 and trapped_table[row-1][column] != -2:
            find_trapping_body_parts_recursive(trapped_table, row-1, column, body_parts)
        if row < TABLE_ROW-1 and trapped_table[row+1][column] != -2:
            find_trapping_body_parts_recursive(trapped_table, row+1, column, body_parts)
        if column > 0 and trapped_table[row][column-1] != -2:
            find_trapping_body_parts_recursive(trapped_table, row, column-1, body_parts)
        if column < TABLE_COLUMN-1 and trapped_table[row][column+1] != -2:
            find_trapping_body_parts_recursive(trapped_table, row, column+1, body_parts)

    body_parts = []

    if start_row > 0 and TABLE[start_row-1][start_column] != 1:
        find_trapping_body_parts_recursive(trapped_table, start_row-1, start_column, body_parts)
    if start_row < TABLE_ROW-1 and TABLE[start_row+1][start_column] != 1:
        find_trapping_body_parts_recursive(trapped_table, start_row+1, start_column, body_parts)
    if start_column > 0 and TABLE[start_row][start_column-1] != 1:
        find_trapping_body_parts_recursive(trapped_table, start_row, start_column-1, body_parts)
    if start_column < TABLE_COLUMN-1 and TABLE[start_row][start_column+1] != 1:
        find_trapping_body_parts_recursive(trapped_table, start_row, start_column+1, body_parts)
    
    return body_parts

class Snake:
    def __init__(self, name, head_row, head_column):
        """init for Snake class

        Args:
            name (string): snakes name
            head_row (int): snakes heads row index
            head_column (int): snakes heads column index
        """
        self.name = name
        self.point = 0
        self.body = [[int(head_row),int(head_column)], [int(head_row) + 1,int(head_column)], [int(head_row) + 2,int(head_column)]]

        for part in self.body:
            TABLE[part[0]][part[1]] = 1
   
    def select_move(self, snakes):
        """selects next move of snake

        Args:
            snakes (list): list of other snakes on the table

        Returns:
            string: selected move
        """
        # 1- calculate path costs to apple
        cost_table = calculate_cost_table(APPLE_ROW, APPLE_COLUMN, snake=self,)

        # 2- select path with smallest cost
        costs = {'n':float("inf"), 's':float("inf"), 'e':float("inf"), 'w':float("inf")}
        head_row, head_column = self.body[0][0], self.body[0][1]

        if head_row > 0:
            costs['n'] = cost_table[head_row-1][head_column]
        if head_row < TABLE_ROW-1:
            costs['s'] = cost_table[head_row+1][head_column]
        if head_column > 0:
            costs['w'] = cost_table[head_row][head_column-1]
        if head_column < TABLE_COLUMN-1:
            costs['e'] = cost_table[head_row][head_column+1]

        sorted_costs = sorted(costs, key=costs.get, reverse=False)
        smallest = costs[sorted_costs[0]]

        if smallest != float("inf"):
            # 3- if smallest two cost are different select minimum one
            if costs[sorted_costs[0]] != costs[sorted_costs[1]]:
                return min(costs, key=costs.get)
            # 4- if smallest two cost are same, calculate wall_heuristic and select minimum one
            else:
                for key in sorted_costs:
                    if costs[key] == smallest:
                        # subtracting the wall heuristic means more surrounded places should be selected
                        # this way snake is enforced to follow next to walls if there are multiple equal paths
                        costs[key] = costs[key] - wall_heuristic(self, key)
                return min(costs, key=costs.get)

        else: # 5- if snake is trapped
            # 6- calculate which tail parts are reachable
            table_copy = copy.deepcopy(TABLE)
            trapping_body_parts = find_trapping_body_parts(table_copy, self.body[0][0], self.body[0][1])

            # 7- calculate which part belongs to which snake and how far are they to its tail
            snakes_earliest_deleting_parts = [[] for _ in range(len(snakes))]
            for part in trapping_body_parts:
                for e, snake in enumerate(snakes):
                    if part in snake.body:
                        snakes_earliest_deleting_parts[e].append((part, len(snake.body) - snake.body.index(part)))

            snakes_earliest_deleting_parts = [sublist for sublist in snakes_earliest_deleting_parts if len(sublist)>0]
            
            # completely trapped, go north to die
            if len(snakes_earliest_deleting_parts) == 0:
                return 'n'
            
            # 8- select the earliest deleting part among each snakes earliest deleting parts
            earliest_deleting_part = sorted([sorted(sublist, key=lambda x: x[1])[0] for sublist in snakes_earliest_deleting_parts], key= lambda x:x[1])[0][0]

            # 9- calculate cost to earliest deleting part
            trapped_table = calculate_cost_table(earliest_deleting_part[0], earliest_deleting_part[1], snake=self)

            # 10- select path with biggest cost
            costs = {'n':-1, 's':-1, 'e':-1, 'w':-1}
            head_row, head_column = self.body[0][0], self.body[0][1]

            if head_row > 0 and trapped_table[head_row-1][head_column] != float("inf"):
                costs['n'] = trapped_table[head_row-1][head_column]
            if head_row < TABLE_ROW-1 and trapped_table[head_row+1][head_column] != float("inf"):
                costs['s'] = trapped_table[head_row+1][head_column]
            if head_column > 0 and trapped_table[head_row][head_column-1] != float("inf"):
                costs['w'] = trapped_table[head_row][head_column-1]
            if head_column < TABLE_COLUMN-1 and trapped_table[head_row][head_column+1] != float("inf"):
                costs['e'] = trapped_table[head_row][head_column+1]

            sorted_costs = sorted(costs, key=costs.get, reverse=True)
            biggest = costs[sorted_costs[0]]
            
            # 11 - if biggest two cost are different select maximum one
            if costs[sorted_costs[0]] != costs[sorted_costs[1]]:
                return max(costs, key=costs.get)
            # 12- if biggest two cost are same, calculate wall_heuristic and select maximum one
            else:
                for key in sorted_costs:
                    if costs[key] == biggest:
                        # adding the wall heuristic means more surrounded places should have bigger costs
                        # this way snake is enforced to follow next to walls if there are multiple equal paths
                        costs[key] = costs[key] + wall_heuristic(self, key)
                return max(costs, key=costs.get)   

    def get_keyboard_move(self, last_direction):
        start_time = time.time()
        
        move = last_direction
        while time.time() - start_time < MOVE_TIME:
            if keyboard.is_pressed('w'):
                if last_direction != "s":
                    move = "n"
            if keyboard.is_pressed('a'):
                if last_direction != "e":
                    move = "w"
            if keyboard.is_pressed('s'):
                if last_direction != "n":
                    move = "s"
            if keyboard.is_pressed('d'):
                if last_direction != "w":
                    move = "e"
        
        time.sleep(max(0, MOVE_TIME - (time.time() - start_time)))
        return move

    def move(self, direction):
        """moves snake

        Args:
            direction (string): direction to move between north, south, east, west

        Returns:
            string: moved direction
        """
        direction_new_head_dict = {'n': [self.body[0][0]-1,self.body[0][1]], 's': [self.body[0][0]+1,self.body[0][1]], 'e': [self.body[0][0],self.body[0][1]+1], 'w': [self.body[0][0],self.body[0][1]-1]}
        new_head = direction_new_head_dict[direction]

        # moved out of the TABLE or hitted a body part
        if (new_head[0] >= TABLE_ROW or new_head[0] < 0 or new_head[1] >= TABLE_COLUMN or new_head[1] < 0) or (TABLE[new_head[0]][new_head[1]] == 1):
            for part in self.body:
                TABLE[part[0]][part[1]] = 0
            snakes.remove(self)
            snake_points[self.name] = self.point
            return

        self.body.insert(0, new_head)
        if TABLE[new_head[0]][new_head[1]] == 0: # empty place
            TABLE[new_head[0]][new_head[1]] = 1
            TABLE[self.body[-1][0]][self.body[-1][1]] = 0
            del self.body[-1]
        elif TABLE[new_head[0]][new_head[1]] == -1 : # ate an apple
            TABLE[new_head[0]][new_head[1]] = 1
            self.point = self.point + 1
            put_apple()

        return direction

Gabriel = Snake("Gabriel", 5, 2)
Michael = Snake("Michael", 5, 4)
Raphael = Snake("Raphael", 5, 6)
Uriel = Snake("Uriel", 5, 8)
Lucifer = Snake("Lucifer", 5, 10)
lucifers_move = "n"

snakes = [Gabriel, Michael, Raphael, Uriel, Lucifer]
snake_render_dict = {"Gabriel":{"head": "g", "tail": "G"},
                     "Michael":{"head": "M", "tail": "m"},
                     "Raphael":{"head": "R", "tail": "r"},
                     "Uriel":{"head": "U", "tail": "u"},
                     "Lucifer":{"head": "L", "tail": "l"}}
snake_points = {}

put_apple()
while len(snakes) > 0:
    random.shuffle(snakes)
    
    render_table(snakes, snake_render_dict)
    
    if Lucifer in snakes:
        lucifers_move = Lucifer.get_keyboard_move(lucifers_move)
        Lucifer.move(lucifers_move)

    for snake in snakes:
        if snake.name != "Lucifer":
            move = snake.select_move(snakes)
            snake.move(move)

print(snake_points)