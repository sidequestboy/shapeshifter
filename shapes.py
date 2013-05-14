from functools import total_ordering
from array import array

type_codes = 'BHILQ'


class Game(object):
    """docstring for Game"""
    def __init__(self, filename):
        super(Game, self).__init__()
        raw_board = []
        raw_shapes = []
        dim = None
        with open(filename) as f:
            board, shape = False, False
            for line in (l.replace('\n', '').replace(' ', '') for l in f):
                #print("line='{}'".format(line))
                if line.startswith('Board:'):
                    board, shape = True, False
                    continue
                elif line.startswith('Shapes:'):
                    board, shape = False, True
                    i = 0
                    new_shape = True
                    continue

                if board:
                    if line.startswith('&'):
                        l = line[1:]
                        if l.startswith('dim='):
                            l = l[4:]
                            dim = int(l)
                        else:
                            print('unrecognized option {}'.format(line))
                        continue
                    elif line == '':
                        continue
                    else:
                        raw_board.append(line)
                elif shape:
                    if line == '':
                        if new_shape is False:
                            i += 1
                            new_shape = True
                            continue
                        else:
                            continue  # ignore excess whitespace
                    elif new_shape is False:
                        raw_shapes[i].append(line)
                    elif new_shape is True:  # and line != ''
                        new_shape = False
                        raw_shapes.append([])
                        raw_shapes[i].append(line)
            if raw_board == []:
                print("no board")
                exit(0)

            try:
                self.board = Board(raw_board, dim)
            except NameError as e:
                print("Missing 'Board:' line?")
                raise e
            try:
                self.shapes = Shapes(raw_shapes, self.board)
            except NameError as e:
                print("Missing 'Shapes:' line?")
                raise e
        self.num_possibilities = 1
        for shape in self.shapes:
            shape.pos_bound = (self.board.height-shape.height+1, self.board.width-shape.width+1)
            shape.valid_positions = Positions([(row, col)
                                               for row in range(shape.pos_bound[0])
                                               for col in range(shape.pos_bound[1])
                                               ])
            self.num_possibilities *= len(shape.valid_positions)

        self._goal = [[0]*self.board.width for i in range(self.board.height)]

    def place_shape(self, shape, pos, check=True):
        """expects Shape shape and tuple pos"""
        if check and shape.current_position is not None:
            print('Attempted to place shape on board more than once rejected')
            return
        if check and pos[0] >= 0 and pos[0] < shape.pos_bound[0] \
                and pos[1] >= 0 and pos[1] < shape.pos_bound[1]:
            print('Attempted to place shape off of board rejected')
            return
        if self.board.dim == 2 and shape.dim == 2:
            for row in range(shape.height):
                for col in range(shape.width):
                    self.board.values[pos[0]+row][pos[1]+col] ^= shape[row][col]
        else:
            for row in range(shape.height):
                for col in range(shape.width):
                    self.board[pos[0]+row][pos[1]+col] = (self.board[pos[0]+row][pos[1]+col] + shape[row][col]) % self.board.dim
        shape.current_position = pos

    def remove_shape(self, shape):
        if shape.current_position is None:
            return
        elif self.board.dim == 2 and shape.dim == 2:
            for row in range(shape.height):
                for col in range(shape.width):
                    self.board.values[shape.current_position[0]+row][shape.current_position[1]+col] ^= shape[row][col]
        else:
            for row in range(shape.height):
                    self.board[shape.current_position[0]+row][shape.current_position[1]+col] = \
                        (self.board[shape.current_position[0]+row][shape.current_position[1]+col] -
                            shape[row][col]) % self.board.dim
        shape.current_position = None

    def solved(self):
        """expects Board board"""
        if [list(arr) for arr in self.board.values] == self._goal and \
                all(shape.current_position is not None for shape in self.shapes):
            print('success!')
            print('shapes:')
            print(self.shapes)
            print('places: {}'.format(' '.join([str(a) for a in [shape.current_position for shape in self.shapes]])))
            return True
        else:
            return False


class Positions(object):
    def __init__(self, pos_list):
        super(Positions, self).__init__()
        self.list = pos_list
        self.original_order = ([hash(position) for position in self.list])

    def __iter__(self):
        return iter(self.list)

    def __getitem__(self, key):
        return self.list[key]

    def __len__(self):
        return len(self.list)

    def __str__(self):
        return ' '.join([str(a) for a in self.list])

    def reorder(self, hash_list=None):
        if hash_list is None:
            hash_list = self.original_order
        elif len(hash_list) != len(self.list):
            print('hash_list must have same number of elements as there are possible positions')
            raise IndexError

        current_hash_list = [hash(position) for position in self.list]

        # swaps
        for i in range(len(self.list)):
            temp_position = self.list[i]
            j = current_hash_list.index(hash_list[i])
            self.list[i] = self.list[j]
            self.list[j] = temp_position

    def sort(self):
        self.reorder()


class Shapes(list):
    """simply a wrapper for list of shapes wrt a board"""
    def __init__(self, raw_shape_list, board):
        super(Shapes, self).__init__()
        self.list = [Shape(raw_shape, board.dim) for raw_shape in raw_shape_list]
        self.original_order = ([hash(shape) for shape in self.list])

    def __iter__(self):
        return iter(self.list)

    def __getitem__(self, key):
        return self.list[key]

    def __len__(self):
        return len(self.list)

    def __str__(self):
        return '\n\n'.join([str(shape) for shape in self.list])

    def reorder(self, hash_list=None):
        if hash_list is None:
            hash_list = self.original_order
        elif len(hash_list) != len(self.list):
            print('hash_list must have same number of elements as there are shapes')
            raise IndexError

        current_hash_list = [hash(shape) for shape in self.list]

        # swaps
        for i in range(len(self.list)):
            temp_shape = self.list[i]
            j = current_hash_list.index(hash_list[i])
            self.list[i] = self.list[j]
            self.list[j] = temp_shape

    def sort(self):
        hash_list = [shape.get_size() for shape in self.list].sort()
        self.reorder(hash_list)


class Shape(object):
    """Shape.values is array of strings of bits
    representing shape"""
    def __init__(self, raw_shape, dim=None):
        super(Shape, self).__init__()
        self.dim = dim
        w = len(raw_shape[0])
        for line in raw_shape:
            #print("line='{}'".format(line))
            if len(line) != w:
                print("len('{}') != len('{}')".format(line, w))
                print('Shape dimensions should not be jagged.')
                raise IndexError

            try:
                if min([int(entry) for entry in line]) < 0:
                    print('All Shape entries should be non-negative.')
                    raise ValueError

            except ValueError as e:
                print('All Shape entries should be ints.')
                raise e

        max_value = max([max_from_string(row) for row in raw_shape])
        if dim is None:
            self.dim = max_value + 1
        elif dim < max_value + 1:
            print('provided shape dim is too low for board entries.')
            self.dim = max_value + 1
            print('setting dim = {}'.format(max_value + 1))
        else:
            self.dim = dim

        self.values = get_small_array(raw_shape, self.dim)

        self.width = w
        self.height = len(raw_shape)

        self._string = [[str(value) for value in row] for row in self.values]
        self.pos_bound = None
        self.valid_positions = Positions([])
        self.current_position = None

    def get_size(self):
        return sum(sum(row) for row in self.values)

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def __str__(self):
        """String representation"""
        return '\n'.join([' '.join(row) for row in self._string])

    def __eq__(self, other):
        return True if self.values == other.values else False


def max_from_string(from_string):
    #limit of base 32
    return max([int(ch, 32) for ch in from_string])


def get_small_array(raw, dim):
    success = False
    i = 0
    while success is False:
        try:
            values = []
            for row in raw:
                values.append(array(type_codes[i], [int(c, dim) for c in row]))
            success = True
        except OverflowError as e:
            if i + 1 < len(type_codes) - 1:
                print('rows too long, trying bigger data type')
                success = False
                i += 1
            else:
                print('rows too long for unsigned long long?!')
                raise e
    return values


class Board(object):
    """docstring for Board"""
    def __init__(self, raw_board, dim=None):
        super(Board, self).__init__()
        #print(raw_board)

        for line in raw_board:
            #print("line='{}'".format(line))
            w = len(raw_board[0])
            if len(line) != w:
                print("len('{}') != len('{}')".format(line, w))
                print('Board dimensions should not be jagged.')
                raise IndexError

            try:
                if min([int(entry) for entry in line]) < 0:
                    print('All board entries should be non-negative.')
                    raise ValueError

            except ValueError as e:
                print('All Board entries should be ints.')
                raise e
        #print([int(entry) for entry in line.strip() for line in raw_board])

        max_value = max([max_from_string(row) for row in raw_board])

        if dim is None:
            self.dim = max_value + 1
        elif dim < max_value + 1:
            print('provided board dim is too low for board entries.')
            self.dim = max_value + 1
            print('setting dim = {}'.format(max_value + 1))
        else:
            self.dim = dim
        self.width = w
        self.height = len(raw_board)

        self.values = get_small_array(raw_board, self.dim)

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key):
        if type(key) is int:
            return self.values[key]
        elif type(key) is tuple and len(key) == 2:
            if self.dim == 2:
                if key[1] >= self.width:
                    print('Index out of bounds on board.')
                    raise IndexError
                else:
                    try:
                        return int(str(self.values)[-(self.width-key[1])])
                    except ValueError:
                        return 0
            else:
                return self.values[key[0]][key[1]]
        else:
            print('Expected int or tuple length 2 for board key.')
            raise KeyError

    def __str__(self):
        #print('\n'.join(s_rep))
        return '\n'.join([' '.join([str(value) for value in row]) for row in self.values])


def base_print(num, base):
    """Returns string representation of num in base base
    expects num is type int, base is type int"""

    new_num = str(num % base)
    num = int(num / base)
    while(num >= base):
        new_num = str(num % base) + new_num
        num = int(num / base)
    new_num = str(num % base) + new_num
    return(new_num)


def main():
    base_print(123, 7)
    g = Game('input')
    print(g.board)
    print(g.shapes[1])


if __name__ == '__main__':
    main()
