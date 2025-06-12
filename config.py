import os

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = False  # Disable debug mode to reduce cache generation
    
    # Database Configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '16042006'
    MYSQL_DB = 'menu_db'
    
    # BOM Database Configuration
    MYSQL_BOM_HOST = 'localhost'
    MYSQL_BOM_USER = 'root'
    MYSQL_BOM_PASSWORD = '16042006'
    MYSQL_BOM_DB = 'bom1'
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_THRESHOLD = 1000  # Maximum number of items in cache
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging Configuration
    LOG_LEVEL = 'WARNING'  # Reduce logging to minimize cache impact
    LOG_TO_STDOUT = False
    
    # Performance Configuration
    JSON_SORT_KEYS = False  # Disable JSON sorting for better performance
    JSONIFY_PRETTYPRINT_REGULAR = False  # Disable pretty printing
    
    @staticmethod
    def init_app(app):
        # Create upload folder if it doesn't exist
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        
        # Configure logging
        import logging
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )

class DevelopmentConfig(Config):
    DEBUG = False  # Keep debug off even in development to reduce cache
    LOG_LEVEL = 'INFO'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'ERROR'
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    LOG_LEVEL = 'CRITICAL'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 