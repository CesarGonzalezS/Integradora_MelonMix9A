import unittest
import test_read_favorite_on_use
import test_create_favorite_on_use
import test_update_favorite_on_use
import test_delete_favorite_on_use

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_read_favorite_on_use))
suite.addTests(loader.loadTestsFromModule(test_create_favorite_on_use))
suite.addTests(loader.loadTestsFromModule(test_delete_favorite_on_use))
suite.addTests(loader.loadTestsFromModule(test_update_favorite_on_use))

runner = unittest.TextTestRunner(verbosity=3)
runner.run(suite)