import unittest
import pandas as pd
from src.pipeline import SelectionRules, optimize_team


class OptimizerTests(unittest.TestCase):
    def test_enforces_team_limit_and_size(self):
        rows = [{"team": team, "player": f"{team}{i}", "role": "all-rounder", "predicted_points": 100 - i}
                for team in ("A", "B") for i in range(8)]
        result = optimize_team(pd.DataFrame(rows), SelectionRules())
        self.assertEqual(len(result), 11)
        self.assertLessEqual(result["team"].value_counts().max(), 7)
        self.assertEqual(result.iloc[0]["designation"], "Captain")

    def test_rejects_too_small_pool(self):
        with self.assertRaises(ValueError):
            optimize_team(pd.DataFrame([{"team": "A", "player": "x", "role": "batter", "predicted_points": 1}]))


if __name__ == "__main__":
    unittest.main()
