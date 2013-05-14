from shapes import Game


def brute_force(game):
    """expects Game game"""
    # solves in original order
    valid_placements = Brute_Valid_Placements(game)
    iters = 0
    for updated_placement in valid_placements:
        iters += 1
        for shape in updated_placement:
            game.remove_shape(shape, shape.current_position)
            game.place_shape(shape, updated_placement[shape])
        if game.solved():
            break
    print('Took {} iterations'.format(iters))


class Brute_Valid_Placements(object):
    """docstring for Brute_Valid_Placements"""
    def __init__(self, game):
        super(Brute_Valid_Placements, self).__init__()
        self.game = game
        self.current_inds = {shape: 0 for shape in game.shapes}
        self.updated_shapes = self.game.shapes
        self.stop_condition = {shape: len(shape.valid_positions)-1 for shape in self.game.shapes}

    def __iter__(self):
        while True:
            yield {shape: shape.valid_positions[self.current_inds[shape]] for shape in self.updated_shapes}
            if self.current_inds == self.stop_condition:
                break
            self.updated_shapes = []
            for shape in self.game.shapes:
                self.updated_shapes.append(shape)
                if self.current_inds[shape] >= self.stop_condition[shape]:
                    self.current_inds[shape] = 0
                else:
                    self.current_inds[shape] += 1
                    break


def main(filename):
    game = Game(filename)
    print('number of possibilities: {}'.format(game.num_possibilities))
    brute_force(game)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('filename', help='The filename to use as input.')

    args = parser.parse_args()

    main(args.filename)
