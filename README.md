shapeshifter
============

Python suite to help solve Neopets' Shapeshifter puzzles.  OOP

requires Python 3
Basic Usage:

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
python my_strategy.py simple_input.txt
```

or if you're feeling confident:

```bash
python my_strategy.py input.txt
```

