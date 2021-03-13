
"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

import unittest
import numpy as np

# WA Simulator
import wa_simulator.utils as utils

# -----
# Tests
# -----


class TestWAUtils(unittest.TestCase):
    """Tests various package level things"""

    def test_data_directory(self):
        """Tests the global DATA_DIRECTORY variable"""
        import os.path

        self.assertTrue(os.path.isdir(utils.DATA_DIRECTORY))
        self.assertTrue(os.path.isfile(utils.DATA_DIRECTORY + '/test/test.json'))  # noqa

    def test_get_wa_data_file(self):
        """Tests the get_wa_data_file method"""
        import os.path

        self.assertTrue(os.path.isfile(utils.get_wa_data_file('/test/test.json')))  # noqa
        self.assertTrue(os.path.isfile(utils.get_wa_data_file('test/test.json')))  # noqa
        self.assertFalse(os.path.isfile(utils.get_wa_data_file('test/test2.json')))  # noqa

    def test_set_wa_data_directory(self):
        """Tests the set_wa_data_directory method"""
        import os

        old = utils.DATA_DIRECTORY

        # Absolute
        utils.set_wa_data_directory("/TEST")
        self.assertTrue(utils.DATA_DIRECTORY == "/TEST")
        self.assertTrue(old != "/TEST")

        # Relative
        utils.set_wa_data_directory("TEST")
        self.assertTrue(utils.DATA_DIRECTORY == os.path.join(os.getcwd(), "TEST"))  # noqa
        self.assertTrue(utils.get_wa_data_file('test/test.json') == os.path.join(os.getcwd(), "TEST/test/test.json"))  # noqa
        self.assertFalse(utils.get_wa_data_file('test/test.json') == os.path.join(os.getcwd(), "TEST/test/test2.json"))  # noqa

        # Reset
        utils.set_wa_data_directory(old)
        self.assertTrue(utils.DATA_DIRECTORY == old)

    def test_set_wa_data_directory_temp(self):
        """Tests the set_wa_data_diretory_temp method"""
        import os

        old = utils.DATA_DIRECTORY

        # Absolute
        with utils.set_wa_data_directory_temp("/TEST"):
            self.assertTrue(utils.DATA_DIRECTORY == "/TEST")
            self.assertTrue(old != "/TEST")
        self.assertFalse(utils.DATA_DIRECTORY == "/TEST")

        with utils.set_wa_data_directory_temp("TEST"):
            self.assertTrue(utils.DATA_DIRECTORY == os.path.join(os.getcwd(), "TEST"))  # noqa
            self.assertTrue(utils.get_wa_data_file('test/test.json') == os.path.join(os.getcwd(), "TEST/test/test.json"))  # noqa
            self.assertFalse(utils.get_wa_data_file('test/test.json') == os.path.join(os.getcwd(), "TEST/test/test2.json"))  # noqa
        self.assertTrue(utils.DATA_DIRECTORY == old)

    def test_check_type(self):
        """Tests the check_type method"""

        with self.assertRaises(TypeError):
            utils.check_type("TEST", int, "test", "test")
        with self.assertRaises(TypeError):
            utils.check_type("TEST", bool, "test", "test")
        with self.assertRaises(TypeError):
            utils.check_type(True, str, "test", "test")

        # Doesn't raise
        try:
            utils.check_type("TEST", str, "test", "test")
            utils.check_type(True, bool, "test", "test")
        except:
            self.fail("Raise exception unexpectedly!")

    def test_load_json(self):
        """Tests the load_json method"""

        try:
            j = utils.load_json(utils.get_wa_data_file('test/test.json'))
        except:
            self.fail("Raise exception unexpectedly!")

        self.assertTrue('Name' in j)
        self.assertTrue('Type' in j)
        self.assertTrue('Template' in j)
        self.assertTrue('Properties' in j)

        self.assertTrue(j['Name'] == 'Test GPS Sensor Model')

        self.assertTrue('Update Rate' in j['Properties'])
        self.assertTrue(isinstance(j['Properties'], dict))

    def test_check_field(self):
        """Tests the check_field method"""
        j = utils.load_json(utils.get_wa_data_file('test/test.json'))

        try:
            utils.check_field(j, 'Name')
            utils.check_field(j, 'Test', optional=True)
            utils.check_field(j, 'Template', value='GPS')
            utils.check_field(j, 'Properties', field_type=dict)
            utils.check_field(j['Properties']['Noise Model'], 'Noise Type',
                              field_type=str, allowed_values=['Normal', 'Test'])
        except:
            self.fail("Raise exception unexpectedly!")

        with self.assertRaises(KeyError):
            utils.check_field(j, "Test")
        with self.assertRaises(TypeError):
            utils.check_field(j, "Name", field_type=bool)
        with self.assertRaises(ValueError):
            utils.check_field(j, "Name", value='Noise Model')
        with self.assertRaises(ValueError):
            utils.check_field(j, "Name", value='Noise Model', optional=True)

    def test_check_field_allowed_values(self):
        """Tests the check_field_allowed_values method"""
        j = utils.load_json(utils.get_wa_data_file('test/test.json'))

        try:
            utils.check_field_allowed_values(j, 'Name', ['Test GPS Sensor Model', 'Test', 'Type'])  # noqa
        except:
            self.fail("Raise exception unexpectedly!")

        with self.assertRaises(ValueError):
            utils.check_field_allowed_values(j, 'Name', ['Test', 'Type'])  # noqa


if __name__ == '__main__':
    unittest.main()
