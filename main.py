import time as t
import PySimpleGUI as sg
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw


def button_image(width, height, color='red', square=True):
    """
    Draws an image with a cross or a circle as a PNG
    :return: the image
    """
    im = Image.new(
        mode='RGBA', size=(width, height), color=(255, 255, 255, 0))
    image = ImageDraw.Draw(im, mode='RGBA')

    image.line((im.size[0] / 2, 0, im.size[0] / 2, im.size[0]), fill="black", width=3)
    image.line((0, im.size[0] / 2, im.size[0], im.size[0] / 2), fill="black", width=3)
    if not square:
        image.ellipse((3, 3, height - 3, height - 3), fill=color)

    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data


class Grafica:
    def __init__(self):
        self.size = 0
        self.layout = []
        self.matrice = []
        self.celule_axa_x = 10
        self.celule_axa_y = 10
        self.tip_adversar = 0
        self.window = 0
        self.first_player = -1

    def init_tabla_joc(self):
        """
        Numerical representation, as a matrix (list of lists)
        """
        self.matrice = np.asarray([[0 for i in range(self.celule_axa_x)] for j in range(self.celule_axa_y)])
        if self.tip_adversar != 0 and self.first_player == 1:
            self.matrice[int(self.celule_axa_y / 2) - 1][int(self.celule_axa_x / 2)] = 1

    def init_grafica(self):
        """
        Creates the PySimpleGui layout with buttons and stuff
        :param matrice:
        :return:
        """
        menu_def = [['File', ['New Game', 'Exit', ]],
                    ['About', ['Author', ], ],
                    ]
        init_layout = [[sg.Menu(menu_def)]]

        w, h = sg.Window.get_screen_size()  # scalare in functe de dimensiune ecran
        self.size = int(min((w / self.celule_axa_x), (h / self.celule_axa_y) * 0.75))

        counter = 0
        for line in self.matrice:
            new_line = []
            for item in line:
                if self.tip_adversar != 0 and self.first_player == 1:
                    if counter == int(self.celule_axa_y / 2
                                      - 1) * self.celule_axa_x + int(self.celule_axa_x / 2):
                        new_line.append(sg.Button("", key=f"{counter}", button_color=('gray', 'gray'),
                                                  image_data=button_image(self.size, self.size, 'red', False),
                                                  border_width=0))
                    else:
                        new_line.append(sg.Button("", key=f"{counter}", button_color=('gray', 'gray'),
                                                  image_data=button_image(self.size, self.size, 'gray'),
                                                  border_width=0))
                else:
                    new_line.append(sg.Button("", key=f"{counter}", button_color=('gray', 'gray'),
                                              image_data=button_image(self.size, self.size, 'gray'), border_width=0))
                counter += 1
            init_layout.append(new_line)

        self.layout = init_layout

    def update_grafica(self, player, item):
        """
            changes the color of a single button
            :param player - determines the color of the change
            :param item - the button that needs changing
        """
        if player == 1:
            color = "red"
        else:
            color = "green"
        item.update(image_data=button_image(self.size, self.size, color, False))

    def new_game(self, tip_adversar=1, first_player=1, celule_axa_x=4, celule_axa_y=4):
        """
              initialises a new game with certain characteristics
              :param tip_adversar  takes 4 values. 0 for human (PvP game), (1, 2, 3) for (easy, medium, hard) difficulty
              :param first_player  -1 if green plays first, 1 if red plays first. Computer is always red
              :param celule_axa_x number of horizontal cells
              :param celule_axa_y number of vertical cells
        """
        self.celule_axa_x = celule_axa_x
        self.celule_axa_y = celule_axa_y
        self.tip_adversar = tip_adversar
        self.first_player = first_player

        self.init_tabla_joc()
        self.init_grafica()

        self.window = sg.Window('4inaROW', self.layout, element_padding=((0, 0), (0, 0)), margins=(0, 0))
        self.next_click(-1)  # the game starts and the app awaits a click from player

    def get_game_info(self):
        """
        Opens a popup in which you can select the Opponent type, the first player, and the dimensions of the playing
        table (all the parameters requested)
        :return: the information needed to start a new_game()
        """
        event, values = sg.Window('What kind of \"GAME\" would you like to play?',
                                  [[sg.Radio('Red First', "RADIO1", default=True, size=(10, 1)),
                                    sg.Radio('Green First', "RADIO1")],
                                   [sg.Text('table width: '), sg.Spin([i for i in range(4, 20)], initial_value=8)],
                                   [sg.Text('table height'), sg.Spin([i for i in range(4, 20)], initial_value=8)],
                                   [sg.Button("PvP"), sg.Button("easy"), sg.Button("medium"),
                                    sg.Button("hard"), ]]).read(
            close=True)

        if event in (sg.WIN_CLOSED, 'Exit'):
            return
        if event == "PvP":
            tip_adversar = 0
        if event == "easy":
            tip_adversar = 1
        if event == "medium":
            tip_adversar = 2
        if event == "hard":
            tip_adversar = 3

        if values[0]:
            first_player = 1
        else:
            first_player = -1

        # sanity check
        values_list = []
        for key, value in values.items():
            values_list.append(value)
        if int(values_list[2]) in range(20) and int(values_list[2]) not in range(4):
            if int(values_list[3]) in range(20) and int(values_list[3]) not in range(4):
                return tip_adversar, first_player, int(values_list[2]), int(values_list[3])
        sg.popup("Table width and height must be  3 < value < 20 ")
        return self.get_game_info()

    def next_click(self, player):
        """
        Processes the next click, which is owned by player
        :param player: the player who clicks
        :return:
        """
        print(self.evaluate_state(self.matrice))
        if self.draw():
            sg.popup("'tis a draw.\nequal stength of mind")
            self.window.close()
            a, b, c, d = self.get_game_info()
            self.new_game(a, b, c, d)

        if self.ended(self.matrice):
            if self.tip_adversar == 0:
                if player == 1:
                    sg.popup("Red won")
                else:
                    sg.popup("Green won")
            else:
                sg.popup("Computer won")
            self.window.close()
            a, b, c, d = self.get_game_info()
            self.new_game(a, b, c, d)
            return

        event, values = self.window.read()
        if event == 'New Game':
            self.window.close()
            a, b, c, d = self.get_game_info()
            self.new_game(a, b, c, d)
            return
        if event == 'Author':
            sg.popup("Stafie Stefan\nPython uaic.info.ro 2020")
            self.next_click(player)
            return
        if event == 'Exit':
            self.window.close()
            return
        if event in (sg.WIN_CLOSED, 'Exit'):
            return
        if self.valid_move(event):
            self.update_grafica(player, self.window[event])
            self.update_matrice(player, event)
            self.window.refresh()
            if self.tip_adversar == 0:  # for human
                self.next_click(player * -1)
            else:  # for machine
                if self.ended(self.matrice):
                    sg.popup("Human won")
                    self.window.close()
                    a, b, c, d = self.get_game_info()
                    self.new_game(a, b, c, d)

                dummy, computer_x, computer_y = self.minimax_with_alfabeta_pruning(self.matrice, 2, 1000000)
                self.matrice[computer_y][computer_x] = 1
                self.window[str(computer_y * self.celule_axa_x + computer_x)].update(
                    image_data=button_image(self.size, self.size, "red", False))

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
        y = int(event / self.celule_axa_x)
        x = event % self.celule_axa_x
        return self.matrice[y][x] == 0

    def update_matrice(self, player, event):
        """
        Updates a value in matrix with the color of the player
        :param player: the player for which to modify
        :param event: the button indicator
        :return:
        """
        event = int(event)
        y = int(event / self.celule_axa_x)
        x = event % self.celule_axa_x
        self.matrice[y][x] = player

    def draw(self):
        for i in self.matrice:
            for j in i:
                if j == 0:
                    return 0
        return 1

    def ended(self, evaluated_matrix):
        """
        Checks if the game has reached its end
        :return: True if it has ended
        """
        for x in range(self.celule_axa_x):
            for y in range(self.celule_axa_y):
                if evaluated_matrix[y][x] != 0:
                    if x < self.celule_axa_x - 3:
                        if evaluated_matrix[y][x] == evaluated_matrix[y][x + 1] == evaluated_matrix[y][x + 2] == \
                                evaluated_matrix[y][x + 3]:
                            return True
                    if y < self.celule_axa_y - 3:
                        if evaluated_matrix[y][x] == evaluated_matrix[y + 1][x] == evaluated_matrix[y + 2][x] == \
                                evaluated_matrix[y + 3][x]:
                            return True
                    if x < self.celule_axa_x - 3 and y < self.celule_axa_y - 3:
                        if evaluated_matrix[y][x] == evaluated_matrix[y + 1][x + 1] == evaluated_matrix[y + 2][x + 2] == \
                                evaluated_matrix[y + 3][x + 3]:
                            return True
                if x < self.celule_axa_x - 3 and y < self.celule_axa_y - 3:
                    if evaluated_matrix[y + 3][x] != 0:
                        if evaluated_matrix[y + 3][x] == evaluated_matrix[y + 2][x + 1] == evaluated_matrix[y + 1][
                            x + 2] == \
                                evaluated_matrix[y][x + 3]:
                            return True
        return False

    def generate_move(self, evaluated_matrix, player):
        """
        Generates all possible moves for player where the piece is placed adjacent to other pieces
        :param player: the player for which the moves are generated
        :return:
        """
        generated_matrix = []
        for y in range(self.celule_axa_y):
            for x in range(self.celule_axa_x):
                if (x + 1 < self.celule_axa_x and evaluated_matrix[y][x + 1] != 0) or \
                        (x + 1 < self.celule_axa_x and y + 1 < self.celule_axa_y and evaluated_matrix[y + 1][
                            x + 1] != 0) or \
                        (x + 1 < self.celule_axa_x and y - 1 >= 0 and evaluated_matrix[y - 1][x + 1] != 0) or \
                        (x - 1 >= 0 and y + 1 < self.celule_axa_y and evaluated_matrix[y + 1][x - 1] != 0) or \
                        (x - 1 >= 0 and y - 1 >= 0 and evaluated_matrix[y - 1][x - 1] != 0) or \
                        (x - 1 >= 0 and evaluated_matrix[y][x - 1] != 0) or \
                        (y + 1 < self.celule_axa_y and evaluated_matrix[y + 1][x] != 0) or \
                        (y - 1 >= 0 and evaluated_matrix[y - 1][x] != 0):
                    if evaluated_matrix[y][x] == 0:
                        aux = [[item for item in line] for line in evaluated_matrix]
                        aux[y][x] = player
                        generated_matrix.append([aux, x, y])
        return generated_matrix

    def better_generate_move(self, evaluated_matrix, player):
        """
        Improved for efficiency. Instead of choosing positions adjacent to other pieces, it chooses only line ends
        :param evaluated_matrix: the player for which the moves are generated
        :param player:
        :return:
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
            for y in range(self.celule_axa_y):
                for x in range(self.celule_axa_x):
                    if (0 <= y + y_mod < self.celule_axa_y) and (0 <= x + x_mod < self.celule_axa_x):
                        if aux[y + y_mod][x + x_mod] < 0 and aux[y][x] < 0:
                            aux[y + y_mod][x + x_mod] *= 10 * abs(aux[y][x])
                        if aux[y + y_mod][x + x_mod] > 0 and aux[y][x] > 0:
                            aux[y + y_mod][x + x_mod] *= 10 * abs(aux[y][x])

            for y in range(self.celule_axa_y):
                for x in range(self.celule_axa_x):
                    if abs(aux[y][x]) >= 10:
                        if self.celule_axa_y > y + y_mod > 0 < x + x_mod < self.celule_axa_x and \
                                aux[y + y_mod][x + x_mod] == 0:
                            to_add = [[item for item in line] for line in evaluated_matrix]
                            to_add[y + y_mod][x + x_mod] = player
                            generated_matrix.append([to_add, x + x_mod, y + y_mod])

                        if self.celule_axa_y > y - 3 * y_mod > 0 < x - 3 * x_mod < self.celule_axa_x and \
                                aux[y - 3 * y_mod][x - 3 * x_mod] == 0:
                            to_add = [[item for item in line] for line in evaluated_matrix]
                            to_add[y - 3 * y_mod][x - 3 * x_mod] = player
                            generated_matrix.append([to_add, x - 3 * x_mod, y - 3 * y_mod])

                        if self.celule_axa_y > y - 2 * y_mod > 0 < x - 2 * x_mod < self.celule_axa_x and \
                                aux[y - 2 * y_mod][x - 2 * x_mod] == 0:
                            to_add = [[item for item in line] for line in evaluated_matrix]
                            to_add[y - 2 * y_mod][x - 2 * x_mod] = player
                            generated_matrix.append([to_add, x - 2 * x_mod, y - 2 * y_mod])

        if len(generated_matrix) == 0:
            for y in range(self.celule_axa_y):
                for x in range(self.celule_axa_x):
                    if (x + 1 < self.celule_axa_x and evaluated_matrix[y][x + 1] != 0) or \
                            (x + 1 < self.celule_axa_x and y + 1 < self.celule_axa_y and evaluated_matrix[y + 1][
                                x + 1] != 0) or \
                            (x + 1 < self.celule_axa_x and y - 1 >= 0 and evaluated_matrix[y - 1][x + 1] != 0) or \
                            (x - 1 >= 0 and y + 1 < self.celule_axa_y and evaluated_matrix[y + 1][x - 1] != 0) or \
                            (x - 1 >= 0 and y - 1 >= 0 and evaluated_matrix[y - 1][x - 1] != 0) or \
                            (x - 1 >= 0 and evaluated_matrix[y][x - 1] != 0) or \
                            (y + 1 < self.celule_axa_y and evaluated_matrix[y + 1][x] != 0) or \
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
        :return:
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
        for y in range(self.celule_axa_y):
            for x in range(self.celule_axa_x):
                if (0 <= y + y_mod < self.celule_axa_y) and (0 <= x + x_mod < self.celule_axa_x):
                    if aux[y + y_mod][x + x_mod] < 0 and aux[y][x] < 0:
                        aux[y + y_mod][x + x_mod] *= 10 * abs(aux[y][x])
                    if aux[y + y_mod][x + x_mod] > 0 and aux[y][x] > 0:
                        aux[y + y_mod][x + x_mod] *= 10 * abs(aux[y][x])
        return np.sum(aux)

    def evaluate_state(self, evaluated_matrix):
        """
        Evaluates the current state of the game based on self.matrix using a score calculator. The precision of this
        score defines the "intelligence" of the AI
        :return: a score of the table. the score is >0 if the computer is in advantage. <=0 otherwise
        """
        score = (self.get_score(evaluated_matrix, 0)
                 + self.get_score(evaluated_matrix, 1)
                 + self.get_score(evaluated_matrix, 2)
                 + self.get_score(evaluated_matrix, 3))
        return score

    def minimax_with_alfabeta_pruning(self, evaluated_matrix, levels, prev_beta):
        if levels == 0:  # if the end was reached, return
            return evaluated_matrix, 0, 0

        mutari1 = self.better_generate_move(evaluated_matrix, 1)  # generate computer moves
        # cool_print(mutari1)
        valori1 = []  # values for MIN function
        if self.ended(evaluated_matrix):  # if it is final state, no need to look any further
            return evaluated_matrix, 0, 0
        alfa = -100000000  # initialize alfa with an unreachably low value
        for i in mutari1:  # iterate first level, choose MAX
            if self.ended(i[0]):  # if it is a final state, no need to look any further
                return i[0], i[1], i[2]
            mutari2 = self.better_generate_move(i[0], -1)  # generate human moves
            valori2 = []  # values for MIN function
            beta = 100000000  # initialize beta with an unreachably high value
            # cool_print(mutari2)
            for j in mutari2:  # iterare pe nivel 2, se alege minimul
                if self.ended(j[0]):
                    valori2.append(-10000)
                    break
                valori2.append(self.evaluate_state(self.minimax_with_alfabeta_pruning(j[0], levels - 1, beta)[0]))
                if beta > valori2[-1]:  # daca se gaseste un minim mai bun, se actualizeaza
                    beta = valori2[-1]
                if alfa > beta:  # daca alfa > beta, nu mai are rost sa continuam pe ramura asta
                    break
            try:
                minimum = np.argmin(valori2)
                valori1.append(valori2[minimum])
            except ValueError:
                valori1.append(0)

            if alfa < valori1[-1]:  # daca se gaseste un maxim mai bun, se actualizeaza
                alfa = valori1[-1]
            if alfa > prev_beta:  # daca alfa > prev_beta, nu mai are rost sa continuam pe ramura asta
                return i[0], i[1], i[2]
        try:
            maximum = np.argmax(valori1)
        except ValueError:
            return self.matrice, 0, 0
        return mutari1[maximum]


def cool_print(ultra):
    for i in ultra:
        for line in i[0]:
            print(line)
        print()


if __name__ == '__main__':
    grafica = Grafica()
    grafica.new_game()
