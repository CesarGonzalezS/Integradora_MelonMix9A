import unittest
import songs_test.test_read_song as test_read_song
import songs_test.test_create_song as test_create_song
import songs_test.test_update_song as test_update_song
import songs_test.test_delete_song as test_delete_song

import admin_test.test_app_read_admin as test_app_read_admin
import admin_test.test_app_create_admin as test_app_create_admin

import albums_test.test_app_read_album as test_app_read_album
import albums_test.test_app_create_album as test_app_create_album
import albums_test.test_app_update_album as test_app_update_album
import albums_test.test_app_delete_album as test_app_delete_album

import artist_test.test_create_artist_app as test_create_artist_app
import artist_test.test_read_artist_app as test_read_artist_app
import artist_test.test_update_artist_app as test_update_artist_app
import artist_test.test_delete_artist_app as test_delete_artist_app
import artist_test.test_read_all_artist_app as test_read_all_artist_app

import test_user.test_app_read_user as test_app_read_user

import tests.unit.cognito.test_login as test_login
import tests.unit.cognito.test_sign_up as test_sign_up
import tests.unit.cognito.test_confirm_sign_up as test_confirm_sign_up

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_read_song))
suite.addTests(loader.loadTestsFromModule(test_create_song))
suite.addTests(loader.loadTestsFromModule(test_delete_song))
suite.addTests(loader.loadTestsFromModule(test_update_song))

suite.addTests(loader.loadTestsFromModule(test_app_create_admin))
suite.addTests(loader.loadTestsFromModule(test_app_read_admin))

suite.addTests(loader.loadTestsFromModule(test_app_read_album))
suite.addTests(loader.loadTestsFromModule(test_app_create_album))
suite.addTests(loader.loadTestsFromModule(test_app_update_album))
suite.addTests(loader.loadTestsFromModule(test_app_delete_album))

suite.addTests(loader.loadTestsFromModule(test_create_artist_app))
suite.addTests(loader.loadTestsFromModule(test_read_artist_app))
suite.addTests(loader.loadTestsFromModule(test_update_artist_app))
suite.addTests(loader.loadTestsFromModule(test_delete_artist_app))
suite.addTests(loader.loadTestsFromModule(test_read_all_artist_app))

suite.addTests(loader.loadTestsFromModule(test_app_read_user))

suite.addTests(loader.loadTestsFromModule(test_login))
suite.addTests(loader.loadTestsFromModule(test_sign_up))
suite.addTests(loader.loadTestsFromModule(test_confirm_sign_up))


runner = unittest.TextTestRunner(verbosity=3)
runner.run(suite)