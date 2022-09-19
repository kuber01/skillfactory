from random import randint

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Нельзя стрелять за пределами доски"

class BoardWrongShipException(BoardException):
    pass

class BoardUsedException(BoardException):
    def __str__(self):
        return "По клетке уже стреляли"


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, point):
        return self.x == point.x and self.y == point.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, length, nose_point, direction):
        self.length = length
        self.nose_point = nose_point
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        dots = []
        for i in range(self.length):
            ship_x = self.nose_point.x
            ship_y = self.nose_point.y

            if self.direction == 0:
                ship_x += i

            elif self.direction == 1:
                ship_y += i

            dots.append(Dot(ship_x, ship_y))

        return dots


class Board:
    def __init__(self, hid=False, size=6):
        self.field = [["O"] * size for _ in range(size)]
        self.size = size
        self.hid = hid
        self.live_ships = 0
        self.busy = []
        self.ships = []

    def __str__(self):
        board = ""
        board += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            board += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            board = board.replace("■", "O")
        return board

    def out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for d_x, d_y in near:
                point = Dot(dot.x + d_x, dot.y + d_y)
                if not (self.out(point)) and point not in self.busy:
                    if verb:
                        self.field[point.x][point.y] = "."
                    self.busy.append(point)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()

        if dot in self.busy:
            raise BoardUsedException()

        self.busy.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.lives == 0:
                    self.live_ships += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен")
                    return False
                else:
                    print("Корабль подбит")
                    return True

        self.field[dot.x][dot.y] = "."
        print("Промах")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, player_board, enemy_board):
        self.player_board = player_board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as error:
                print(error)


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Компьютер бьет сюда: {dot.x + 1} {dot.y + 1}")
        return dot


class User(Player):
    def ask(self):
        while True:
            coords = input("Вы ходите:").split()

            if len(coords) != 2:
                print("Введите 2 координаты")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def try_board(self):
        ships = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        tries = 0
        for s in ships:
            while True:
                tries += 1
                if tries > 2000:
                    return None
                ship = Ship(s, Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True

        self.ai = AI(computer, player)
        self.us = User(player, computer)

    def greet(self):
        print("Морской бой")

    def loop(self):
        num = 0
        while True:
            print("Ваша доска")
            print(self.us.player_board)
            print("------------")
            print("Доска компьютера:")
            print(self.ai.player_board)
            print("------------")
            if num % 2 == 0:
                print("Вы ходите")
                repeat = self.us.move()
            else:
                print("Ход компьютера")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.player_board.live_ships == 7:
                print("------------")
                print("Вы выиграли")
                break

            if self.us.player_board.live_ships == 7:
                print("------------")
                print("Компьютер выиграл")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()