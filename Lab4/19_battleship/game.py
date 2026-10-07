from board import Board
from ai import AI


class Battleship:
    def __init__(self):
        self.player = Board()
        self.enemy = Board()
        self.ai = AI()
        self.ai_last_hit = None
        self._setup()

    def _setup(self):
        self.player.place_ship({(1, 1), (1, 2), (1, 3)})
        self.player.place_ship({(4, 0), (5, 0)})

        self.enemy.place_ship({(2, 2), (2, 3), (2, 4)})
        self.enemy.place_ship({(4, 4), (5, 4)})

    def show(self):
        print("\nYour shots are coordinates like 2,3.")
        remaining = len(self.enemy.ships - self.enemy.shots)
        print("Ship cells remaining:", remaining)

    def _player_turn(self, raw):
        try:
            r, c = map(int, raw.split(","))
            pos = (r - 1, c - 1)
        except ValueError:
            print("Use row,col.")
            return "rejected"

        if not (0 <= pos[0] < Board.SIZE and 0 <= pos[1] < Board.SIZE):
            print("Outside board.")
            return "rejected"

        if pos in self.enemy.shots:
            print("Already fired there.")
            return "rejected"

        hit, sunk, _ = self.enemy.fire(pos)

        if hit:
            print("HIT!")
            if sunk:
                print("You sank a ship.")
        else:
            print("MISS!")

        if self.enemy.all_sunk():
            print("You sank the fleet.")
            return "won"

        return "continue"

    def _ai_turn(self):
        ai_pos = self.ai.choose(last_hit=self.ai_last_hit)

        if ai_pos is None:
            print("AI has no remaining shots.")
            return False

        print("AI fired at", f"{ai_pos[0] + 1},{ai_pos[1] + 1}")
        hit, sunk, _ = self.player.fire(ai_pos)

        if hit:
            print("AI scored a hit.")
            self.ai_last_hit = None if sunk else ai_pos
            if sunk:
                print("AI sank a ship.")
        else:
            print("AI missed.")
            # Keep the last successful hit so the AI continues checking
            # the remaining neighbouring cells before returning to random play.

        return self.player.all_sunk()

    def run(self):
        print("Battleship")

        while True:
            self.show()
            raw = input("> ").strip().lower()

            if raw == "q":
                return

            player_result = self._player_turn(raw)

            # Only a valid, non-winning shot gives the AI a turn.
            # Rejected input must not consume a turn.
            if player_result == "rejected":
                continue
            if player_result == "won":
                return

            if self._ai_turn():
                print("The AI sank your fleet.")
                return
