import unittest
import elo
import ecf
import random


#: Any tests including random data will be run this often
PASSES = 4000

class ConversionTest(unittest.TestCase):
    def test_ecf_to_elo(self):
        for elem in xrange(PASSES):
            rand_ecf = random.randint(20, 400)
            elo_rating = ecf.ecf_to_elo(rand_ecf)
            self.assertEqual(rand_ecf, elo.elo_to_ecf(elo_rating))


class ECFKnownValues(unittest.TestCase): 
    def setUp(self):
        # WHEN ADDING DATA ALWAYS PROVIDE SOURCES
        self.known_values = (
            # DATA FROM ENGLISH WIKIPEDIA
            # See http://tinyurl.com/4lbfwf
            ((160, 140), (190, 110)), 
            ((160, 100), (170, 90 )),

        )
    def test_known_values(self):
        for key, value in self.known_values:
            self.assertEqual(ecf.get_new_grade(*key), value)

class ELOKnownValues(unittest.TestCase):
    def setUp(self):
        # WHEN ADDING DATA ALWAYS PROVIDE SOURCES
        self.known_values = (
            # DATA FROM GERMAN WIKIPEDIA 
            # See http://tinyurl.com/2b3dku
            ((2577, 2806), (2585, 2798)), 
            ((2806, 2577), (2808, 2575)),
            ((2806, 2577, True), (2803, 2580)), # DRAW
            

        )
    # Make test_known_values once known_values are present!
    def test_known_values(self):
        for key, value in self.known_values:
            self.assertEqual(elo.get_new_rating(*key), value)
            

if __name__ == "__main__":
    unittest.main()
