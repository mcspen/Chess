from DecisionTreeNode import DecisionTreeNode
import time


class AI:

    def __init__(self, game_board, color, first_player, pipe):
        self.game_board = game_board
        self.color = color
        self.pipe = pipe
        self.queue = []
        self.decision_tree = DecisionTreeNode(self.game_board, self.color, first_player, 0, [])
        self.queue.append(self.decision_tree)
        self.run()

    def run(self):
        terminate = False

        while not terminate:
            # Check if anything in pipe
            message_in_pipe = self.pipe.poll()

            # Get message from pipe
            if message_in_pipe:
                pipe_message = self.pipe.recv()

                # If message is terminate, end the looping
                if pipe_message[0] == "terminate":
                    terminate = True

                # If message is update, update the game board
                elif pipe_message[0] == "update":
                    self.update_board(pipe_message[1])

                # If message is move, get move
                elif pipe_message[0] == "move":
                    self.pipe.send(self.get_move())

            # Nothing in pipe, continue to analyze
            else:
                self.analyze_board(1)
        self.pipe.close()

    def update_board(self, game_board):
        # Check if any changes have occurred, if not, return
        if len(self.game_board.history) == len(game_board.history):
            print self.color + ": " + "Nothing to update on board."
            return
        self.game_board = game_board
        print "Last move: " + str(self.game_board.history[-1])
        print "Before updating tree: " + str(self.decision_tree.count_nodes())

        # Trim branches off decision tree
        branch = self.decision_tree.get_branch(self.game_board.history[-1])
        while branch is None:
            self.reset_queue()
            self.analyze_board()
            branch = self.decision_tree.get_branch(self.game_board.history[-1])
            print str(branch)
        self.decision_tree = branch
        print "After updating tree: " + str(self.decision_tree.count_nodes()) + '\n'

        # Remove nodes from queue that are no longer valid
        print "Before updating queue: " + str(len(self.queue))
        self.reset_queue()
        print "After updating queue: " + str(len(self.queue)) + '\n'

    def reset_queue(self):
        self.queue = []
        self.decision_tree.get_leaf_nodes(self.queue)
        self.sort_queue()

    def sort_queue(self):
        self.queue.sort(key=lambda x: x.depth, reverse=False)
        self.queue.sort(key=lambda x: x.evaluation, reverse=True)

    def analyze_board(self, loop_time=1):
        print "Before looping through queue: " + str(len(self.queue))
        self.sort_queue()

        start_time = time.time()
        while len(self.queue) > 0:
            node = self.queue[0]
            node.set_children(self.queue)
            self.queue.remove(node)
            if time.time() - start_time >= loop_time:
                break

        print "Analyzing time: " + str(time.time() - start_time)
        print "Total tree nodes: " + str(self.decision_tree.count_nodes())
        print "Total queue nodes: " + str(len(self.queue)) + '\n'

    def get_move(self):
        # While branch's children is None, analyze board
        while self.decision_tree.children is None:
            self.analyze_board()
        if self.color == "black":
            move = self.decision_tree.eval_tree_2()
        else:
            move = self.decision_tree.eval_tree_1()
        print "AI move: " + str(move) + '\n'
        return move
