import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración base
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-2024')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-2024')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Base de datos
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback para desarrollo local
        SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    @staticmethod
    def is_production():
        return os.getenv('PRODUCTION', 'False').lower() == 'true'

# Usar configuración unificada
config = Config