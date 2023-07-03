"""Unit tests for plans.py.
"""
import unittest


from src.reading_plan.writers import num_to_word

class TestReadingPlanWriter(unittest.TestCase):
    """Test class for ReadingPlanWriter."""

    def test_num_to_word_below_1000(self) -> None:
        """Test that numbers below 1000 be converted into words.
        """

        self.assertEqual(num_to_word(1), 'One')
        self.assertEqual(num_to_word(17), 'Seventeen')
        self.assertEqual(num_to_word(27), 'Twenty-Seven')
        self.assertEqual(num_to_word(999), 'Nine Hundred Ninety-Nine')

    def test_num_to_word_above_999_and_below_0(self) -> None:
        """Test that numbers above 999 throw an error.
        """

        # Validate that 999 does not throw error.
        num_to_word(999)
        # Validate that 1000 breaks fine.
        with self.assertRaises(NotImplementedError):
            num_to_word(1000)
        # Validate that 0 breaks fine.
        with self.assertRaises(NotImplementedError):
            num_to_word(0)


if __name__ == '__main__':
    unittest.main()
