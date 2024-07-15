import unittest
import test_app_delete_album
import test_app_read_album
import test_app_update_album
import test_app_create_album

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_app_create_album))
suite.addTests(loader.loadTestsFromModule(test_app_read_album))
suite.addTests(loader.loadTestsFromModule(test_app_update_album))
suite.addTests(loader.loadTestsFromModule(test_app_delete_album))

runner = unittest.TextTestRunner(verbosity=3)
runner.run(suite)