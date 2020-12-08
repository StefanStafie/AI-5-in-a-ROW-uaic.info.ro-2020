import PySimpleGUI as sg
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw


def button_image(width, height, color='black', square=True):
    """
    Draws an image with a cross or a circle as a PNG
    :return: the image
    """
    im = Image.new(
        mode='RGBA', size=(width, height), color=(255, 255, 255, 0))
    image = ImageDraw.Draw(im, mode='RGBA')

    image.line((im.size[0] / 2, 0, im.size[0] / 2, im.size[0]), fill="black", width=2)
    image.line((0, im.size[0] / 2, im.size[0], im.size[0] / 2), fill="black", width=2)
    if not square:
        image.ellipse((3, 3, height - 3, height - 3), fill=color)

    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data


class FourInARow:
    def __init__(self):
        self.size = 0
        self.layout = []
        self.matrix = []
        self.x_cells = 10
        self.y_cells = 10
        self.adversary_type = 0
        self.window = sg.Window
        self.first_player = -1
        self.is_swap2 = 0
        self.player_to_put_piece = 0
        self.player_names = []

    def init_table(self):
        """
        Numerical representation, as a matrix (list of lists)
        """
        self.matrix = np.zeros((self.x_cells, self.y_cells))
        if self.adversary_type != 0 and self.first_player == 1:
            self.matrix[int(self.y_cells / 2) - 1][int(self.x_cells / 2)] = 1
        return None

    def init_graphics(self):
        """
        Creates the PySimpleGui layout with buttons and stuff
        :return: None
        """
        menu_def = [['File', ['New Game', 'Exit', ]],
                    ['About', ['Author', ], ],
                    ]
        init_layout = [[sg.Menu(menu_def)]]

        w, h = sg.Window.get_screen_size()  # scale with screen size
        self.size = int(min((w / self.x_cells), (h / self.y_cells) * 0.75))

        counter = 0
        init_layout.append(
            [sg.Text(f"Player at turn: {self.player_names[self.player_to_put_piece]}", key='the_current_player')])
        for line in self.matrix:
            new_line = []
            for item in line:
                if self.adversary_type != 0 and self.first_player == 1:
                    if counter == int(self.y_cells / 2
                                      - 1) * self.x_cells + int(self.x_cells / 2):
                        new_line.append(sg.Button("", key=f"{counter}", button_color=('light gray', 'light gray'),
                                                  image_data=button_image(self.size, self.size, 'black', False),
                                                  border_width=0))
                    else:
                        new_line.append(sg.Button("", key=f"{counter}", button_color=('light gray', 'light gray'),
                                                  image_data=button_image(self.size, self.size, 'gray'),
                                                  border_width=0))
                else:
                    new_line.append(sg.Button("", key=f"{counter}", button_color=('light gray', 'light gray'),
                                              image_data=button_image(self.size, self.size, 'gray'), border_width=0))
                counter += 1
            init_layout.append(new_line)
        self.layout = init_layout

    def update_button(self, player, button):
        """
            changes the color of a single button
            :param player - determines the color of the change
            :param button - the button that needs changing
        """
        if player == 1:
            color = "black"
        else:
            color = "white"
        button.update(image_data=button_image(self.size, self.size, color, False))
        return None

    def new_game(self, adversary_type=1, first_player=1, x_cells=19, y_cells=19, is_swap2=False,
                 player_names=["john", "Lennon"]):
        """
              initialises a new game with certain characteristics
              :param adversary_type  takes 4 values. 0 for human (PvP game), (1, 2, 3) for (easy, medium, hard) difficulty
              :param first_player  -1 if white plays first, 1 if black plays first. Computer is always black
              :param x_cells number of horizontal cells
              :param y_cells number of vertical cells
              :param is_swap2 determines the start sequence of the game
              :param player_names a list with length 2 representing the names of the players
        """
        print(first_player)
        self.x_cells = x_cells
        self.y_cells = y_cells
        self.adversary_type = adversary_type
        self.player_to_put_piece = 0 if first_player == -1 else 1
        self.first_player = first_player
        self.is_swap2 = is_swap2
        self.player_names = player_names

        self.init_table()
        self.init_graphics()

        self.window = sg.Window('4inaROW', self.layout, element_padding=((0, 0), (0, 0)), margins=(0, 0))
        if is_swap2:
            if adversary_type == 0:  # human 
                self.swap_moves(first_player, 3)
                event, values = sg.Window('Select your \"GAME\"',
                                          [[sg.Radio('keep color', "RADIO1", default=True, size=(10, 1))],
                                           [sg.Radio('swap', "RADIO1")],
                                           [sg.Radio('add 2 more stones and let opponent decide', "RADIO1")],
                                           [sg.OK()]], margins=(40, 25)).read(close=True)

                if values[1]:
                    self.player_names = self.player_names[::-1]
                if values[2]:
                    self.swap_moves(first_player, 2)
                    event, values = sg.Window('Select your \"GAME\"',
                                              [[sg.Radio('keep color', "RADIO1", default=True, size=(10, 1))],
                                               [sg.Radio('swap', "RADIO1")],
                                               [sg.OK()]], margins=(40, 25)).read(close=True)
                    if values[1]:
                        self.player_names = self.player_names[::-1]
                self.next_click(first_player * -1)
            else:
                self.next_click(-1)  # the game starts and the app awaits a click from player

    def get_game_info(self):
        """
        Opens a popup in which you can select the Opponent type, the first player, and the dimensions of the playing
        table (all the parameters requested)
        :return: the information needed to start a new_game()
        """
        event, values = sg.Window('Select your \"GAME\"',
                                  [[sg.Text('Player1 name (white):'), sg.InputText()],
                                   [sg.Text('Player2 name (black):'), sg.InputText()],
                                   [sg.Radio('black First', "RADIO1", default=True, size=(10, 1)),
                                    sg.Radio('white First', "RADIO1")],
                                   [sg.Radio('Swap2 start', "RADIO2", default=True, size=(10, 1)),
                                    sg.Radio('Regular start', "RADIO2")],
                                   [sg.Text('table width: '), sg.Spin([i for i in range(4, 20)], initial_value=19)],
                                   [sg.Text('table height'), sg.Spin([i for i in range(4, 20)], initial_value=19)],
                                   [sg.Button("PvP"), sg.Button("easy"), sg.Button("medium"),
                                    sg.Button("hard"), ]
                                   ], margins=(40, 25)).read(
            close=True)

        if event in (sg.WIN_CLOSED, 'Exit'):
            return None
        adversary_type = 0
        if event == "easy":
            adversary_type = 1
        if event == "medium":
            adversary_type = 2
        if event == "hard":
            adversary_type = 3

        if values[2]:
            first_player = 1
        else:
            first_player = -1

        # sanity check
        values_list = []
        for key, value in values.items():
            values_list.append(value)
        print(values_list)
        if int(values_list[6]) in range(20) and int(values_list[6]) not in range(4):
            if int(values_list[7]) in range(20) and int(values_list[7]) not in range(4):
                return adversary_type, first_player, int(values_list[6]), int(values_list[7]), values[2], values_list[
                                                                                                          0:2]
        sg.popup("Table width and height must be  3 < value < 20 ")
        return self.get_game_info()

    def swap_moves(self, player, moves_left=3):
        """
            Processes the next click, which is owned by player
            :param player: the player who clicks
            :param moves_left how many pieces to place
            :return: None
        """
        if moves_left == 0:
            return None

        event, values = self.window.read()
        if event == 'New Game':
            self.window.close()
            a, b, c, d, e, f = self.get_game_info()
            self.new_game(a, b, c, d, e, f)
            return None
        if event == 'Author':
            sg.popup("Iacob Stefan\nStafie Stefan\nStefanica Catalin\n\nAI uaic.info.ro 2020")
            self.next_click(player)
            return None
        if event == 'Exit':
            self.window.close()
            return None
        if event in (sg.WIN_CLOSED, 'Exit'):
            return None
        if self.valid_move(event):
            self.update_button(player, self.window[event])
            self.update_matrix(player, event)
            self.window.refresh()
            self.swap_moves(player * -1, moves_left - 1)
        else:
            self.swap_moves(player, moves_left)

    def next_click(self, player):
        """
        Processes the next click, which is owned by player
        :param player: the player who clicks
        :return: None
        """
        if self.draw():
            sg.popup("'tis a draw.\nequal stength of mind")
            self.window.close()
            a, b, c, d, e, f = self.get_game_info()
            self.new_game(a, b, c, d, e, f)

        if self.ended(self.matrix):
            if self.adversary_type == 0:
                if player == 1:
                    sg.popup("white won")
                else:
                    sg.popup("black won")
            else:
                sg.popup("Computer won")
            self.window.close()
            a, b, c, d, e, f = self.get_game_info()
            self.new_game(a, b, c, d, e, f)
            return None

        event, values = self.window.read()
        if event == 'New Game':
            self.window.close()
            a, b, c, d, e, f = self.get_game_info()
            self.new_game(a, b, c, d, e, f)
            return None
        if event == 'Author':
            sg.popup("Iacob Stefan\nStafie Stefan\nStefanica Catalin\n\nAI uaic.info.ro 2020")
            self.next_click(player)
            return None
        if event == 'Exit':
            self.window.close()
            return None
        if event in (sg.WIN_CLOSED, 'Exit'):
            return None
        if self.valid_move(event):
            self.update_button(player, self.window[event])
            self.update_matrix(player, event)
            self.window.refresh()
            if self.adversary_type == 0:  # for human
                self.player_to_put_piece = (self.player_to_put_piece + 1) % 2
                self.window['the_current_player'].update(
                    f"Player at turn: {self.player_names[self.player_to_put_piece]}")
                self.next_click(player * -1)

            else:  # for machine
                if self.ended(self.matrix):
                    sg.popup("Human won")
                    self.window.close()
                    a, b, c, d, e, f = self.get_game_info()
                    self.new_game(a, b, c, d, e, f)
                # computer moves
                self.window['the_current_player'].update("Player at turn: computer")
                dummy, computer_x, computer_y = self.minimax_with_alfabeta_pruning(self.matrix, 2, 1000000, player)
                self.matrix[computer_y][computer_x] = 1
                self.window[str(computer_y * self.x_cells + computer_x)].update(
                    image_data=button_image(self.size, self.size, "black", False))

                # back to human
                self.window['the_current_player'].update(
                    f"Player at turn: {self.player_names[self.player_to_put_piece]}")
                self.next_click(-1)
        else:
            self.next_click(player)

    def valid_move(self, event):
        """
        Checks if a certain move is valid (the button is grey)
        :param event: button identifier
        :return: True if the move is valid
        """
        event = int(event)
        y = int(event / self.x_cells)
        x = event % self.x_cells
        return self.matrix[y][x] == 0

    def update_matrix(self, player, event):
        """
        Updates a value in matrix with the color of the player
        :param player: the player for which to modify
        :param event: the button indicator
        :return: None
        """
        event = int(event)
        y = int(event / self.x_cells)
        x = event % self.x_cells
        self.matrix[y][x] = player

    def draw(self):
        for i in self.matrix:
            for j in i:
                if j == 0:
                    return 0
        return 1

    def ended(self, evaluated_matrix):
        """
        Checks if the game has reached its end
        :return: True if it has ended
        """
        for x in range(self.x_cells):
            for y in range(self.y_cells):
                if evaluated_matrix[y][x] != 0:
                    if x < self.x_cells - 3:
                        if evaluated_matrix[y][x] == evaluated_matrix[y][x + 1] == evaluated_matrix[y][x + 2] == \
                                evaluated_matrix[y][x + 3]:
                            return True
                    if y < self.y_cells - 3:
                        if evaluated_matrix[y][x] == evaluated_matrix[y + 1][x] == evaluated_matrix[y + 2][x] == \
                                evaluated_matrix[y + 3][x]:
                            return True
                    if x < self.x_cells - 3 and y < self.y_cells - 3:
                        if evaluated_matrix[y][x] == evaluated_matrix[y + 1][x + 1] == evaluated_matrix[y + 2][x + 2] == \
                                evaluated_matrix[y + 3][x + 3]:
                            return True
                if x < self.x_cells - 3 and y < self.y_cells - 3:
                    if evaluated_matrix[y + 3][x] != 0:
                        if evaluated_matrix[y + 3][x] == evaluated_matrix[y + 2][x + 1] == evaluated_matrix[y + 1][
                            x + 2] == \
                                evaluated_matrix[y][x + 3]:
                            return True
        return False

    def generate_move(self, evaluated_matrix, player):
        """
         !!!! OBSOLETE !!!!
        Generates all possible moves for player where the piece is placed adjacent to other pieces
        :param player: the player for which the moves are generated
        :return: None
        """
        generated_matrix = []
        for y in range(self.y_cells):
            for x in range(self.x_cells):
                if (x + 1 < self.x_cells and evaluated_matrix[y][x + 1] != 0) or \
                        (x + 1 < self.x_cells and y + 1 < self.y_cells and evaluated_matrix[y + 1][
                            x + 1] != 0) or \
                        (x + 1 < self.x_cells and y - 1 >= 0 and evaluated_matrix[y - 1][x + 1] != 0) or \
                        (x - 1 >= 0 and y + 1 < self.y_cells and evaluated_matrix[y + 1][x - 1] != 0) or \
                        (x - 1 >= 0 and y - 1 >= 0 and evaluated_matrix[y - 1][x - 1] != 0) or \
                        (x - 1 >= 0 and evaluated_matrix[y][x - 1] != 0) or \
                        (y + 1 < self.y_cells and evaluated_matrix[y + 1][x] != 0) or \
                        (y - 1 >= 0 and evaluated_matrix[y - 1][x] != 0):
                    if evaluated_matrix[y][x] == 0:
                        aux = [[item for item in line] for line in evaluated_matrix]
                        aux[y][x] = player
                        generated_matrix.append([aux, x, y])
        return generated_matrix

    def better_generate_move(self, evaluated_matrix, player):
        """
        Better than the one above
        Improved for efficiency. Instead of choosing positions adjacent to other pieces, it chooses only line ends
        :param evaluated_matrix: the player for which the moves are generated
        :param player:
        :return: None
        """
        generated_matrix = []
        for axis in range(4):
            if axis == 0:
                x_mod = 1
                y_mod = 0
            if axis == 1:
                x_mod = 0
                y_mod = 1
            if axis == 2:
                x_mod = 1
                y_mod = 1
            if axis == 3:
                x_mod = -1
                y_mod = 1
            aux = [[item for item in line] for line in evaluated_matrix]
            for y in range(self.y_cells):
                for x in range(self.x_cells):
                    if (0 <= y + y_mod < self.y_cells) and (0 <= x + x_mod < self.x_cells):
                        if aux[y + y_mod][x + x_mod] < 0 and aux[y][x] < 0:
                            aux[y + y_mod][x + x_mod] *= 10 * abs(aux[y][x])
                        if aux[y + y_mod][x + x_mod] > 0 and aux[y][x] > 0:
                            aux[y + y_mod][x + x_mod] *= 10 * abs(aux[y][x])

            for y in range(self.y_cells):
                for x in range(self.x_cells):
                    if abs(aux[y][x]) >= 10:
                        # the place at the end of a chain (2 or 3 piece)
                        if self.y_cells > y + y_mod > 0 < x + x_mod < self.x_cells and \
                                aux[y + y_mod][x + x_mod] == 0:
                            to_add = [[item for item in line] for line in evaluated_matrix]
                            to_add[y + y_mod][x + x_mod] = player
                            generated_matrix.append([to_add, x + x_mod, y + y_mod])
                        # the place at the start of a 2 piece chain
                        if self.y_cells > y - 2 * y_mod > 0 < x - 2 * x_mod < self.x_cells and \
                                aux[y - 2 * y_mod][x - 2 * x_mod] == 0:
                            to_add = [[item for item in line] for line in evaluated_matrix]
                            to_add[y - 2 * y_mod][x - 2 * x_mod] = player
                            generated_matrix.append([to_add, x - 2 * x_mod, y - 2 * y_mod])
                        # the place at the start of a 3 piece chain
                        if abs(aux[y][x]) >= 100:
                            if self.y_cells > y - 3 * y_mod > 0 < x - 3 * x_mod < self.x_cells and \
                                    aux[y - 3 * y_mod][x - 3 * x_mod] == 0:
                                to_add = [[item for item in line] for line in evaluated_matrix]
                                to_add[y - 3 * y_mod][x - 3 * x_mod] = player
                                generated_matrix.append([to_add, x - 3 * x_mod, y - 3 * y_mod])

        if len(generated_matrix) == 0:
            for y in range(self.y_cells):
                for x in range(self.x_cells):
                    if (x + 1 < self.x_cells and evaluated_matrix[y][x + 1] != 0) or \
                            (x + 1 < self.x_cells and y + 1 < self.y_cells and evaluated_matrix[y + 1][
                                x + 1] != 0) or \
                            (x + 1 < self.x_cells and y - 1 >= 0 and evaluated_matrix[y - 1][x + 1] != 0) or \
                            (x - 1 >= 0 and y + 1 < self.y_cells and evaluated_matrix[y + 1][x - 1] != 0) or \
                            (x - 1 >= 0 and y - 1 >= 0 and evaluated_matrix[y - 1][x - 1] != 0) or \
                            (x - 1 >= 0 and evaluated_matrix[y][x - 1] != 0) or \
                            (y + 1 < self.y_cells and evaluated_matrix[y + 1][x] != 0) or \
                            (y - 1 >= 0 and evaluated_matrix[y - 1][x] != 0):
                        if evaluated_matrix[y][x] == 0:
                            aux = [[item for item in line] for line in evaluated_matrix]
                            aux[y][x] = player
                            generated_matrix.append([aux, x, y])
                            break
        return generated_matrix

    def get_score(self, evaluated_matrix, axis):
        """
        Returns a score for an axis in the matrix.
        :param evaluated_matrix:
        :param axis: 0 for horizontal, 1 for vertical, 2 for \, 3 for /
        :return: None
        """
        if axis == 0:
            x_mod = 1
            y_mod = 0
        if axis == 1:
            x_mod = 0
            y_mod = 1
        if axis == 2:
            x_mod = 1
            y_mod = 1
        if axis == 3:
            x_mod = -1
            y_mod = 1
        aux = [[item for item in line] for line in evaluated_matrix]
        for y in range(self.y_cells):
            for x in range(self.x_cells):
                if (0 <= y + y_mod < self.y_cells) and (0 <= x + x_mod < self.x_cells):
                    if aux[y + y_mod][x + x_mod] < 0 and aux[y][x] < 0:
                        aux[y + y_mod][x + x_mod] *= 10 * abs(aux[y][x])
                    if aux[y + y_mod][x + x_mod] > 0 and aux[y][x] > 0:
                        aux[y + y_mod][x + x_mod] *= 10 * abs(aux[y][x])
        return np.sum(aux)

    def evaluate_state(self, evaluated_matrix):
        """
        Evaluates the current state of the game based on self.matrix using a score calculator. The precision of this
        score defines the "intelligence" of the AI.
        The function takes into consideration more information depending on the difficulty of the AI.
        :return: a score of the table. the score is >0 if the computer is in advantage. <=0 otherwise
        """
        score = self.get_score(evaluated_matrix, 0) + self.get_score(evaluated_matrix, 1)
        if self.adversary_type > 1:
            score += self.get_score(evaluated_matrix, 2)
        if self.adversary_type > 2:
            score += self.get_score(evaluated_matrix, 3)
        return score

    def minimax_with_alfabeta_pruning(self, evaluated_matrix, levels, prev_beta, player):
        """
        Calculates the best move for the player based on the minimax alg with alfa beta optimization
        :param player the player that receives the move advice
        :param evaluated_matrix: the current state of the table
        :param levels: the level count of the tree generated by minimax
        :param prev_beta: the beta for the previous level
        :return: a matrix representing the table generated by the best move
        """
        if levels == 0:  # if the end was reached, return
            return evaluated_matrix, 0, 0

        moves1 = self.better_generate_move(evaluated_matrix, player)  # generate computer moves
        scores1 = []  # values for MIN function
        if self.ended(evaluated_matrix):  # if it is final state, no need to look any further
            return evaluated_matrix, 0, 0
        alfa = -100000000  # initialize alfa with an unreachably low value
        for i in moves1:  # iterate first level, choose MAX
            if self.ended(i[0]):  # if it is a final state, no need to look any further
                return i[0], i[1], i[2]
            moves2 = self.better_generate_move(i[0], -1 * player)  # generate human moves
            scores2 = []  # values for MIN function
            beta = 100000000  # initialize beta with an unreachably high value
            for j in moves2:  # iterate second level, choose min
                if self.ended(j[0]):
                    scores2.append(-10000)
                    break
                scores2.append(
                    0.9 * self.evaluate_state(self.minimax_with_alfabeta_pruning(j[0], levels - 1, beta, player)[0]))
                if beta > scores2[-1]:  # find better minimum
                    beta = scores2[-1]
                if alfa > beta:  # there is no reason to continue on this branch
                    break
            try:
                minimum = np.argmin(scores2)
                scores1.append(scores2[minimum])
            except ValueError:
                scores1.append(0)

            if alfa < scores1[-1]:  # find better maximum
                alfa = scores1[-1]
            if alfa > prev_beta:  # there is no reason to continue on this branch
                return i[0], i[1], i[2]
        try:
            maximum = np.argmax(scores1)
        except ValueError:
            return self.matrix, 0, 0
        return moves1[maximum]


if __name__ == '__main__':
    the_game = FourInARow()
    a, b, c, d, e, f = the_game.get_game_info()
    the_game.new_game(a, b, c, d, e, f)
