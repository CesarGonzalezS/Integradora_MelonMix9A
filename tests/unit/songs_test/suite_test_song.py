import unittest
import test_read_song
import test_create_song
import test_update_song
import test_delete_song

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_read_song))
suite.addTests(loader.loadTestsFromModule(test_create_song))
suite.addTests(loader.loadTestsFromModule(test_delete_song))
suite.addTests(loader.loadTestsFromModule(test_update_song))

runner = unittest.TextTestRunner(verbosity=3)
runner.run(suite)