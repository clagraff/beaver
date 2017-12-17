import unittest
import unittest.mock as mock

import beaver.drivers as drivers


class TestGetExt(unittest.TestCase):
    def test_empty_path(self):
        with self.assertRaises(Exception):
            drivers.get_ext("")
