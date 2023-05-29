#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

import unittest

if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover(".")
    unittest.TextTestRunner(verbosity=1).run(testsuite)
