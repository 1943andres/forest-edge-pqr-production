# app.py - Aplicación Flask con configuración de producción
from flask import Flask, render_template_string
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, User
from routes import register_routes
from config import config
import os

def setup_openai():
    """Configurar OpenAI de manera robusta"""
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_key or openai_key.startswith('tu_clave') or openai_key.startswith('sk-tu-'):
        print("⚠️  OPENAI_API_KEY no configurada - IA limitada")
        return None
    
    try:
        # Intentar importar y usar la nueva API de OpenAI
        from openai import OpenAI
        
        client = OpenAI(api_key=openai_key)
        
        # Hacer una prueba rápida en desarrollo
        if not config.is_production():
            test_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            print("✅ OpenAI configurado correctamente (nueva API)")
        else:
            print("✅ OpenAI configurado para producción")
        
        return client
        
    except ImportError:
        print("❌ Error: Versión incorrecta de OpenAI")
        print("🔧 Instala: pip install openai==1.3.0")
        return None
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            print("❌ OpenAI API Key inválida")
        elif "quota" in error_msg.lower():
            print("❌ Sin créditos en OpenAI")
        else:
            print(f"❌ Error OpenAI: {e}")
        return None

def create_app():
    app = Flask(__name__)
    
    # Configuración desde config.py
    app.config.from_object(config)
    
    # Configurar OpenAI
    openai_client = setup_openai()
    app.config['OPENAI_CLIENT'] = openai_client
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar CORS según entorno
    if config.is_production():
        # En producción, configurar CORS más específico si es necesario
        CORS(app)
    else:
        # En desarrollo, permitir todo
        CORS(app)
    
    jwt = JWTManager(app)
    
    # Registrar rutas
    register_routes(app)
    
    # Ruta principal para servir el HTML
    @app.route('/')
    def index():
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            return html_content
        except FileNotFoundError:
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error - Sistema PQR</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; }
                    .error-container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .error-title { color: #e74c3c; font-size: 24px; margin-bottom: 20px; }
                    .error-message { color: #666; line-height: 1.6; }
                    .code-block { background: #f8f8f8; padding: 15px; border-radius: 5px; margin: 15px 0; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1 class="error-title">❌ Error: Archivo index.html no encontrado</h1>
                    <div class="error-message">
                        <p>El archivo <strong>index.html</strong> no se encuentra en el directorio del proyecto.</p>
                        <p><strong>Solución:</strong></p>
                        <ol>
                            <li>Asegúrate de que index.html esté en la raíz del proyecto</li>
                            <li>Verifica que el archivo se haya subido correctamente</li>
                            <li>Reinicia el servidor</li>
                        </ol>
                    </div>
                </div>
            </body>
            </html>
            '''

    @app.route('/test_ia.html')
    def test_ia():
        try:
            return open('test_ia.html', 'r', encoding='utf-8').read()
        except:
            return "<h2>Archivo test_ia.html no encontrado</h2>", 404
    
    @app.route('/health')
    def health_check():
        """Endpoint de salud para monitoreo"""
        try:
            # Verificar conexión a base de datos
            with app.app_context():
                db.session.execute('SELECT 1')
            
            return {
                'status': 'healthy',
                'database': 'connected',
                'openai': 'configured' if app.config.get('OPENAI_CLIENT') else 'not_configured',
                'environment': 'production' if config.is_production() else 'development'
            }, 200
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'environment': 'production' if config.is_production() else 'development'
            }, 500
    
    return app

def create_demo_users_if_needed():
    """Crear usuarios de demostración si no existen"""
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
    
    try:
        db.session.commit()
        if not config.is_production():
            print("✅ Usuarios de demostración verificados")
    except Exception as e:
        db.session.rollback()
        if not config.is_production():
            print(f"⚠️  Error al crear usuarios de demostración: {e}")

# Crear la aplicación
app = create_app()

# Inicializar base de datos en el contexto de la aplicación
with app.app_context():
    try:
        db.create_all()
        create_demo_users_if_needed()
        
        # Crear directorio uploads si no existe
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
            
    except Exception as e:
        if not config.is_production():
            print(f"⚠️  Error en inicialización: {e}")

if __name__ == '__main__':
    # Solo para desarrollo local
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )