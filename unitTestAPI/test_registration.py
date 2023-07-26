import unittest

from testRegistrationAPI import TestRegistrationResource

if __name__ == '__main__':
    # create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRegistrationResource)

    # run the test suite
    unittest.TextTestResult(verbosity=2).run(test_suite)
