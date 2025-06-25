from .database import get_db

# This module provides compatibility with your existing code structure
# by providing the database session via the get_db() function

def get_supabase_session():
    """Returns Supabase client to maintain your existing code structure"""
    return get_db()