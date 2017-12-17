import unittest
import unittest.mock as mock

import beaver.version as version


class TestVersion(unittest.TestCase):
    def test_ensure_existance(self):
        assert version.__version__
