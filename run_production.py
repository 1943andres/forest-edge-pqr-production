# run_production.py - Servidor optimizado para producción
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
        sys.exit(1)