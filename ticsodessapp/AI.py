import math
import numpy as np
import time


class Node:
    """  
        Simualates the game as per MCTS algorithm
    """
    def __init__(self, state=np.zeros(81)):
        self.state = state
        self.move = None
        self.parent = None
        self.visits = 0
        self.wins = 0
        self.losses = 0
        self. draws = 0
        self.children = []
        self.expanded = False

    def value(self):
        """  
            returns the value for each node
        """
        if self.visits == 0:
            return 0
        success_percentage = (self.wins + self.draws * 0.5) / self.visits
        return success_percentage

    def computeUCT(self):  # returns best child
        """  
            returns the best child among all the children
        """
        scores = []
        for child in self.children:
            if child.visits == 0:
                scores.append(math.inf)
            else:
                parent_node_visits = child.parent.visits
                assert child.visits <= parent_node_visits
                exploration_term = (
                    math.sqrt(2.0) * math.sqrt(math.log(parent_node_visits) / child.visits))
                scores.append(child.value() + exploration_term)
        best_child_index = np.argmax(scores)
        return self.children[best_child_index]

    def addParent(self, parent):
        self.parent = parent

    def findBestNode(self, marker, board, ticTacToe):
        """  
            calls computeUCT and returns the best child
        """
        try:
            if not self.expanded:
                self.findChildren(marker, board, ticTacToe)
                self.expanded = True
            return self.computeUCT()
        except:
            print(board, ticTacToe.last_move)

    def addNode(self, move, board, marker):
        """  
            new explored moves are added to the state
        """
        node = Node()
        node.state = np.copy(board)
        node.state[move] = marker
        node.move = move
        node.addParent(self)
        return node

    def findChildren(self, marker, board, ticTacToe):
        """  
            find the chldren of the current board for maximum exploitation
        """
        moves = ticTacToe.availableMoves(board)
        for move in moves:
            child = self.addNode(move, board, marker)
            self.children.append(child)


"""  
    checks for the win
"""
def checkWin(board, val):
    for i in range(3):
        if board[i*3] == val and board[i*3+1] == val and board[i*3+2] == val:
            return True
        if board[i] == val and board[i+3] == val and board[i+6] == val:
            return True
    if board[0] == val and board[4] == val and board[8] == val:
        return True
    if board[2] == val and board[4] == val and board[6] == val:
        return True
    return False

"""  
    Important step
    adds the reward to each node
"""
def backPropogate(game_hisory, win, loss, draw):
    if draw == 1:
        for game in game_hisory:
            game.visits += 1
            game.draws += 1
        return
    status = True
    for game in reversed(game_hisory):
        game.visits += 1
        if status:
            game.wins += 1
        else:
            game.losses += 1
        status = not status


class TicTacToe:
    """  
        Class for the board, board list 
        Game is created in this class
        constructor has last move and player marker
    """
    def __init__(self, last_move, marker):
        self.board_list = np.zeros(9)
        self.board = np.zeros(81)
        self.turn = True
        self.last_move = last_move
        self.marker = marker

    """  
        checks if game is over
    """
    def isGameOver(self):
        return checkWin(np.copy(self.board_list), -1) or checkWin(np.copy(self.board_list), 1) or np.all(self.board_list != 0)
    """  
        returns the available moves
    """
    def availableMoves(self, board):
        if np.all(board == 0):
            return [i for i in range(81)]
        if not (self.board_list[self.last_move % 9] == 0 or self.last_move == None):
            ranges = [i for i, j in enumerate(self.board_list) if j == 0]
            return [j for i in ranges for j in range(i*9, (i*9)+9, 1) if board[j] == 0]
        nextRange = (self.last_move % 9) * 9
        return [i for i in range(nextRange, nextRange+9, 1) if board[i] == 0]
    """  
        checks if the subboards are won, if yes then board list is updated
    """
    def checkSubBoardWin(self, board, marker):
        nextRange = math.floor(self.last_move / 9) * 9
        subBoard = board[nextRange:nextRange + 9]
        if checkWin(subBoard, marker):
            self.board_list[math.floor(self.last_move / 9)] = marker
        if np.all(subBoard != 0):
            self.board_list[math.floor(self.last_move / 9)] = -2
    """  
        move is automated by using MCTS algorithm
    """
    def makeMove(self, node, board):
        if self.turn:
            next_move = node.findBestNode(self.marker, np.copy(board), self)
            board[next_move.move] = self.marker
            self.last_move = next_move.move
            self.checkSubBoardWin(np.copy(board), self.marker)
        else:
            next_move = node.findBestNode(self.marker*-1, np.copy(board), self)
            board[next_move.move] = self.marker*-1
            self.last_move = next_move.move
            self.checkSubBoardWin(np.copy(board), self.marker*-1)
        self.turn = not self.turn
        return next_move

    """  
        game is played and the result is checked
        this data is used to find the best node
    """
    def playGame(self, node, board, board_list):
        gameHistory = []
        gameHistory.append(node)
        self.board_list = board_list
        while not self.isGameOver():
            node = self.makeMove(node, board)
            gameHistory.append(node)
        win = 1 if checkWin(np.copy(self.board_list), -1) else 0
        loss = 1 if checkWin(np.copy(self.board_list), 1) else 0
        draw = 1 if (win == 0 and loss == 0) else 0
        backPropogate(gameHistory, win, loss, draw)


"""  
    checks if the sub board is win
"""
def checkSubBoardWin(board, marker, last_move, board_list):
    nextRange = math.floor(last_move / 9) * 9
    subBoard = board[nextRange:nextRange + 9]
    if checkWin(subBoard, marker):
        board_list[math.floor(last_move / 9)] = marker
    if np.all(subBoard != 0):
        board_list[math.floor(last_move / 9)] = -2


"""  
    simulates the game for 3 seconds and the best node is found
"""
def getAIMove(board, boardList, last_move, marker):
    node = Node()
    t_end = time.time() + 3
    while time.time() < t_end:
        t = TicTacToe(last_move, marker)
        t.playGame(node, np.copy(board), np.copy(boardList))
    values = []
    for i in node.children:
        values.append(i.value())
    best_node = node.children[np.argmax(values)]
    return best_node.move


def checktime():
    board = np.zeros(81)
    start = time.time()
    board2 = list(board)
    end = time.time()
