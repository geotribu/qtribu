import os
import unittest

from qtribu.toolbelt.env_var_parser import EnvVarParser


class TestEnvVarParser(unittest.TestCase):
    """Unit tests for EnvVarParser."""

    def setUp(self) -> None:
        """Prepare the test environment before each test."""
        self.env_backup = dict(os.environ)  # Backup environment variables

    def tearDown(self) -> None:
        """Restore the original environment variables after each test."""
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_int_conversion(self) -> None:
        """Test integer conversion from environment variable"""
        os.environ["MY_INT"] = "42"
        self.assertEqual(EnvVarParser.get_env_var("MY_INT", 0), 42)

    def test_float_conversion(self) -> None:
        """Test float conversion from environment variable"""
        os.environ["MY_FLOAT"] = "3.14"
        self.assertEqual(EnvVarParser.get_env_var("MY_FLOAT", 0.0), 3.14)

    def test_bool_conversion_true(self) -> None:
        """Test bool conversion from environment variable"""
        for true_value in ["1", "true", "yes", "on"]:
            os.environ["MY_BOOL"] = true_value
            self.assertTrue(EnvVarParser.get_env_var("MY_BOOL", False))

    def test_bool_conversion_false(self) -> None:
        """Test bool conversion from environment variable"""
        for false_value in ["0", "false", "no", "off"]:
            os.environ["MY_BOOL"] = false_value
            self.assertFalse(EnvVarParser.get_env_var("MY_BOOL", True))

    def test_bool_invalid_defaults_to_original(self) -> None:
        """Test invalid bool conversion from environment variable"""
        os.environ["MY_BOOL"] = "maybe"
        self.assertFalse(
            EnvVarParser.get_env_var("MY_BOOL", False)
        )  # Default should remain

    def test_string_conversion(self) -> None:
        """Test string conversion from environment variable"""
        os.environ["MY_STRING"] = "Hello, World!"
        self.assertEqual(
            EnvVarParser.get_env_var("MY_STRING", "default"), "Hello, World!"
        )

    def test_default_value_when_env_missing(self) -> None:
        """Test default value is used when environment variable is missing"""
        self.assertEqual(EnvVarParser.get_env_var("MISSING_INT", 99), 99)

    def test_invalid_int_fallback_to_default(self) -> None:
        """Test default value used when the environment variable is not a valid int"""
        os.environ["MY_INT"] = "not_an_int"
        self.assertEqual(EnvVarParser.get_env_var("MY_INT", 10), 10)

    def test_invalid_float_fallback_to_default(self) -> None:
        """Test default value used when the environment variable is not a valid float"""
        os.environ["MY_FLOAT"] = "not_a_float"
        self.assertEqual(EnvVarParser.get_env_var("MY_FLOAT", 1.23), 1.23)

    def test_unsupported_type(self) -> None:
        """Test exception is raised when the type expected is not supported"""
        os.environ["INT_LIST"] = "1,2,3,4"
        self.assertRaises(TypeError, EnvVarParser.get_env_var, "INT_LIST", [1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
