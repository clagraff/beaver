import unittest
import unittest.mock as mock

import beaver


class TestRun(unittest.TestCase):
    @mock.patch("beaver.subprocess.Popen")
    def test_retcode_exception(self, popen_mock):
        """test_retcode_exception ensures that `beaver.run` will raise
        an exception when it executes a subprocess which returns a non-zero
        execution result."""
        m = mock.MagicMock()
        popen_mock.return_value = m

        m.returncode = 1    # non-zero return value

        with self.assertRaises(Exception):
            beaver.run("echo", "some text goes here")

    @mock.patch("beaver.subprocess.Popen")
    def test_retcode_no_exception(self, popen_mock):
        """test_retcode_exception ensures that `beaver.run` will not raise
        an exception when it executes a subprocess which returns a zero
        execution result."""
        m = mock.MagicMock()
        popen_mock.return_value = m

        m.returncode = 0
        beaver.run("echo", "some text goes here")


class TestPathContext(unittest.TestCase):
    def test_path_context(self):
        # argument: expected
        table = {
            # empty state
            "": {
                "__file__": "",
                "__name__": "",
                "__ext__": "",
                "__dir__": "",
                "__path__": "",
            },
            "/": {
                "__file__": "",
                "__name__": "",
                "__ext__": "",
                "__dir__": "/",
                "__path__": "/",
            },
            "/dir/file": {
                "__file__": "file",
                "__name__": "file",
                "__ext__": "",
                "__dir__": "/dir",
                "__path__": "/dir/file",
            },
            "/dir1/dir2/": {
                "__file__": "",
                "__name__": "",
                "__ext__": "",
                "__dir__": "/dir1/dir2",
                "__path__": "/dir1/dir2/",
            },
            "/dir/file.ext": {
                "__file__": "file.ext",
                "__name__": "file",
                "__ext__": "ext",
                "__dir__": "/dir",
                "__path__": "/dir/file.ext",
            },
            "/dir/file.ext1.ext2": {
                "__file__": "file.ext1.ext2",
                "__name__": "file.ext1",
                "__ext__": "ext2",
                "__dir__": "/dir",
                "__path__": "/dir/file.ext1.ext2",
            },
        }

        for arg in table:
            result = beaver.path_context(arg)
            expected = table[arg]

            self.assertEqual(result, expected)


class TestDoOne(unittest.TestCase):
    @mock.patch("beaver.os.path.isfile")
    def test_file_exceptions(self, mock_isfile):
        mock_isfile.return_value = True
        def side_effect(path):
            return bool(path)
        mock_isfile.side_effect = side_effect

        m = mock.Mock()
        m.template = ""

        with self.assertRaises(Exception):
            beaver.do_one(m)

        m.template = "/some/path"
        m.input = ""

        with self.assertRaises(Exception):
            beaver.do_one(m)

    @mock.patch("beaver.open")
    @mock.patch("beaver.write_output")
    @mock.patch("beaver.run")
    @mock.patch("beaver.load_template")
    @mock.patch("beaver.drivers.parse")
    @mock.patch("beaver.os.path.isfile")
    def test_ensure_posts(
        self, mock_isfile, mock_parse, mock_load_template,
        mock_run, mock_write_output, mock_open
    ):
        m = mock.Mock()
        m.post = [
            "first",
            "second",
            "third"
        ]

        mock_tpl = mock.Mock()
        mock_tpl.return_value = None

        mock_load_template.return_value = mock_tpl

        beaver.do_one(m)

        assert mock_run.call_count == len(m.post)


if __name__ == '__main__':
    unittest.main()
