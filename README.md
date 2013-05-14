shapeshifter
============

Python library to help solve Neopets' Shapeshifter puzzles.  OOP
----------------------------------------------------------------

requires Python 3
###Basic Usage:

```bash
$ git clone https://github.com/jameh/shapeshifter
$ cd shapeshifter
$ ls
```
create new file my_strategy.py with your favourite text editor

my_strategy.py:

```python
from shapes import Game
...
def solve(game):
    """
    Your strategy here
    """
    if game.solved():
        print('success!')
    else:
        print('unsuccessful :(')
...

def main(filename):
    # construct game with filename:
    game = Game(filename)
    solve(game)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('filename', help='The filename to use as input.')

    args = parser.parse_args()

    main(args.filename)
```


```bash
$ python my_strategy.py simple_input.txt
```

or if you're feeling confident:

```bash
$ python my_strategy.py level_31.txt
```


###How do I use shapes.py ?

First, let's cd to where we wish to clone the repository, clone the repository, and open a python shell:

```bash
$ cd ~/Desktop
$ git clone https://github.com/jameh/shapeshifter
$ cd shapeshifter/
$ python
>>>
```

now that we have python shell, let's explore. Import the shapes.py module:

```python
>>> import shapes
```

Now let's create a simple game. One is defined in simple_input.txt.
The game is constructed like so:

```python
>>> game = shapes.Game('simple_input.txt')
```

let's take a look at the board.

```python
>>> print(game.board)
1 0 1 1 0
1 1 0 0 0
1 0 0 0 0
1 0 0 0 0
0 0 0 0 0
```

and the shapes:

```python
>>> print(game.shapes)
1

1
1
1
1

1 1 1 1
1 1 0 0

1
1

1 1
```

We see that we have four shapes to work with.  The rules state that you must place each piece once (and only once) to render the board to all zeros (zero represents the goal state!)
Let's try some configurations of shapes.

```python
>>> game.place_shape(game.shapes[1], (0,0))
>>> print(game.board)
0 0 1 1 0
0 1 0 0 0
0 0 0 0 0
0 0 0 0 0
0 0 0 0 0
```

To make life simpler, we can access an array of valid positions for each shape, zero-indexed relative to the top-left corner of the board at ```shape.valid_positions```. Let's look at where we are allowed to place game.shapes[1].

```python
>>> print(game.shapes[1].valid_positions)
(0, 0) (0, 1) (0, 2) (0, 3) (0, 4) (1, 0) (1, 1) (1, 2) (1, 3) (1, 4)
```

Note that if we try to place the shape again, it will print a warning, and not change the board, since we have not removed it yet!

```python
>>> place_shape(game.shapes[1], (0, 1))
Attempt to place shape on board more than once rejected
```

To remove it, use game.remove_shape():

```python
>>> remove_shape(game.shapes[1])
>>> print(game.board)
1 0 1 1 0
1 1 0 0 0
1 0 0 0 0
1 0 0 0 0
0 0 0 0 0
```

Now we can place the shape in any of the valid positions listed above.

For fun, let's try placing the shape in an invalid position, say (3, 3).

```python
>>> place_shape(game.shapes[1], (3, 3))
Attempted to place shape off of board rejected
```

But wait a minute, did it just check the whole ```valid_positions``` list for (3, 3)? that doesn't seem very efficient! It isn't! For better efficiency, pass the keyword argument ```check=False``` into ```place_shape()```. But be careful, an error will stop execution.

```python
>>> place_shape(game.shapes[1], (3,3), check=False)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "./shapes.py", line 79, in place_shape
    self.board.values[pos[0]+row][pos[1]+col] ^= shape[row][col]
IndexError: list index out of range
```

With this simple example, a brute-force approach works well. Let's try this. brute_force.py will check every possibility in order.

This is easiest to run from the command-line. Exit your python shell, make sure you are in the correct directory and run brute_force.py with input simple_input.txt

```bash
$ pwd
/home/jamie/Desktop/shapeshifter
$ python brute_force.py simple_input.txt
number of possibilities: 800000
success!
shapes:
1

1
1
1
1

1 1 1 1
1 1 0 0

1
1

1 1
places: (0, 0) (0, 0) (0, 0) (0, 0) (0, 0)
Took 1 iterations
```

Now we see how simple of a puzzle that was! brute_force solved that pretty quickly. To see where brute_force meets its limitations, try it on level_31.txt.

Those are the basics!

Some useful attributes of the game objects follow:

```game = shapes.Game('input.txt')```: <-- the game object!  
```game.board``` <-- the board  
```game.board.dim``` <-- the number of states for board squares  
```game.board.height``` <-- the height of the board in squares  
```game.board.width``` <-- the width of the board in squares  
```game.board.values``` <-- list of array()'s of ints (one array() per row)  

```game.shapes``` <-- a list of shapes (wrapped up nicely)  
```game.num_possibilities``` <-- the number of possible configurations of shapes  
```game.place_shape(shape, pos, check=True)``` <-- places Shape shape at tuple pos  
```game.remove_shape(shape)``` <-- removes Shape shape from Board game.board  
```game.solved()``` <-- returns True if game.board is solved and all shapes are used, False otherwise  
```shapes.shape``` <-- a shape (basically list of array()'s of ints wrapped in a class [one array per row])

###How do I enter in a new puzzle?
A puzzle file needs two main things: a 'Board:' line and a 'Shapes:' line.

following the 'Board:' line, you can draw out the board. Every entry should be integer-valued in whatever base up to base 32 (this is the limit to how many board states there can be currently). I've not seen a puzzle with more than 3 states so far. 

The relationship between states is inferred by their numbering; for a given state ```i```, it has a successor state ```(i+1) % game.board.dim``` and a predecessor state ```(i-1) % game.board.dim```. ```game.board.dim``` is also inferred from how many states there exist on your board.  

E.g.

    Board:
    0 0 0 0
    1 0 1 0
    0 2 0 2
    3 0 3 0

The constructor for game.board will infer that ```game.board.dim == 4```, the states map 0 -> 1 -> 2 -> 3 -> 0, and that 0 is the goal state.

if you wish for the board to have more states than would be implicitly inferred, you may add an option line under the 'Board:' line, and before the board, prefacing the option name with an ampersand like so:  

    Board:
    & dim = 4
    0 3 1 1
    3 2 3 1
    3 3 1 1
    0 2 2 1
    1 1 1 0

The available board options are: dim  
Note that the argument will be read as a base-10 integer.  

The 'Shapes:' line syntax is identical to the 'Board:' line syntax except that there are no special options; shapes are pretty much static, and always have dimension 2 as far as I know. Furthermore, shapes are separated by an empty line. 

E.g.

    Shapes:
    1 1 1
    0 0 1
    0 0 1
    1 1 0

    1 1 1
    1 0 1
    1 1 1
    1 0 1

    1 0 1
    1 1 1
    1 0 1
    1 0 1

    1 1 1
    1 0 0
    1 1 1
    1 0 0
    1 1 1

    1 0 1
    1 0 1
    1 1 1
    1 0 1
