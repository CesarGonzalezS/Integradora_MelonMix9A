import unittest
import test_app_delete_admin
import test_app_read_admin
import test_app_update_admin
import test_app_create_admin

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_app_create_admin))
suite.addTests(loader.loadTestsFromModule(test_app_read_admin))
suite.addTests(loader.loadTestsFromModule(test_app_update_admin))
suite.addTests(loader.loadTestsFromModule(test_app_delete_admin))

runner = unittest.TextTestRunner(verbosity=3)
runner.run(suite)