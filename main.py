from itertools import groupby, product
import os
import random

from polyomino import Polyomino


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

title_godomati = Polyomino([
    (2, 8), (3, 8), (0, 7), (1, 7), (2, 7), (2, 6), (0, 5), (1, 5), (2, 5),
    (5, 8), (5, 7), (7, 7), (8, 7), (5, 6), (6, 6), (7, 6), (8, 6), (5, 5),
    (0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (1, 1), (2, 1), (3, 1), (2, 0),
    (6, 3), (7, 3), (8, 3), (7, 2), (5, 1), (6, 1), (7, 1), (8, 1), (7, 0)
])
plaque = [
    '',
    '          G o d o m a c h i',
    '                               v1.0.0'
]

#############
# Interface #
#############

class Scene:

    def __init__(self, doe):
        if not doe:
            exit()
        self.dialogue, self.options, self.exit_to = doe
        cls()
        self.main()

    def print_dialogue(self):
        print()
        for d in self.dialogue:
            print(d)
        print('      E - Exit\n')

    def take_input(self):
        i = input('godomachi>>> ')
        if i == 'E':
            scenes[self.exit_to]()
        try:
            name = self.options[i]
        except KeyError:
            self.take_input()
        scenes[name]()

    def main(self):
        self.print_dialogue()
        self.take_input()

########
# Play #
########

dialogue_pregame = [
    title_godomati,
    *plaque,
    '      0 - 2 person play',
    '      1 - AI Level 1',
    ''
]
options_pregame = {
    '0': '0',
    '1': '1'
}


class Player:

    def __init__(self, level = 0):
        self.level = level

    def play(self, game):
        def retry():
            game.show_board()
            print('Try again')
            return take_moves()
        if self.level:
            game.play(random.choice(game.get_all_valid_movesets()))
            input('ok>>> ')
        else:
            print('Use commas to separate chosen values.')
            def take_moves():
                moveset = []
                for n, p in enumerate(game.polys, 1):
                    i = input('Player {0} - Polyomino {1} >>> '.format(self.number, n))
                    try:
                        moveset.append([p.number_to_cell[int(cs)] for cs in i.split(',')])
                    except (KeyError, IndexError, ValueError):
                        return retry()
                if game.is_valid_moveset(moveset):
                    return moveset
                return retry()
            game.play(take_moves())


class Game(Scene):

    def __init__(self, players=[0, 1], size_original=15):
        self.players = []
        for i, p in enumerate(players, 1):
            player = Player(p)
            player.number = i
            self.players.append(player)
        self.polys = [Polyomino() for _ in players]
        self.turn = -1
        for poly in self.polys:
            poly.expand_by(size_original)
        self.main()

    def show_board(self):
        cls()
        print()
        for i, p in enumerate(self.polys, 1):
            print('Polyomino {0}'.format(i))
            print(p)
            print()

    def switch_turns(self):
        self.turn += 1
        if self.turn == len(self.players):
            self.turn = 0

    def main(self):
        while not all_equal(Polyomino(p.playfield) for p in self.polys):
            self.switch_turns()
            self.show_board()
            self.players[self.turn].play(self)
        self.show_board()
        level = self.players[self.turn].level
        if level:
            print('AI level {0} wins'.format(level))
        else:
            if self.turn < 0:
                self.turn += len(self.players)
            print('Player {0} wins'.format(self.turn+1))
        input('ok>>>')
        scenes['main']()

    def is_valid_moveset(self, moveset):
        if not all_equal(Polyomino(m) for m in moveset):
            return False
        return all(p.is_valid_move(m) for p, m in zip(self.polys, moveset))

    def get_valid_movesets(self, size):
        movesets = product(*(p.get_valid_moves(size) for p in self.polys))
        return [ms for ms in movesets if self.is_valid_moveset(ms)]

    def get_all_valid_movesets(self):
        size = self.polys[0].size_existing
        valids = []
        for s in range(1, size+1):
            valids.extend(self.get_valid_movesets(s))
        return valids

    def play(self, moveset):
        assert self.is_valid_moveset(moveset)
        for p, m in zip(self.polys, moveset):
            p.play(m)

########
# Main #
########

dialogue_main = [
    title_godomati,
    *plaque,
    '      P - Play',
    '      I - Instructions',
    '      C - Credits'
]
options_main = {
    'P': 'play',
    'I': 'instructions',
    'C': 'credits',
    'E': 'exit'
}

################
# Instructions #
################

dialogue_instructions = [
    '             Instructions',
    '',
    '      Godomachi is a two-player',
    '   game. The game starts with two',
    '   polyominoes. Players take turns',
    '   removing pieces from both',
    '   polyominoes according to the',
    '   following rules.',
    '',
    '   1. The slices must identical in',
    '      shape and size.',
    '      (Reflections & rotations OK)',
    '   2. Each slice and remaining',
    '      polyomino must be connected',
    '      individually.',
    '',
    '     The game ends when remaining',
    '   polyominoes are identical. The',
    '   last player who made a move wins.',
    '     The second player wins if the',
    '   initial polyominoes are the same.',
    '',
    '      Minor variations have been',
    '   introduced for this program.',
    ''
]
options_instructions = {}

###########
# Credits #
###########

dialogue_credits = [
    title_godomati,
    '',
    '         Console Application',
    '                Lolly',
    '',
    '    Godomachi Web Application Team',
    '    Miyoshi Junichi       terasawa',
    '          Tatt             shoko',
    '        tateishi           onewan',
    '           RK              bucchi',
    '         kimura',
    ''
]
options_credits = {}


scenes = {
    'main': lambda: Scene((dialogue_main, options_main, 'exit')),
    'play': lambda: Scene((dialogue_pregame, options_pregame, 'main')),
    '0': lambda: Game([0, 0]),
    '1': lambda: Game([0, 1]),
    'instructions': lambda: Scene((dialogue_instructions, options_instructions, 'main')),
    'credits': lambda: Scene((dialogue_credits, options_credits, 'main')),
    'exit': lambda: exit()
}


if __name__ == '__main__':
    scenes['main']()
