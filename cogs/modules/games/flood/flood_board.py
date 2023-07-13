from copy import deepcopy


COLOR_SQUARES = ["🟥", "🟩", "🟦", "🟧", "🟨", "🟪", "🟫", "⬜"]
COLOR_CIRCLES = ["🔴", "🟢", "🔵", "🟠", "🟡", "🟣", "🟤", "⚪"]


class Node():
    def __init__(self, board, parent_node, color_count: int):
        self.board = board
        self.parent = parent_node
        self.color_count = color_count
    

    def generate_states(self):
        prev_color = COLOR_CIRCLES.index(self.board[0][0])
        
        # Create new node for every color flood option
        new_nodes = []
        for i in range(self.color_count):
            if i == prev_color:
                continue
            
            # Do the flood and create new node
            state = replace(deepcopy(self.board), self.board[0][0], COLOR_SQUARES[i])
            node = Node(replace(state, state[0][0], COLOR_CIRCLES[i]), self, self.color_count)
            new_nodes.append(node)
        
        return new_nodes

    
    def is_solved(self) -> bool:
        color = self.board[0][0]

        for y in range(len(self.board)):
            for x in range(len(self.board)):
                if color != self.board[x][y]:
                    return False
        
        return True


def board_arr_to_str(board):
    board_str = ""
    for row in board:
        for char in row:
            board_str += char
        board_str += "\n"
    
    return board_str


def board_str_to_arr(board: str):
    board_arr = []
    row = []

    for i in range(len(board)):
        if board[i] == "\n":
            board_arr.append(row)
            row = []
        else:
            row.append(board[i])
    
    if len(row) > 0:
        board_arr.append(row)
        
    return board_arr


def replace(board, prev_color: str, new_color: str, x = 0, y = 0):
        board[x][y] = new_color

        # Recursively convert tile's neighbors
        if x > 0 and board[x-1][y] == prev_color:
            board = replace(board, prev_color, new_color, x-1, y)

        if y > 0 and board[x][y-1] == prev_color:
            board = replace(board, prev_color, new_color, x, y-1)
        
        if x < len(board)-1 and board[x+1][y] == prev_color:
            board = replace(board, prev_color, new_color, x+1, y)
        
        if y < len(board)-1 and board[x][y+1] == prev_color:
            board = replace(board, prev_color, new_color, x, y+1)

        return board


def is_single_color(board: str) -> bool:
    current_color = board[0]
    for char in board:
        if char != current_color:
            return False
    return True


def count_color(board, color: str, x = 0, y = 0):
    board[x][y] = "!"
    count = 1

    # Recursively convert tile's neighbors
    if x > 0 and board[x-1][y] == color:
        count += count_color(board, color, x-1, y)

    if y > 0 and board[x][y-1] == color:
        count += count_color(board, color, x, y-1)

    if x < len(board)-1 and board[x+1][y] == color:
        count += count_color(board, color, x+1, y)
    
    if y < len(board)-1 and board[x][y+1] == color:
        count += count_color(board, color, x, y+1)

    return count


def solution_step_count(board, color_count: int) -> int:
    root = Node(board, None, color_count)

    stack = [root]

    visited = set()
    visited.add(root)

    while True:
        # Get the oldest node
        node = stack.pop()

        # If the node is solved return the number of it's parents
        if node.is_solved():
            node_count = 1

            while node.parent != None:
                node = node.parent
                node_count += 1

            return node_count
        
        # Create all possible moves
        nodes = node.generate_states()
        new_nodes = []
        for node in nodes:
            if node not in visited:
                new_nodes.append(node)
        
        # Count the new area of all moves
        color_counts = []
        for node in new_nodes:
            color_counts.append(count_color(deepcopy(node.board), node.board[0][0]))
            visited.add(node)
        
        # Sort both lists by color counts
        index = list(range(len(color_counts)))

        index.sort(key = color_counts.__getitem__)

        color_counts[:] = [color_counts[i] for i in index]
        new_nodes[:] = [new_nodes[i] for i in index]
        
        # Add new nodes to the stack
        for node in new_nodes:
            stack.append(node)