import random


class AI:
    def __init__(self, size=6):
        self.size = size
        self.tried = set()

    def choose(self, last_hit=None):
        """Return an untried (row, col), preferring neighbours of the last hit."""
        if len(self.tried) == self.size * self.size:
            return None

        options = []
        if last_hit is not None:
            r, c = last_hit
            neighbours = [
                (r - 1, c),
                (r + 1, c),
                (r, c - 1),
                (r, c + 1),
            ]
            options = [
                pos for pos in neighbours
                if 0 <= pos[0] < self.size
                and 0 <= pos[1] < self.size
                and pos not in self.tried
            ]

        if not options:
            options = [
                (r, c)
                for r in range(self.size)
                for c in range(self.size)
                if (r, c) not in self.tried
            ]

        pos = random.choice(options)
        self.tried.add(pos)
        return pos
