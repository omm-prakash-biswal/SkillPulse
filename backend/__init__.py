"""Field Atlas Backend Package Initialization."""
try:
    # Ensure PyMySQL is registered as the MySQLdb driver for Django ORM
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
