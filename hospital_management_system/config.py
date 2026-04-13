"""
Configuration for Hospital Management System
Database: MySQL
"""
import os


class Config:
    """Application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hospital-secret-key-2025')

    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '12345')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'hospital_db')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

    # Pagination
    ITEMS_PER_PAGE = 10
