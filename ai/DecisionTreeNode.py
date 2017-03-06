import copy
import random

colors = ["white", "black"]


class DecisionTreeNode:
    def __init__(self, game_board, color, whose_turn, depth, move_chain):
        self.game_board = game_board
        self.color = color
        self.whose_turn = whose_turn
        self.depth = depth
        self.move_chain = move_chain
        self.evaluation = self.eval_node()
        self.children = None

    def set_children(self, queue):
        self.children = []
        # First set of moves should be of color. Second set should be opposite color, and so on.
        next_move = colors[(colors.index(self.whose_turn) + 1) % 2]

        valid_moves = self.game_board.get_valid_moves(self.whose_turn)
        for move in valid_moves:
            temp_board = copy.deepcopy(self.game_board)
            temp_board.move_wrapper(move[0], move[1], False)
            move_history = (self.whose_turn, move[0], move[1])
            self.children.append(
                DecisionTreeNode(temp_board, self.color, next_move, self.depth+1, self.move_chain + [move_history]))
            queue.append(self.children[-1])

        del self.game_board

    def get_branch(self, last_move):
        # If tree isn't build yet, return self
        if self.children is None:
            return self

        correct_branch = None
        for branch in self.children:
            if branch.move_chain[-1] == last_move:
                correct_branch = branch
                break

        # Return found branch or None if not found
        return correct_branch

    def get_leaf_nodes(self, queue):
        if self.children is None:
            queue.append(self)
        else:
            for child in self.children:
                child.get_leaf_nodes(queue)

    def eval_node(self):
        # Simple game board evaluation function
        score = 0
        for tile in self.game_board.game_board:
            if tile.type != "blank":

                if tile.color == self.color:
                    if tile.type == "king":
                        score += 100
                    elif tile.type == "queen":
                        score += 9
                    elif tile.type == "rook":
                        score += 5
                    elif tile.type == "bishop":
                        score += 3
                    elif tile.type == "knight":
                        score += 3
                    else:
                        score += 1

                else:
                    if tile.type == "king":
                        score -= 100
                    elif tile.type == "queen":
                        score -= 9
                    elif tile.type == "rook":
                        score -= 5
                    elif tile.type == "bishop":
                        score -= 3
                    elif tile.type == "knight":
                        score -= 3
                    else:
                        score -= 1

        return score

    def count_nodes(self):
        count = 0
        if self.children is not None:
            for child in self.children:
                count += child.count_nodes()

        return count + 1

    def eval_tree_1(self):
        # Find the best possible path
        # In version 1, that means find highest evaluation value

        best_eval = -1000
        best_eval_nodes = []

        nodes_to_check = copy.deepcopy(self.children)

        while len(nodes_to_check) > 0:
            node = nodes_to_check[0]
            if node.evaluation > best_eval:
                best_eval = node.evaluation
                best_eval_nodes = [node]
            elif node.evaluation == best_eval:
                best_eval_nodes.append(node)

            if node.children is not None:
                nodes_to_check += node.children
            nodes_to_check.remove(node)

        if len(best_eval_nodes) > 0:
            random_idx = random.randint(0, len(best_eval_nodes)-1)
        else:
            return None, None

        # Determine what is the current move in the move chain by comparing to root
        best_move_chain = best_eval_nodes[random_idx].move_chain
        root_move_chain = self.move_chain
        while len(root_move_chain) > 0:
            if root_move_chain[0] != best_move_chain[0]:
                print "Move chain does not match up with root!"
                print "Root: " + str(root_move_chain) + "     Move chain: " + str(best_move_chain)
            else:
                root_move_chain.remove(root_move_chain[0])
                best_move_chain.remove(best_move_chain[0])

        best_move = best_move_chain[0]

        return best_move[1], best_move[2]

    def eval_tree_2(self):
        # Find the best possible path
        # In version 1, that means find highest evaluation value

        best_eval = -1000
        best_eval_nodes = []
        str_output = [str(self.evaluation)]
        root_depth = self.depth

        nodes_to_check = copy.deepcopy(self.children)

        while len(nodes_to_check) > 0:
            node = nodes_to_check[0]

            # Temp
            while len(str_output) < (node.depth - root_depth + 1):
                str_output.append('')
            str_output[node.depth-root_depth] += str(node.evaluation) + "     "


            # Only evaluate the deepest nodes of a branch
            if node.children is None:
                if node.evaluation > best_eval:
                    best_eval = node.evaluation
                    best_eval_nodes = [node]
                elif node.evaluation == best_eval:
                    best_eval_nodes.append(node)
            else:
                nodes_to_check += node.children
            nodes_to_check.remove(node)

        if len(best_eval_nodes) > 0:
            random_idx = random.randint(0, len(best_eval_nodes)-1)
        else:
            return None, None

        # Determine what is the current move in the move chain by comparing to root
        best_move_chain = best_eval_nodes[random_idx].move_chain
        root_move_chain = self.move_chain
        while len(root_move_chain) > 0:
            if root_move_chain[0] != best_move_chain[0]:
                print "Move chain does not match up with root!"
                print "Root: " + str(root_move_chain) + "     Move chain: " + str(best_move_chain)
            else:
                root_move_chain.remove(root_move_chain[0])
                best_move_chain.remove(best_move_chain[0])

        best_move = best_move_chain[0]
        print ''
        for string in str_output:
            print string
        print ''
        print "Best Eval Score: " + str(best_eval)
        return best_move[1], best_move[2]
