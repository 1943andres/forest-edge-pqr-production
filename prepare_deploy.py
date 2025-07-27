#!/usr/bin/env python3
"""
Script para preparar automáticamente la aplicación para despliegue
"""

import os
import shutil
import subprocess

def create_file(filename, content):
    """Crear archivo con contenido específico"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename} creado")
        return True
    except Exception as e:
        print(f"❌ Error creando {filename}: {e}")
        return False

def backup_existing_files():
    """Hacer backup de archivos existentes"""
    files_to_backup = ['app.py', 'requirements.txt']
    
    for file in files_to_backup:
        if os.path.exists(file):
            backup_name = f"{file}.backup"
            shutil.copy2(file, backup_name)
            print(f"💾 Backup creado: {backup_name}")

def create_procfile():
    """Crear Procfile"""
    content = "web: python run_production.py"
    return create_file('Procfile', content)

def create_runtime():
    """Crear runtime.txt"""
    content = "python-3.11.4"
    return create_file('runtime.txt', content)

def create_config():
    """Crear config.py"""
    content = '''import os
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
config = ProductionConfig if Config.is_production() else DevelopmentConfig'''
    
    return create_file('config.py', content)

def create_env_example():
    """Crear .env.example"""
    content = '''# Configuración de seguridad (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=tu-clave-secreta-super-segura-aqui
JWT_SECRET_KEY=tu-clave-jwt-super-segura-aqui

# API de OpenAI (opcional - para asistente IA)
OPENAI_API_KEY=sk-tu-clave-openai-aqui

# Base de datos (se configura automáticamente en Railway/Render)
DATABASE_URL=postgresql://user:password@host:port/database

# Configuración de Flask
FLASK_DEBUG=False
FLASK_ENV=production

# Límite de archivos (16MB por defecto)
MAX_CONTENT_LENGTH=16777216

# Puerto (se configura automáticamente en la mayoría de plataformas)
PORT=5000'''
    
    return create_file('.env.example', content)

def update_requirements():
    """Actualizar requirements.txt"""
    content = '''Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
Flask-JWT-Extended==4.5.3
Flask-Bcrypt==1.0.1
python-dotenv==1.0.0
openai==1.3.0
Werkzeug==2.3.7
SQLAlchemy==2.0.23
requests==2.31.0
psycopg2-binary==2.9.7
gunicorn==21.2.0'''
    
    return create_file('requirements.txt', content)

def create_run_production():
    """Crear run_production.py"""
    content = '''# run_production.py - Servidor optimizado para producción
import os
import sys
from app import app, db
from models import User
from config import config

def create_demo_users():
    """Crear usuarios de demostración si no existen (solo en primera ejecución)"""
    print("🔧 Verificando usuarios de demostración...")
    
    demo_users = [
        {
            'email': 'admin@alimentos-enriko.com',
            'password': 'admin123',
            'name': 'Administrador Principal',
            'role': 'administrador'
        },
        {
            'email': 'calidad@alimentos-enriko.com',
            'password': 'calidad123',
            'name': 'María González',
            'role': 'calidad'
        },
        {
            'email': 'cliente@kfc.com',
            'password': 'cliente123',
            'name': 'Cliente KFC',
            'role': 'cliente'
        },
        {
            'email': 'registrador@alimentos-enriko.com',
            'password': 'registrador123',
            'name': 'Juan Registrador',
            'role': 'registrador'
        }
    ]
    
    users_created = 0
    for user_data in demo_users:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            new_user = User(
                email=user_data['email'],
                name=user_data['name'],
                role=user_data['role']
            )
            new_user.set_password(user_data['password'])
            db.session.add(new_user)
            users_created += 1
            print(f"✅ Usuario creado: {user_data['email']} ({user_data['role']})")
    
    if users_created > 0:
        try:
            db.session.commit()
            print(f"✅ {users_created} usuarios de demostración creados exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear usuarios: {e}")

def setup_production_environment():
    """Configurar entorno de producción"""
    print("🚀 Configurando entorno de producción...")
    
    # Crear directorio uploads si no existe
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Directorio uploads creado")
    
    # Verificar variables de entorno críticas
    required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("El sistema usará valores por defecto, pero es recomendable configurarlas")
    
    # Verificar OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("⚠️  OPENAI_API_KEY no configurada - Asistente IA limitado")
    else:
        print("✅ OpenAI API Key configurada")
    
    print("✅ Entorno de producción configurado")

if __name__ == '__main__':
    print("🌲 Forest Edge PQR - Iniciando en PRODUCCIÓN")
    print(f"🔧 Puerto: {config.PORT}")
    print(f"🔧 Host: {config.HOST}")
    print(f"🔧 Debug: {config.DEBUG}")
    print(f"🔧 Base de datos: {config.SQLALCHEMY_DATABASE_URI[:50]}...")
    
    # Configurar entorno de producción
    setup_production_environment()
    
    # Inicializar la base de datos
    with app.app_context():
        try:
            # Crear todas las tablas si no existen
            db.create_all()
            print("🗄️  Base de datos inicializada correctamente")
            
            # Crear usuarios de demostración solo si no existen
            create_demo_users()
            
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {e}")
            # En producción no queremos que falle por esto
            pass
    
    print("🚀 Servidor de producción iniciando...")
    print("="*50)
    
    # Ejecutar la aplicación en modo producción
    try:
        app.run(
            debug=config.DEBUG,
            host=config.HOST,
            port=config.PORT,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Error al ejecutar el servidor: {e}")
        sys.exit(1)'''
    
    return create_file('run_production.py', content)

def show_git_commands():
    """Mostrar comandos de Git"""
    print("\n" + "="*60)
    print("📋 COMANDOS PARA SUBIR A GITHUB:")
    print("="*60)
    print("""
1. Inicializar repositorio (si no está inicializado):
   git init

2. Agregar todos los archivos:
   git add .

3. Hacer commit:
   git commit -m "Preparado para despliegue en producción"

4. Crear repositorio en GitHub y conectar:
   git remote add origin https://github.com/TU_USUARIO/TU_REPO.git

5. Subir código:
   git branch -M main
   git push -u origin main

¡Después ve a Railway.app y conecta tu repositorio!
""")

def main():
    """Función principal"""
    print("🚀 PREPARANDO APLICACIÓN PARA DESPLIEGUE")
    print("="*50)
    
    print("\n1. Haciendo backup de archivos existentes...")
    backup_existing_files()
    
    print("\n2. Creando archivos de configuración...")
    
    success = True
    success &= create_procfile()
    success &= create_runtime()
    success &= create_config()
    success &= create_env_example()
    success &= update_requirements()
    success &= create_run_production()
    
    if success:
        print("\n✅ ¡TODOS LOS ARCHIVOS CREADOS EXITOSAMENTE!")
        print("\n📝 ARCHIVOS IMPORTANTES CREADOS:")
        print("   - Procfile (para Railway/Render)")
        print("   - runtime.txt (versión Python)")
        print("   - config.py (configuración de producción)")
        print("   - run_production.py (servidor optimizado)")
        print("   - requirements.txt (dependencias actualizadas)")
        print("   - .env.example (variables de entorno)")
        
        print("\n🔧 SIGUIENTE PASO:")
        print("   Actualiza tu app.py para usar la nueva configuración")
        print("   Agrega al inicio: from config import config")
        print("   Cambia: app.config.from_object(config)")
        
        show_git_commands()
        
        print("\n🌍 DESPUÉS DEL DESPLIEGUE:")
        print("   Tu aplicación estará disponible en todo el mundo")
        print("   Ejemplo: https://tu-app.railway.app")
        
    else:
        print("\n❌ Hubo errores creando algunos archivos")
        print("Revisa los errores arriba y intenta nuevamente")

if __name__ == "__main__":
    main()
    
return create_file('prepare_deploy.py', content)

def show_next_steps():
    """Mostrar pasos siguientes"""
    print("\n" + "="*60)
    print("🚀 PRÓXIMOS PASOS PARA DESPLIEGUE")
    print("="*60)
    print("""
1. 📝 PREPARAR ARCHIVOS:
   python prepare_deploy.py

2. 📤 SUBIR A GITHUB:
   - Crear repositorio en GitHub
   - git add .
   - git commit -m "Listo para producción"
   - git push

3. 🚀 DESPLEGAR EN RAILWAY:
   - Ir a railway.app
   - Conectar repositorio GitHub
   - Agregar PostgreSQL database
   - Configurar variables de entorno

4. 🌍 ACCEDER A TU APP:
   - Tu app estará en: https://tu-app.railway.app
   - Accesible desde cualquier parte del mundo

¿Quieres que te ayude con algún paso específico?
""")

if __name__ == "__main__":
    show_next_steps()