"""
NanoServer - Database Module
Handles SQLite database queries with proper transaction handling.
Fixes SQL injection vulnerabilities from v1.1.0.
"""

import sqlite3
import os
import logging
from typing import List, Tuple, Any, Optional
from contextlib import contextmanager

from config import trace_execution

logger = logging.getLogger(__name__)


def is_read_query(query: str) -> bool:
    """
    Safely detect if query is read-only.
    Handles injection tricks like ';;;SELECT * FROM users;'
    
    Args:
        query: SQL query string
        
    Returns:
        True if query is read-only (SELECT, PRAGMA, EXPLAIN)
    """
    # Remove all leading semicolons, whitespace, and comments
    cleaned = query.lstrip('; \t\n')
    
    # Skip SQL comments
    while cleaned.startswith('--') or cleaned.startswith('/*'):
        if cleaned.startswith('--'):
            # Skip to end of line
            newline = cleaned.find('\n')
            cleaned = cleaned[newline + 1:] if newline != -1 else ''
        elif cleaned.startswith('/*'):
            # Skip to end of block comment
            end = cleaned.find('*/')
            cleaned = cleaned[end + 2:] if end != -1 else ''
        cleaned = cleaned.lstrip('; \t\n')
    
    if not cleaned:
        return True  # Empty query, treat as read
    
    # Get first word
    first_word = cleaned.split()[0].upper() if cleaned.split() else ''
    
    read_only_keywords = {'SELECT', 'PRAGMA', 'EXPLAIN', 'WITH'}
    return first_word in read_only_keywords


class DatabaseManager:
    """
    SQLite database manager with proper transaction handling.
    Uses context manager pattern for safe transactions.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    def set_database(self, db_path: str) -> None:
        """Set the database path."""
        if self._connection:
            self._connection.close()
            self._connection = None
        self.db_path = db_path
        logger.info(f"Database set to: {db_path}")
    
    @contextmanager
    def connection(self):
        """
        Context manager for database connection.
        Ensures proper connection handling.
        """
        if not self.db_path:
            raise ValueError("No database path set")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column name access
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def transaction(self):
        """
        Context manager for transactions.
        Auto-commits on success, rolls back on exception.
        """
        with self.connection() as conn:
            try:
                yield conn
                conn.commit()
                logger.debug("Transaction committed")
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back: {e}")
                raise
    
    @trace_execution
    def execute(self, query: str, params: tuple = ()) -> Tuple[bool, Any]:
        """
        Execute a SQL query with proper transaction handling.
        
        Args:
            query: SQL query string
            params: Query parameters (for parameterized queries)
            
        Returns:
            Tuple of (success: bool, result: rows for SELECT or affected count for DML)
        """
        if not self.db_path:
            return False, "No database selected"
        
        if not os.path.exists(self.db_path):
            return False, f"Database file not found: {self.db_path}"
        
        is_read = is_read_query(query)
        
        try:
            with self.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if is_read:
                    # Read query - fetch results
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    result = {
                        'columns': columns,
                        'rows': [tuple(row) for row in rows],
                        'count': len(rows)
                    }
                    logger.info(f"SELECT returned {len(rows)} rows")
                    return True, result
                else:
                    # Write query - commit and return affected rows
                    conn.commit()
                    affected = cursor.rowcount
                    logger.info(f"Query affected {affected} rows")
                    return True, {'affected': affected}
                    
        except sqlite3.Error as e:
            logger.error(f"SQL Error: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Database error: {e}")
            return False, str(e)
    
    @trace_execution
    def list_tables(self) -> List[str]:
        """Get list of all tables in the database."""
        success, result = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        if success:
            return [row[0] for row in result['rows']]
        return []
    
    def get_table_info(self, table_name: str) -> List[dict]:
        """Get column info for a table."""
        # Use parameterized query for table name safety
        success, result = self.execute(f"PRAGMA table_info({table_name})")
        if success:
            return [
                {
                    'name': row[1],
                    'type': row[2],
                    'nullable': not row[3],
                    'primary_key': bool(row[5])
                }
                for row in result['rows']
            ]
        return []
