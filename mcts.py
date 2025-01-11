import copy
import time
import random
import math

ROWS = 6
COLS = 7

###############################################################################
#                          MCTS Implementation                                #
###############################################################################
class MCTSNode:
    """
    A node in the MCTS search tree.
    """
    def __init__(self, board, current_player, parent=None):
        self.board = board
        self.current_player = current_player
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = get_valid_moves(board)
    
    def uct_value(self):
        """
        Upper Confidence Bound for Trees (UCT).
        """
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + 1.4142 * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )


def get_valid_moves(board):
    """
    Return a list of all valid columns where a move can be made.
    """
    valid_moves = []
    for col in range(COLS):
        if board[0][col] == ".":
            valid_moves.append(col)
    return valid_moves

def make_move(board, col, player):
    """
    Place the player's piece ('R' or 'Y') in the given column of the board if valid.
    Returns a new board state (copy) with the move applied.
    """
    new_board = copy.deepcopy(board)
    for row in reversed(range(ROWS)):
        if new_board[row][col] == ".":
            new_board[row][col] = player
            break
    return new_board

def check_winner(board, player):
    """
    Check if 'player' has 4 in a row somewhere on the board.
    Returns True if player wins, otherwise False.
    """
    # Horizontal check
    for row in range(ROWS):
        for col in range(COLS - 3):
            if (board[row][col] == player and
                board[row][col+1] == player and
                board[row][col+2] == player and
                board[row][col+3] == player):
                return True
    # Vertical check
    for col in range(COLS):
        for row in range(ROWS - 3):
            if (board[row][col] == player and
                board[row+1][col] == player and
                board[row+2][col] == player and
                board[row+3][col] == player):
                return True
    # Diagonal (down-right) check
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if (board[row][col] == player and
                board[row+1][col+1] == player and
                board[row+2][col+2] == player and
                board[row+3][col+3] == player):
                return True
    # Diagonal (up-right) check
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if (board[row][col] == player and
                board[row-1][col+1] == player and
                board[row-2][col+2] == player and
                board[row-3][col+3] == player):
                return True
    return False

def get_next_player(current_player):
    """
    Switch from 'R' to 'Y' or vice versa.
    """
    return "R" if current_player == "Y" else "Y"

def is_board_full(board):
    """
    Check if the board is completely full (no moves can be made).
    """
    return all(board[0][col] != "." for col in range(COLS))

def simulate_game(board, current_player):
    """
    Simulate a random game (rollout) until we get a winner or a draw.
    Returns 'R' if Red wins, 'Y' if Yellow wins, or None if draw.
    """
    sim_board = copy.deepcopy(board)
    sim_player = current_player
    
    while True:
        moves = get_valid_moves(sim_board)
        if not moves:
            # It's a draw
            return None
        
        # Random move
        col = random.choice(moves)
        sim_board = make_move(sim_board, col, sim_player)
        
        # Check winner
        if check_winner(sim_board, sim_player):
            return sim_player
        
        sim_player = get_next_player(sim_player)

def expand_node(node):
    """
    Expand the MCTS node by taking one untried move and creating a child node.
    """
    move = node.untried_moves.pop()
    new_board = make_move(node.board, move, node.current_player)
    next_player = get_next_player(node.current_player)
    child_node = MCTSNode(new_board, next_player, node)
    node.children.append(child_node)
    return child_node

def best_child(node):
    """
    Select the child with the best UCT value.
    """
    best = None
    best_uct = -float('inf')
    for child in node.children:
        uct_val = child.uct_value()
        if uct_val > best_uct:
            best = child
            best_uct = uct_val
    return best

def backpropagate(node, winner):
    """
    Backpropagate the simulation results up the tree.
    """
    while node is not None:
        node.visits += 1
        # If this node's parent player is the one who ended up winning, 
        # we do an increment. Actually, if the *previous move* was from 
        # node.parent.current_player, we can track it differently.
        # But for simplicity, if winner == node.parent.current_player => node.parent gets credit.
        if winner is not None and winner == get_next_player(node.current_player):
            node.wins += 1
        node = node.parent

def mcts(root_board, current_player, simulations=500, time_limit=1.0):
    """
    Perform MCTS from the root state and return the column of the best move.
    """
    start_time = time.time()
    root_node = MCTSNode(root_board, current_player)
    
    while (time.time() - start_time) < time_limit:
        # 1. Selection
        node = root_node
        while not node.untried_moves and node.children:
            node = best_child(node)
        
        # 2. Expansion
        if node.untried_moves:
            node = expand_node(node)
        
        # 3. Simulation
        winner = simulate_game(node.board, node.current_player)
        
        # 4. Backpropagation
        backpropagate(node, winner)
    
    # After time is up, pick the child with the highest visit count.
    best_move_node = max(root_node.children, key=lambda c: c.visits) if root_node.children else None
    
    if best_move_node is None:
        # fallback if somehow no children
        return random.choice(get_valid_moves(root_board))
    
    # Return the column that leads to best_move_node
    for col in get_valid_moves(root_board):
        candidate_board = make_move(root_board, col, current_player)
        if candidate_board == best_move_node.board:
            return col
    
    return random.choice(get_valid_moves(root_board))

def find_immediate_win_or_block(board, current_player):
    """
    Check if current_player can immediately win,
    or if the opponent can immediately win next turn (then block).
    """
    # Immediate win
    for col in get_valid_moves(board):
        temp_board = make_move(board, col, current_player)
        if check_winner(temp_board, current_player):
            return col
    
    # Block opponent
    opponent = get_next_player(current_player)
    for col in get_valid_moves(board):
        temp_board = make_move(board, col, opponent)
        if check_winner(temp_board, opponent):
            return col
    
    return None

def ai_move(board, current_player, difficulty):
    """
    Decide AI move:
    1. Check immediate win/block
    2. Otherwise use MCTS
    """
    
    # Difficulty is a value between 1 and 5, If values are between 1 and 4, there is a chance of random move
    random_difficulty = random.random()
    # print(random_difficulty)
    if (difficulty == 1 and random_difficulty < 0.2) or \
       (difficulty == 2 and random_difficulty < 0.15) or \
       (difficulty == 3 and random_difficulty < 0.10) or \
       (difficulty == 4 and random_difficulty < 0.05):
      
      # print('random move')
      return random.choice(get_valid_moves(board))
        
    if difficulty == 5:
      col = find_immediate_win_or_block(board, current_player)
    else:
      col = None
                  
    if col is not None:
        return col
                          
    return mcts(board, current_player, simulations=300, time_limit=1.0)
