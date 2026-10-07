class Board:
    SIZE = 6

    def __init__(self):
        self.ships = set()
        self.ship_cells = []
        self.shots = set()
        self.hits = set()

    @classmethod
    def _validate_pos(cls, pos):
        if (
            not isinstance(pos, tuple)
            or len(pos) != 2
            or not all(isinstance(value, int) for value in pos)
        ):
            raise ValueError("Position must be a (row, col) tuple of integers.")
        if not (0 <= pos[0] < cls.SIZE and 0 <= pos[1] < cls.SIZE):
            raise ValueError("Position is outside the board.")

    def place_ship(self, cells):
        cells = set(cells)
        if not cells:
            raise ValueError("A ship must contain at least one cell.")

        for pos in cells:
            self._validate_pos(pos)

        if self.ships.intersection(cells):
            raise ValueError("Ship cells overlap an existing ship.")

        self.ships.update(cells)
        self.ship_cells.append(cells)

    def fire(self, pos):
        """Record a shot and return (hit, sunk, ship_index)."""
        self._validate_pos(pos)

        if pos in self.shots:
            return False, False, None

        self.shots.add(pos)

        if pos not in self.ships:
            return False, False, None

        self.hits.add(pos)

        for index, ship in enumerate(self.ship_cells):
            if pos in ship:
                return True, ship <= self.hits, index

        return True, False, None

    def all_sunk(self):
        return bool(self.ship_cells) and all(ship <= self.hits for ship in self.ship_cells)
