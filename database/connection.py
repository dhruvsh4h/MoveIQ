import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
import streamlit as st

class DatabaseManager:
    """Manages PostgreSQL database connections"""
    
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('PGHOST', 'localhost'),
            'database': os.getenv('PGDATABASE', 'postgres'),
            'user': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', ''),
            'port': os.getenv('PGPORT', '5432')
        }
        
        # Alternative: use DATABASE_URL if provided
        self.database_url = os.getenv('DATABASE_URL')
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            if self.database_url:
                conn = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
            else:
                conn = psycopg2.connect(**self.connection_params, cursor_factory=RealDictCursor)
            
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            return False
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if cursor.description:
                        return cursor.fetchall()
                    return None
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            return None
    
    def execute_many(self, query, data):
        """Execute a query with multiple parameter sets"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.executemany(query, data)
                    return True
        except Exception as e:
            st.error(f"Batch execution failed: {str(e)}")
            return False
