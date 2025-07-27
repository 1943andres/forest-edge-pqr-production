#!/usr/bin/env python3
"""
Script de verificación del Sistema PQR Forest Edge
Verifica que todos los componentes estén funcionando correctamente
"""

import os
import sys
import requests
import time
import subprocess
import json
from threading import Thread

def print_header(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

def print_status(item, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {item}")
    if details:
        print(f"   {details}")

def verificar_archivos():
    """Verificar que todos los archivos necesarios existan"""
    print_header("VERIFICACIÓN DE ARCHIVOS")
    
    archivos_requeridos = {
        'app.py': 'Aplicación Flask principal',
        'models.py': 'Modelos de base de datos',
        'routes.py': 'Rutas y API endpoints',
        'run.py': 'Script de inicio',
        'index.html': 'Interfaz web',
        'requirements.txt': 'Dependencias Python',
        '.env': 'Variables de entorno'
    }
    
    todos_presentes = True
    for archivo, descripcion in archivos_requeridos.items():
        existe = os.path.exists(archivo)
        print_status(f"{archivo} - {descripcion}", existe)
        if not existe:
            todos_presentes = False
    
    # Verificar directorio uploads
    uploads_existe = os.path.exists('uploads')
    print_status("uploads/ - Directorio de archivos", uploads_existe)
    
    return todos_presentes and uploads_existe

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    print_header("VERIFICACIÓN DE DEPENDENCIAS")
    
    dependencias = [
        ('flask', 'Flask web framework'),
        ('flask_sqlalchemy', 'SQLAlchemy ORM'),
        ('flask_cors', 'CORS support'),
        ('flask_jwt_extended', 'JWT authentication'),
        ('flask_bcrypt', 'Password hashing'),
        ('openai', 'OpenAI API client'),
        ('python-dotenv', 'Environment variables')
    ]
    
    todas_instaladas = True
    for dep, descripcion in dependencias:
        try:
            __import__(dep)
            print_status(f"{dep} - {descripcion}", True)
        except ImportError:
            print_status(f"{dep} - {descripcion}", False, "No instalado")
            todas_instaladas = False
    
    return todas_instaladas

def verificar_configuracion():
    """Verificar configuración del archivo .env"""
    print_header("VERIFICACIÓN DE CONFIGURACIÓN")
    
    if not os.path.exists('.env'):
        print_status("Archivo .env", False, "No existe")
        return False
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    variables_requeridas = [
        ('SECRET_KEY', 'Clave secreta de Flask'),
        ('JWT_SECRET_KEY', 'Clave secreta JWT'),
        ('DATABASE_URL', 'URL de base de datos'),
        ('OPENAI_API_KEY', 'Clave API de OpenAI')
    ]
    
    config_valida = True
    for var, descripcion in variables_requeridas:
        valor = os.getenv(var)
        if valor:
            # Ocultar claves sensibles
            if 'KEY' in var and len(valor) > 10:
                valor_mostrar = valor[:10] + "..."
            else:
                valor_mostrar = valor
            print_status(f"{var} - {descripcion}", True, f"Configurado: {valor_mostrar}")
        else:
            print_status(f"{var} - {descripcion}", False, "No configurado")
            config_valida = False
    
    return config_valida

def iniciar_servidor_temporal():
    """Iniciar servidor Flask en proceso separado para testing"""
    try:
        # Usar Python del entorno virtual si existe
        if os.path.exists('venv'):
            if os.name == 'nt':
                python_cmd = 'venv\\Scripts\\python.exe'
            else:
                python_cmd = 'venv/bin/python'
        else:
            python_cmd = sys.executable
        
        proceso = subprocess.Popen(
            [python_cmd, 'run.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar un poco para que el servidor inicie
        time.sleep(5)
        
        return proceso
    except Exception as e:
        print(f"Error iniciando servidor: {e}")
        return None

def verificar_servidor():
    """Verificar que el servidor Flask responda correctamente"""
    print_header("VERIFICACIÓN DEL SERVIDOR")
    
    print("🔄 Iniciando servidor temporal...")
    proceso_servidor = iniciar_servidor_temporal()
    
    if not proceso_servidor:
        print_status("Inicio del servidor", False, "No se pudo iniciar")
        return False
    
    try:
        # Verificar que el servidor responda
        time.sleep(2)  # Esperar un poco más
        
        try:
            response = requests.get('http://localhost:5000', timeout=10)
            servidor_ok = response.status_code == 200
            print_status("Servidor HTTP", servidor_ok, f"Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print_status("Servidor HTTP", False, f"Error: {e}")
            servidor_ok = False
        
        # Verificar endpoint de login
        try:
            login_data = {
                'email': 'admin@alimentos-enriko.com',
                'password': 'admin123'
            }
            response = requests.post(
                'http://localhost:5000/api/login',
                json=login_data,
                timeout=10
            )
            login_ok = response.status_code == 200
            print_status("API de login", login_ok, f"Status: {response.status_code}")
            
            if login_ok:
                # Verificar que recibimos un token
                data = response.json()
                token_ok = 'access_token' in data
                print_status("Generación de JWT", token_ok)
        except requests.exceptions.RequestException as e:
            print_status("API de login", False, f"Error: {e}")
            login_ok = False
        
    finally:
        # Terminar el servidor temporal
        print("🔄 Deteniendo servidor temporal...")
        proceso_servidor.terminate()
        proceso_servidor.wait()
    
    return servidor_ok

def verificar_base_datos():
    """Verificar que la base de datos se pueda crear y usar"""
    print_header("VERIFICACIÓN DE BASE DE DATOS")
    
    try:
        # Importar modelos para verificar estructura
        sys.path.insert(0, os.getcwd())
        from models import db, User
        from app import create_app
        
        # Crear app temporal
        app = create_app()
        
        with app.app_context():
            # Intentar crear tablas
            db.create_all()
            print_status("Creación de tablas", True)
            
            # Verificar que se puede consultar
            user_count = User.query.count()
            print_status("Consulta de usuarios", True, f"{user_count} usuarios encontrados")
            
            return True
            
    except Exception as e:
        print_status("Base de datos", False, f"Error: {e}")
        return False

def verificar_openai():
    """Verificar conectividad con OpenAI"""
    print_header("VERIFICACIÓN DE OPENAI")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key.startswith('tu_clave'):
        print_status("OpenAI API Key", False, "No configurada o placeholder")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Hacer una consulta simple
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hola"}],
            max_tokens=10
        )
        
        print_status("Conexión OpenAI", True, "API responde correctamente")
        return True
        
    except Exception as e:
        print_status("Conexión OpenAI", False, f"Error: {e}")
        return False

def generar_reporte():
    """Generar reporte final de verificación"""
    print_header("EJECUTANDO VERIFICACIÓN COMPLETA")
    
    resultados = {
        'archivos': verificar_archivos(),
        'dependencias': verificar_dependencias(),
        'configuracion': verificar_configuracion(),
        'base_datos': verificar_base_datos(),
        'openai': verificar_openai(),
        'servidor': verificar_servidor()
    }
    
    print_header("REPORTE FINAL")
    
    total_checks = len(resultados)
    exitosos = sum(resultados.values())
    
    for componente, estado in resultados.items():
        print_status(componente.replace('_', ' ').title(), estado)
    
    print(f"\n📊 RESUMEN: {exitosos}/{total_checks} verificaciones exitosas")
    
    if exitosos == total_checks:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ Puedes ejecutar: python run.py")
    elif exitosos >= total_checks - 1:
        print("⚠️  Sistema mayormente funcional con problemas menores")
        print("💡 Revisa los errores mostrados arriba")
    else:
        print("❌ Sistema con problemas significativos")
        print("🔧 Revisa la configuración y dependencias")
    
    return exitosos == total_checks

def main():
    print("""
🌲 FOREST EDGE PQR - VERIFICACIÓN DEL SISTEMA
============================================
Este script verifica que todos los componentes estén funcionando
""")
    
    try:
        sistema_ok = generar_reporte()
        
        print_header("RECOMENDACIONES")
        
        if sistema_ok:
            print("✅ El sistema está listo para usar")
            print("🚀 Ejecuta: python run.py")
            print("🌐 Abre: http://localhost:5000")
        else:
            print("🔧 Acciones recomendadas:")
            print("1. pip install -r requirements.txt")
            print("2. Verificar archivo .env")
            print("3. Configurar OPENAI_API_KEY")
            print("4. Ejecutar: python setup.py")
        
    except Exception as e:
        print(f"❌ Error durante verificación: {e}")
        print("💡 Intenta ejecutar: python setup.py")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()