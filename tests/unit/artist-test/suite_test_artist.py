import unittest
import test_delete_artist_app
import test_update_artist_app
import test_read_all_artist_app
import test_read_artist_app
import test_create_artist_app

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_delete_artist_app))
suite.addTests(loader.loadTestsFromModule(test_update_artist_app))
suite.addTests(loader.loadTestsFromModule(test_read_all_artist_app))
suite.addTests(loader.loadTestsFromModule(test_read_artist_app))
suite.addTests(loader.loadTestsFromModule(test_create_artist_app))

runner = unittest.TextTestRunner(verbosity=3)
runner.run(suite)