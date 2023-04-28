import gamebot
import checkers
import seaborn as sns
import matplotlib.pyplot as plt
from copy import deepcopy
import json

##COLORS##
#             R    G    B
WHITE = (255, 255, 255)
BLUE = (0,   0, 255)
RED = (255,   0,   0)
BLACK = (0,   0,   0)
GOLD = (255, 215,   0)
HIGH = (160, 190, 255)

##DIRECTIONS##
NORTHWEST = "northwest"
NORTHEAST = "northeast"
SOUTHWEST = "southwest"
SOUTHEAST = "southeast"


game = checkers.Game(loop_mode=True)
game.setup()
bot = gamebot.Bot(game, RED, mid_eval='piece_and_board',
                    end_eval='sum_of_dist', method='alpha_beta', depth=3)

start_board = checkers.Board()
states = bot.generate_all_states(start_board)
gamma = 0.9
delta = 1e-400
max_iter = 10000
V = {}  # Initialize values
V_initial = {}
pi = {} # Initialize policy
print(len(states))
for s in states:
    # if(bot.reward(s) != 0):
    #     print(bot.reward(s))
    V[s.getMatrixAsTuple()] = 0
    V_initial[s.getMatrixAsTuple()] = 0
    pi[s.getMatrixAsTuple()] = None

def value_iteration():
    global V, pi, V_initial, states, gamma, delta, max_iter
    for i in range(max_iter):
        max_diff = 0  # Initialize max difference
        V_new = deepcopy(V_initial)
        for s in states:
            # print(type(s))
            # s.repr_matrix()
            max_val = 0
            game = checkers.Game(loop_mode=False)
            game.setup()
            bot = gamebot.Bot(game, RED, mid_eval='piece_and_board',
                    end_eval='sum_of_dist', method='alpha_beta', depth=3)
            r = bot.reward(s)
            all_moves = []
            for piece_moves in bot._generate_all_possible_moves(s):
                current_pos = piece_moves[0:2]
                for final_pos in piece_moves[2]:
                    all_moves.append([current_pos,final_pos])
            for move in all_moves:
                new_board = deepcopy(s)
                bot._action(move[0], move[1], new_board)   
                
                # Compute state value
                val = r  # Get direct reward
                opponent_piece_moves = bot._generate_all_possible_moves(new_board)
                opponent_moves = []
                for piece_moves in opponent_piece_moves:
                    current_pos = piece_moves[0:2]
                    for final_pos in piece_moves[2]:
                        opponent_moves.append([current_pos,final_pos])
                for opponent_move in opponent_moves:
                    s_next = deepcopy(new_board)
                    bot._action(opponent_move[0], opponent_move[1], s_next)
                    if s_next.getMatrixAsTuple() in V:
                        val += (1.0/len(opponent_moves)) * (
                            gamma * V[s_next.getMatrixAsTuple()]
                        )  # Add discounted downstream values

                # Store value best action so far
                max_val = max(max_val, val)
                # print(val, max_val)
                # Update best policy
                if V[s.getMatrixAsTuple()] < val:
                    pi[s.getMatrixAsTuple()] = move  # Store action with highest value

            V_new[s.getMatrixAsTuple()] = max_val  # Update value with highest value

            # Update maximum difference
            max_diff = max(max_diff, abs(V[s.getMatrixAsTuple()] - V_new[s.getMatrixAsTuple()]))

        # Update value functions
        V = V_new

        V_str = {}
        for key in V:
            V_str[str(key)] = str(V[key])
        
        pi_str = {}
        for key in pi:
            pi_str[str(key)] = str(pi[key])

        # add the data of V to a file in JSON format by clearing the file and appending the data on each iteration 
        with open('value_iteration_data.txt', 'w') as f:
            f.write(str(V_str) + '\n')
            
        with open("value_iteration_data.json", "w") as outfile:
            json.dump(V_str, outfile)

        # add the data of pi to a file
        with open('policy_iteration_data.txt', 'w') as f:
            f.write(str(pi_str )+ '\n')

        with open("policy_iteration_data.json", "w") as outfile:
            json.dump(pi_str, outfile)

        # generate heatmap
        # sns.heatmap(V, annot=True, fmt='.2f', cmap='Blues')
        # plt.show()
        print("Iteration: ", i, "Max diff: ", max_diff)


        # If diff smaller than threshold delta for all states, algorithm terminates
        if max_diff < delta:
            break
    
# value_iteration()
bot._mdp_step()