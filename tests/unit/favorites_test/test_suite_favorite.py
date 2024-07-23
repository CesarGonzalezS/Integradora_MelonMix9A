import unittest
import test_read_favorite
import test_create_favorite
import test_update_favorite
import test_delete_favorite

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_read_favorite))
suite.addTests(loader.loadTestsFromModule(test_create_favorite))
suite.addTests(loader.loadTestsFromModule(test_delete_favorite))
suite.addTests(loader.loadTestsFromModule(test_update_favorite))

runner = unittest.TextTestRunner(verbosity=3)
runner.run(suite)