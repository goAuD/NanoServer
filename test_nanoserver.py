"""
NanoServer Unit Tests
Tests for non-UI components: config, server utilities, database.
Run with: python -m pytest test_nanoserver.py -v
Or simply: python test_nanoserver.py
"""

import unittest
import tempfile
import os
import json

from config import Config, trace_execution
from database import DatabaseManager, is_read_query
from server import is_port_in_use, find_available_port


class TestConfig(unittest.TestCase):
    """Tests for configuration module."""
    
    def setUp(self):
        """Create temporary directory for config."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config(config_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary files."""
        config_file = os.path.join(self.temp_dir, "config.json")
        if os.path.exists(config_file):
            os.remove(config_file)
        os.rmdir(self.temp_dir)
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        self.assertEqual(self.config.port, 8000)
        self.assertEqual(self.config.last_project, "")
    
    def test_save_and_load(self):
        """Test saving and loading config."""
        self.config.last_project = "/test/path"
        self.config.port = 9000
        
        # Create new config instance to test loading
        config2 = Config(config_dir=self.temp_dir)
        self.assertEqual(config2.last_project, "/test/path")
        self.assertEqual(config2.port, 9000)
    
    def test_get_set(self):
        """Test get/set methods."""
        self.config.set("custom_key", "custom_value")
        self.assertEqual(self.config.get("custom_key"), "custom_value")
        self.assertIsNone(self.config.get("nonexistent"))


class TestDatabase(unittest.TestCase):
    """Tests for database module."""
    
    def test_is_read_query_basic(self):
        """Test basic SELECT detection."""
        self.assertTrue(is_read_query("SELECT * FROM users"))
        self.assertTrue(is_read_query("select * from users"))
        self.assertTrue(is_read_query("  SELECT * FROM users"))
        self.assertTrue(is_read_query("PRAGMA table_info(users)"))
        self.assertTrue(is_read_query("EXPLAIN SELECT * FROM users"))
    
    def test_is_read_query_write(self):
        """Test write query detection."""
        self.assertFalse(is_read_query("INSERT INTO users VALUES (1)"))
        self.assertFalse(is_read_query("UPDATE users SET name='x'"))
        self.assertFalse(is_read_query("DELETE FROM users"))
        self.assertFalse(is_read_query("DROP TABLE users"))
    
    def test_is_read_query_injection(self):
        """Test SQL injection tricks are handled."""
        # Semicolon prefix attack
        self.assertTrue(is_read_query(";;;SELECT * FROM users"))
        self.assertFalse(is_read_query(";;; INSERT INTO users VALUES (1)"))
        
        # Whitespace variations
        self.assertTrue(is_read_query("\n\t  SELECT * FROM users"))
        self.assertFalse(is_read_query("\n\t  DELETE FROM users"))
    
    def test_is_read_query_comments(self):
        """Test SQL comments are handled."""
        self.assertTrue(is_read_query("-- comment\nSELECT * FROM users"))
        self.assertTrue(is_read_query("/* block */ SELECT * FROM users"))
    
    def test_database_manager_no_path(self):
        """Test database manager without path set."""
        db = DatabaseManager()
        success, result = db.execute("SELECT 1")
        self.assertFalse(success)
        self.assertIn("No database", result)
    
    def test_database_manager_with_temp_db(self):
        """Test database operations with temporary database."""
        # Create temp database
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
            temp_db = f.name
        
        try:
            db = DatabaseManager(temp_db)
            
            # Create table
            success, _ = db.execute("CREATE TABLE test (id INTEGER, name TEXT)")
            self.assertTrue(success)
            
            # Insert
            success, result = db.execute("INSERT INTO test VALUES (1, 'Alice')")
            self.assertTrue(success)
            
            # Select
            success, result = db.execute("SELECT * FROM test")
            self.assertTrue(success)
            self.assertEqual(result['count'], 1)
            self.assertEqual(result['rows'][0], (1, 'Alice'))
            
            # List tables
            tables = db.list_tables()
            self.assertIn('test', tables)
            
        finally:
            os.remove(temp_db)
    
    def test_validate_table_name_valid(self):
        """Test valid table names."""
        from database import validate_table_name
        self.assertTrue(validate_table_name("users"))
        self.assertTrue(validate_table_name("User_Profiles"))
        self.assertTrue(validate_table_name("_private"))
        self.assertTrue(validate_table_name("table123"))
    
    def test_validate_table_name_invalid(self):
        """Test invalid table names are rejected."""
        from database import validate_table_name
        self.assertFalse(validate_table_name("123table"))  # starts with number
        self.assertFalse(validate_table_name("drop;users"))  # SQL injection attempt
        self.assertFalse(validate_table_name("table-name"))  # hyphen not allowed
        self.assertFalse(validate_table_name(""))  # empty
    
    def test_read_only_mode(self):
        """Test read-only mode blocks write queries."""
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
            temp_db = f.name
        
        try:
            db = DatabaseManager(temp_db)
            
            # Create table first (write allowed by default)
            success, _ = db.execute("CREATE TABLE test (id INTEGER)")
            self.assertTrue(success)
            
            # Enable read-only mode
            db.read_only = True
            
            # Write should be blocked
            success, result = db.execute("INSERT INTO test VALUES (1)")
            self.assertFalse(success)
            self.assertIn("Read-only mode", result)
            
            # Read should still work
            success, _ = db.execute("SELECT * FROM test")
            self.assertTrue(success)
        finally:
            os.remove(temp_db)


class TestServer(unittest.TestCase):
    """Tests for server module utilities."""
    
    def test_is_port_in_use(self):
        """Test port detection."""
        # Port 80 might be in use, but high ports usually aren't
        result = is_port_in_use(59999)
        self.assertIsInstance(result, bool)
    
    def test_find_available_port(self):
        """Test finding available port."""
        port = find_available_port(50000, max_attempts=5)
        # Should find some port in the 50000-50004 range
        self.assertIsNotNone(port)
        self.assertGreaterEqual(port, 50000)
        self.assertLess(port, 50005)


class TestDecorator(unittest.TestCase):
    """Tests for trace_execution decorator."""
    
    def test_decorator_preserves_function(self):
        """Test that decorator doesn't break function."""
        @trace_execution
        def test_func(x, y):
            return x + y
        
        result = test_func(2, 3)
        self.assertEqual(result, 5)
    
    def test_decorator_preserves_name(self):
        """Test that decorator preserves function name."""
        @trace_execution
        def my_function():
            pass
        
        self.assertEqual(my_function.__name__, "my_function")


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
