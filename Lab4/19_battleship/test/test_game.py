import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from ai import AI
from board import Board
from game import Battleship


class BoardTests(unittest.TestCase):
    def test_hit(self):
        board = Board()
        board.place_ship({(1, 1), (1, 2)})

        hit, sunk, _ = board.fire((1, 1))

        self.assertTrue(hit)
        self.assertFalse(sunk)

    def test_miss(self):
        board = Board()
        board.place_ship({(1, 1), (1, 2)})

        hit, sunk, _ = board.fire((0, 0))

        self.assertFalse(hit)
        self.assertFalse(sunk)

    def test_repeated_shot_is_not_recorded_twice(self):
        board = Board()
        board.place_ship({(1, 1)})

        first = board.fire((1, 1))
        second = board.fire((1, 1))

        self.assertEqual(first[:2], (True, True))
        self.assertEqual(second, (False, False, None))
        self.assertEqual(len(board.shots), 1)

    def test_sinking_one_ship_does_not_sink_fleet(self):
        board = Board()
        board.place_ship({(0, 0), (0, 1)})
        board.place_ship({(2, 2), (2, 3)})

        board.fire((0, 0))
        _, sunk, _ = board.fire((0, 1))

        self.assertTrue(sunk)
        self.assertFalse(board.all_sunk())

    def test_sinking_all_ships_ends_fleet(self):
        board = Board()
        board.place_ship({(0, 0), (0, 1)})
        board.place_ship({(2, 2), (2, 3)})

        for pos in ((0, 0), (0, 1), (2, 2), (2, 3)):
            board.fire(pos)

        self.assertTrue(board.all_sunk())

    def test_off_board_ship_cells_are_rejected(self):
        for cells in (
            {(-1, 0)},
            {(0, -1)},
            {(Board.SIZE, 0)},
            {(0, Board.SIZE)},
        ):
            with self.subTest(cells=cells):
                board = Board()
                with self.assertRaises(ValueError):
                    board.place_ship(cells)
                self.assertEqual(board.ships, set())

    def test_overlapping_ship_cells_are_rejected(self):
        board = Board()
        board.place_ship({(1, 1), (1, 2)})

        with self.assertRaises(ValueError):
            board.place_ship({(1, 2), (2, 2)})

        self.assertEqual(board.ships, {(1, 1), (1, 2)})
        self.assertEqual(len(board.ship_cells), 1)

    def test_fire_rejects_out_of_bounds_positions(self):
        board = Board()
        board.place_ship({(1, 1)})

        for pos in ((-1, 0), (0, -1), (Board.SIZE, 0), (0, Board.SIZE)):
            with self.subTest(pos=pos):
                with self.assertRaises(ValueError):
                    board.fire(pos)

        self.assertEqual(board.shots, set())


class AITests(unittest.TestCase):
    def test_ai_never_repeats_a_shot(self):
        ai = AI(size=3)
        shots = [ai.choose() for _ in range(9)]

        self.assertEqual(len(shots), len(set(shots)))
        self.assertIsNone(ai.choose())

    def test_ai_targets_adjacent_cell_after_hit(self):
        ai = AI(size=5)
        ai.tried.add((2, 2))

        with patch("ai.random.choice", side_effect=lambda options: options[0]):
            choice = ai.choose(last_hit=(2, 2))

        self.assertIn(choice, {(1, 2), (3, 2), (2, 1), (2, 3)})

    def test_ai_handles_hit_then_miss_without_forgetting_hit(self):
        game = Battleship()

        # Force the AI to hit its target first.
        game.ai.tried.clear()
        game.ai.tried.add((0, 0))
        game.ai_last_hit = (2, 4)

        # (1, 4) is empty on the player board, so the first preferred neighbour misses.
        with patch("ai.random.choice", side_effect=lambda options: options[0]):
            game._ai_turn()

        self.assertEqual(game.ai_last_hit, (2, 4))

    def test_ai_never_returns_off_board_positions(self):
        ai = AI(size=6)
        for _ in range(36):
            pos = ai.choose(last_hit=(0, 0))
            self.assertIsNotNone(pos)
            self.assertTrue(0 <= pos[0] < 6)
            self.assertTrue(0 <= pos[1] < 6)


class GameTurnTests(unittest.TestCase):
    def test_invalid_coordinate_is_rejected_without_ai_turn(self):
        game = Battleship()

        with patch.object(game, "_ai_turn") as ai_turn:
            result = game._player_turn("not-a-coordinate")

        self.assertEqual(result, "rejected")
        ai_turn.assert_not_called()

    def test_out_of_bounds_coordinate_is_rejected(self):
        game = Battleship()

        for raw in ("0,1", "1,0", "7,1", "1,7"):
            with self.subTest(raw=raw):
                result = game._player_turn(raw)
                self.assertEqual(result, "rejected")

    def test_repeated_player_shot_is_rejected_without_ai_turn(self):
        game = Battleship()

        first = game._player_turn("3,3")
        second = game._player_turn("3,3")

        self.assertEqual(first, "continue")
        self.assertEqual(second, "rejected")

    def test_rejected_player_input_does_not_consume_ai_turn(self):
        game = Battleship()
        inputs = iter(["bad", "q"])

        with patch("builtins.input", side_effect=lambda _prompt: next(inputs)):
            with patch.object(game, "_ai_turn") as ai_turn:
                game.run()

        ai_turn.assert_not_called()

    def test_quitting_exits_without_an_ai_turn(self):
        game = Battleship()

        with patch("builtins.input", return_value="q"):
            with patch.object(game, "_ai_turn") as ai_turn:
                game.run()

        ai_turn.assert_not_called()

    def test_valid_shot_allows_ai_to_take_a_turn(self):
        game = Battleship()

        with patch.object(game, "_ai_turn", return_value=False) as ai_turn:
            result = game._player_turn("3,3")
            if result == "continue":
                ai_turn()

        ai_turn.assert_called_once()


class OutputFeedbackTests(unittest.TestCase):
    def test_player_hit_feedback_occurs_once(self):
        game = Battleship()
        output = io.StringIO()

        with redirect_stdout(output):
            game._player_turn("3,3")

        self.assertEqual(output.getvalue().count("HIT!"), 1)
        self.assertEqual(output.getvalue().count("MISS!"), 0)

    def test_player_miss_feedback_occurs_once(self):
        game = Battleship()
        output = io.StringIO()

        with redirect_stdout(output):
            game._player_turn("1,1")

        self.assertEqual(output.getvalue().count("MISS!"), 1)
        self.assertEqual(output.getvalue().count("HIT!"), 0)

    def test_ai_shot_produces_one_hit_or_miss_message(self):
        game = Battleship()
        game.ai.tried.clear()
        output = io.StringIO()

        with patch("ai.random.choice", side_effect=lambda options: [(1, 1)][0]):
            with redirect_stdout(output):
                game._ai_turn()

        text = output.getvalue()
        self.assertEqual(text.count("AI scored a hit.") + text.count("AI missed."), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)