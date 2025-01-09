import streamlit as st

from mcts import ROWS, COLS
from mcts import is_board_full, check_winner, get_valid_moves, make_move, ai_move

###############################################################################
#                          Streamlit Frontend                                 #
###############################################################################
def display_board(board, col1):
    """
    Display the board in Streamlit 
    """
    board_str = ""
    for row in range(ROWS):
        row_str = "  "
        for col in range(COLS):
            val = board[row][col]
            if val == "R":
                row_str += "🔴 "
            elif val == "Y":
                row_str += "🟡 "
            else:
                row_str += "⬜ "
        row_str += "<br>"
        board_str += row_str

    # Add column numbers at the bottom
    # board_str += "  " + " ".join(str(i + 1) for i in range(COLS))
    column_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
    board_str += "  "
    board_str += "  " + " ".join(column_numbers)
    board_str += "  "

    with col2:
      st.markdown(
          f"<pre style='font-family: monospace; line-height: 1.5;'>{board_str}</pre>",
          unsafe_allow_html=True,
      )
                    
def init_board():
    """
    Initialize an empty board.
    """
    return [["." for _ in range(COLS)] for _ in range(ROWS)]

def reset_game_state():
    """
    Reset the game state in Streamlit session_state.
    """
    st.session_state.board = init_board()
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.first_choice_made = False
    st.session_state.human_player = None
    st.session_state.ai_player = None
    st.session_state.current_player = None

def main(col1, col2, col3):

    # Initialize session state on first run
    if "board" not in st.session_state:
        reset_game_state()

    if "game_started" not in st.session_state:
        st.session_state.game_started = False

    # Allow user to reset the game at any point
    with col1:
      if st.session_state.game_started:    
        with col3:
          if st.button("Reset Game"):
              reset_game_state()
              st.session_state.game_started = False

    # -------------------------------------------------------------------------
    # 1) If the user hasn't chosen who goes first yet, ask them
    # -------------------------------------------------------------------------
    if not st.session_state.game_started:
        with col1:
            choice = st.radio("Do you want to go first?", ("Yes", "No"))
            if st.button("Start Game"):
                st.session_state.game_started = True
                st.session_state.first_choice_made = True
                if choice == "Yes":
                    st.session_state.human_player = "R"
                    st.session_state.ai_player = "Y"
                    st.session_state.current_player = "R"
                else:
                    st.session_state.human_player = "Y"
                    st.session_state.ai_player = "R"
                    # If user picks "No," that means the AI is Red and goes first
                    st.session_state.current_player = "R"
                st.rerun()

    # Only show the game interface if the game has started
    if st.session_state.game_started:
        # -------------------------------------------------------------------------
        # 2) Display current board state
        # -------------------------------------------------------------------------
        board = st.session_state.board
        display_board(board, col1)

        if st.session_state.game_over:
            with col1:
              if st.session_state.winner == "Human":
                  st.success("You win! Congratulations!", icon="🎉")
                  st.balloons()
              elif st.session_state.winner == "AI":
                  st.error("Computer wins! Better luck next time.", icon="😢")
                  st.snow()
              else:
                  st.warning("It's a draw!")
                
            st.stop()  # Stop execution here, do not show anything else.

        # -------------------------------------------------------------------------
        # 3) Handle the current turn
        # -------------------------------------------------------------------------
        current_player = st.session_state.current_player
        human_player = st.session_state.human_player
        ai_player = st.session_state.ai_player

        # Check if the board is already full or if there's a winner (edge cases)
        if is_board_full(board):
            st.session_state.game_over = True
            st.session_state.winner = None
            st.warning("It's a draw!")
            st.stop()

        if check_winner(board, "R"):
            st.session_state.game_over = True
            # Figure out if human or AI is R
            if human_player == "R":
                st.session_state.winner = "Human"
            else:
                st.session_state.winner = "AI"
            st.rerun()

        if check_winner(board, "Y"):
            st.session_state.game_over = True
            # Figure out if human or AI is Y
            if human_player == "Y":
                st.session_state.winner = "Human"
            else:
                st.session_state.winner = "AI"
            st.rerun()

        # -------------------------------------------------------------------------
        # If it's human's turn, allow the user to pick a column
        # If it's AI's turn, compute the move automatically
        # -------------------------------------------------------------------------
        if current_player == human_player:
            with col1:
                if human_player == "R":
                    st.markdown(f"**Your turn** 🔴: Choose a column:")
                else:
                    st.markdown(f"**Your turn** 🟡: Choose a column:")
            valid_moves = get_valid_moves(board)
            columns = [str(c+1) for c in valid_moves]

            with col1:

                button_col1, button_col2 = st.columns(2)
              
                with button_col1:
                  chosen_col = st.number_input("Pick a column", min_value=1, max_value=7, value=1, step=1, key="human_move_select")
                if st.button("Make Move"):
                    col_index = int(chosen_col) - 1
                    if col_index in valid_moves:
                        new_board = make_move(board, col_index, human_player)
                        st.session_state.board = new_board
                        if check_winner(new_board, human_player):
                            st.session_state.game_over = True
                            st.session_state.winner = "Human"
                        elif is_board_full(new_board):
                            st.session_state.game_over = True
                            st.session_state.winner = None
                        else:
                            st.session_state.current_player = ai_player
                        st.rerun()
        else:
            with col1:
                if ai_player == "R":
                    st.markdown(f"**AI's turn** 🔴.")
                else:
                    st.markdown(f"**AI's turn** 🟡.")
            valid_moves = get_valid_moves(board)
            if not valid_moves:
                st.session_state.game_over = True
                st.session_state.winner = None
                st.rerun()
            else:
                col = ai_move(board, ai_player)
                new_board = make_move(board, col, ai_player)
                st.session_state.board = new_board
                if check_winner(new_board, ai_player):
                    st.session_state.game_over = True
                    st.session_state.winner = "AI"
                elif is_board_full(new_board):
                    st.session_state.game_over = True
                    st.session_state.winner = None
                else:
                    st.session_state.current_player = human_player
                st.rerun()
                                
if __name__ == "__main__":
  
    st.set_page_config(layout="wide")

    st.title("Connect Four")
    
    st.markdown(
        """
        Connect Four game where you play against the computer.
        The computer uses the Monte Carlo Tree Search (MCTS) algorithm to decide its moves.
        """
    )
    
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
  
    main(col1, col2, col3)