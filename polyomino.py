from itertools import combinations
import random


#########################
# Coordinates utilities #
#########################

def x(cs):
    return cs[0]

def y(cs):
    return cs[1]

def up(cs):
    return x(cs), y(cs) + 1

def down(cs):
    return x(cs), y(cs) - 1

def left(cs):
    return x(cs) - 1, y(cs)

def right(cs):
    return x(cs) + 1, y(cs)

def neighbours(cs):
    return up(cs), down(cs), left(cs), right(cs)

def rotate_cw90(cs):
    return y(cs), -x(cs)

def reflect_x(cs):
    return -x(cs),  y(cs)


class Polyomino:

    sizelimit = 100

    def __init__(self, coords = []):
        self.coords = list(coords)
        self.history = []

    @property
    def number_to_cell(self):
        return dict(enumerate(self.playfield, 1))

    @property
    def cell_to_number(self):
        return dict((self.playfield[n], n+1) for n in range(self.size_existing))

    def __str__(self):
        boxes = []

        corners = [' ', '┌', '┐', '┬', '└', '├', '┼', '┼', '┘', '┼', '┤', '┼', '┴', '┼', '┼', '┼']
        def topleft(cs):
            shared_by = 0
            if up(left(cs)) in self.coords:
                shared_by += 8
            if up(cs) in self.coords:
                shared_by += 4
            if left(cs) in self.coords:
                shared_by += 2
            if cs in self.coords:
                shared_by += 1
            return corners[shared_by]
        def topedge(cs):
            if up(cs) in self.coords or cs in self.coords:
                if up(cs) in self.playfield or cs in self.playfield:
                    return '───'
                return '┈┈┈'
            return '   '
        def top(j):
            top = ['{0}{1}'.format(topleft((i, j)), topedge((i, j))) for i in range(x(self.dimensions))]
            top.append(topleft((x(self.dimensions), j)))
            return ''.join(top)

        def leftedge(cs):
            if left(cs) in self.coords or cs in self.coords:
                if left(cs) in self.playfield or cs in self.playfield:
                    return '│'
                return '┊'
            return ' '
        def middle(cs):
            if cs in self.playfield:
                n = self.cell_to_number[cs]
                if n < 10:
                    return ' {0} '.format(n)
                if n < 100:
                    return ' {0}'.format(n)
                return str(n)   #>sizelimit = 100
            if cs in self.last_move:
                return ' x '
            return ' · '
        def edges(j):
            edges = ['{0}{1}'.format(leftedge((i, j)), middle((i, j))) for i in range(x(self.dimensions))]
            edges.append(leftedge((x(self.dimensions), j)))
            return ''.join(edges)

        for j in range(y(self.dimensions)-1, -1, -1):
            boxes.append(top(j))
            boxes.append(edges(j))
        boxes.append(top(-1))

        return '\n'.join(boxes)

    @property
    def equivalents(self):
        cw90 = self.tf_rotate_cw90()
        cw180 = cw90.tf_rotate_cw90()
        cw270 = cw180.tf_rotate_cw90()
        eqs = [self, cw90, cw180, cw270]
        rest = [poly.tf_reflect_x() for poly in eqs]
        eqs.extend(rest)
        return eqs

    def __eq__(self, poly):
        for p in self.equivalents:
            for q in poly.equivalents:
                if p.coords == q.coords:
                    return True
        return False

    def normalize(self):
        x_min = min(x(cs) for cs in self.coords)
        y_min = min(y(cs) for cs in self.coords)
        self.coords = [(x(cs) - x_min, y(cs) - y_min) for cs in self.coords]
        self.coords.sort(key=x)
        self.coords.sort(key=y, reverse=True)

        self.history = [[(x(cs) - x_min, y(cs) - y_min) for cs in move] for move in self.history]

    def expand_by(self, size):
        assert type(size) is int and 0 < self.size_original + size < self.sizelimit, 'Size limit reached'
        for _ in range(size):
            self.expand_one()
        self.normalize()

    def expand_one(self):
        if not self.coords:
            self.coords.append((0, 0))
        else:
            b = random.choice(self.boundary)
            empty = [n for n in neighbours(b) if n not in self.coords]
            self.coords.append(random.choice(empty))

    def is_boundary(self, cs):
        for n in neighbours(cs):
            if n not in self.coords:
                return True
        return False

    @property
    def boundary(self):
        return [cs for cs in self.coords if self.is_boundary(cs)]

    @property
    def dimensions(self):
        return max(x(cs) for cs in self.coords) + 1, max(y(cs) for cs in self.coords) + 1

    @property
    def size_original(self):
        return len(self.coords)

    ###################
    # Transformations #
    ###################

    def transformation(t):
        def wrapper(self):
            new = t(self)
            new.normalize()
            return new
        return wrapper

    @transformation
    def tf_rotate_cw90(self):
        return Polyomino([rotate_cw90(cs) for cs in self.coords])

    @transformation
    def tf_reflect_x(self):
        return Polyomino([reflect_x(cs) for cs in self.coords])

    ######################
    # Godomati utilities #
    ######################

    @property
    def last_move(self):
        try:
            return self.history[-1]
        except IndexError:
            return []

    @property
    def playfield(self):
        history = [cs for move in self.history for cs in move]  #flattening
        remaining = list(self.coords)
        for cs in history:
            remaining.remove(cs)
        return remaining

    @property
    def size_existing(self):
        return len(self.playfield)

    def existing_neighbours(self, cs):
        return {n for n in neighbours(cs) if n in self.playfield}

    def is_connected(self): #dfs
        checked, coords = set(), [self.playfield[0]]
        while coords:
            cs = coords.pop()
            if cs not in checked:
                checked.add(cs)
                coords.extend(self.existing_neighbours(cs) - checked)
        return len(checked) == self.size_existing

    def is_valid_move(self, coords):
        if not coords or coords == self.playfield:
            return False
        remaining = list(self.playfield)
        for cs in coords:
            if not cs in self.playfield:
                return False
            else:
                remaining.remove(cs)
        return Polyomino(coords).is_connected() and Polyomino(remaining).is_connected()

    def get_valid_moves(self, size):
        valids = []
        for test in combinations(self.playfield, size):
            test = list(test)
            if self.is_valid_move(test) and test not in valids:
                valids.append(test)
        return valids

    def get_all_valid_moves(self):
        valids = []
        for size in range(1, self.size_existing+1):
            valids.extend(self.get_valid_moves(size))
        return valids

    def play(self, coords):
        #assert self.is_valid_move(coords), 'Invalid move'
        self.history.append(coords)
