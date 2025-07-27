import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración base
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback-jwt-secret-change-in-production')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    
    # Base de datos
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        # Railway/Render suelen usar postgres://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback para desarrollo local
        SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Flask
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Variables de entorno específicas de producción
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    @staticmethod
    def is_production():
        """Detectar si estamos en producción"""
        return os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RENDER') or os.getenv('HEROKU_APP_NAME')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'

class ProductionConfig(Config):
    DEBUG = False
    # En producción, la DATABASE_URL debe estar configurada
    if not Config.DATABASE_URL:
        raise ValueError("DATABASE_URL debe estar configurada en producción")

# Seleccionar configuración automáticamente
config = ProductionConfig if Config.is_production() else DevelopmentConfig