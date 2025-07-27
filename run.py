# run.py - Script para iniciar el sistema PQR
import os
import sys
from app import app, db
from models import User
from datetime import datetime

def verificar_entorno():
    """Verificar que el entorno esté configurado correctamente"""
    print("🔧 Verificando configuración del entorno...")
    
    # Verificar archivo .env
    if not os.path.exists('.env'):
        print("⚠️  ADVERTENCIA: No se encontró el archivo .env")
        print("El sistema creará uno básico, pero debes configurar OPENAI_API_KEY")
        crear_env_basico()
    
    # Verificar directorio uploads
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Directorio uploads creado")
    
    # Verificar variables de entorno críticas
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or openai_key.startswith('tu_clave'):
        print("⚠️  OPENAI_API_KEY no configurada - IA limitada")
        print("Para habilitar IA completa, configura OPENAI_API_KEY en .env")
    else:
        print("✅ OpenAI API Key configurada")

def crear_env_basico():
    """Crear archivo .env básico si no existe"""
    env_content = """SECRET_KEY=desarrollo-clave-secreta-pqr-forest-edge-2024
JWT_SECRET_KEY=desarrollo-jwt-clave-secreta-pqr-forest-edge-2024
OPENAI_API_KEY=tu_clave_openai_aqui
DATABASE_URL=sqlite:///database.db
FLASK_DEBUG=True
FLASK_ENV=development
MAX_CONTENT_LENGTH=16777216"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env básico creado")
    except Exception as e:
        print(f"❌ Error creando .env: {e}")

def create_demo_users():
    """Crear usuarios de demostración si no existen"""
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
        else:
            print(f"ℹ️  Usuario ya existe: {user_data['email']}")
    
    if users_created > 0:
        try:
            db.session.commit()
            print(f"✅ {users_created} usuarios de demostración creados exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear usuarios: {e}")
    else:
        print("ℹ️  Todos los usuarios de demostración ya existen")

def mostrar_informacion_sistema():
    """Mostrar información del sistema al iniciar"""
    print("\n" + "="*60)
    print("🌲 FOREST EDGE PQR - SISTEMA INICIADO")
    print("="*60)
    print("🚀 Servidor: http://localhost:5000")
    print("📊 Panel Admin: http://localhost:5000 (login como admin)")
    print("="*60)
    print("")
    print("👥 USUARIOS DE PRUEBA DISPONIBLES:")
    print("📧 Administrador: admin@alimentos-enriko.com / admin123")
    print("🔬 Calidad: calidad@alimentos-enriko.com / calidad123") 
    print("👤 Cliente: cliente@kfc.com / cliente123")
    print("📝 Registrador: registrador@alimentos-enriko.com / registrador123")
    print("")
    print("🔧 CARACTERÍSTICAS DEL SISTEMA:")
    print("✅ Autenticación JWT")
    print("✅ Gestión completa de PQR")
    print("✅ Trazabilidad de productos")
    print("✅ Roles y permisos")
    print("✅ Dashboard con estadísticas")
    print("✅ Asistente IA integrado")
    print("✅ API REST completa")
    print("")
    print("💡 Presiona Ctrl+C para detener el servidor")
    print("="*60)

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_cors
        import flask_jwt_extended
        import openai
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"❌ Falta dependencia: {e}")
        print("Ejecuta: pip install -r requirements.txt")
        return False

if __name__ == '__main__':
    print("🌲 Iniciando Sistema PQR Alimentos Enriko")
    print("Versión: 1.0.0 - Forest Edge")
    print("")
    
    # Verificar dependencias
    if not verificar_dependencias():
        print("❌ No se pueden importar las dependencias necesarias")
        print("Solución: pip install -r requirements.txt")
        sys.exit(1)
    
    # Verificar entorno
    verificar_entorno()
    
    # Inicializar la base de datos y crear usuarios de demostración
    with app.app_context():
        try:
            # Crear todas las tablas si no existen
            db.create_all()
            print("🗄️  Base de datos inicializada correctamente")
            
            # Crear usuarios de demostración
            create_demo_users()
            
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {e}")
            print("Verifica que tienes permisos de escritura en el directorio")
            sys.exit(1)
    
    # Mostrar información del sistema
    mostrar_informacion_sistema()
    
    # Ejecutar la aplicación
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        print("¡Gracias por usar Forest Edge PQR!")
    except Exception as e:
        print(f"❌ Error al ejecutar el servidor: {e}")
        print("Verifica que el puerto 5000 esté disponible")