#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la conectividad con OpenAI - VERSIÓN CORREGIDA
"""

import os
import sys
from dotenv import load_dotenv

def print_status(item, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {item}")
    if details:
        print(f"   {details}")

def verificar_variables_entorno():
    """Verificar variables de entorno"""
    print("\n🔧 VERIFICANDO VARIABLES DE ENTORNO")
    print("="*50)
    
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if openai_key:
        if openai_key.startswith('sk-'):
            print_status("OPENAI_API_KEY formato", True, f"Comienza con 'sk-': {openai_key[:20]}...")
        else:
            print_status("OPENAI_API_KEY formato", False, "No comienza con 'sk-'")
            return False
            
        if len(openai_key) > 40:
            print_status("OPENAI_API_KEY longitud", True, f"Longitud: {len(openai_key)} caracteres")
        else:
            print_status("OPENAI_API_KEY longitud", False, f"Muy corta: {len(openai_key)} caracteres")
            return False
    else:
        print_status("OPENAI_API_KEY", False, "No configurada")
        return False
    
    return True

def verificar_importaciones():
    """Verificar que se puedan importar las librerías necesarias"""
    print("\n📦 VERIFICANDO IMPORTACIONES")
    print("="*50)
    
    try:
        import openai
        print_status("openai", True, f"Versión: {openai.__version__}")
        
        # Verificar nueva API
        from openai import OpenAI
        print_status("OpenAI class", True, "Nueva API disponible")
        
        return True
    except ImportError as e:
        print_status("openai", False, f"Error: {e}")
        return False

def probar_conexion_openai():
    """Probar conexión real con OpenAI"""
    print("\n🌐 PROBANDO CONEXIÓN CON OPENAI")
    print("="*50)
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print_status("API Key", False, "No configurada")
            return False
        
        # Crear cliente con configuración simple (sin proxies ni otros parámetros)
        client = OpenAI(api_key=api_key)
        print_status("Cliente OpenAI", True, "Cliente creado correctamente")
        
        # Hacer una consulta de prueba
        print("🔄 Realizando consulta de prueba...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": "Hola, ¿puedes responder con 'OK' si me escuchas?"}
            ],
            max_tokens=10,
            temperature=0.1
        )
        
        reply = response.choices[0].message.content.strip()
        print_status("Consulta OpenAI", True, f"Respuesta: '{reply}'")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "invalid" in error_msg.lower():
            print_status("API Key", False, "Clave inválida o expirada")
        elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
            print_status("Cuota OpenAI", False, "Sin créditos disponibles")
        elif "rate" in error_msg.lower():
            print_status("Rate Limit", False, "Límite de velocidad excedido")
        elif "proxies" in error_msg.lower():
            print_status("Configuración", False, "Error en configuración del cliente")
        else:
            print_status("Conexión OpenAI", False, f"Error: {error_msg}")
        
        return False

def verificar_endpoint_flask():
    """Verificar que el endpoint de Flask funcione"""
    print("\n🖥️  VERIFICANDO ENDPOINT FLASK")
    print("="*50)
    
    try:
        import requests
        import time
        
        # Esperar un poco si el servidor está iniciando
        time.sleep(2)
        
        # Probar endpoint de login
        login_data = {
            'email': 'admin@alimentos-enriko.com',
            'password': 'admin123'
        }
        
        response = requests.post(
            'http://localhost:5000/api/login',
            json=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print_status("Servidor Flask", True, "Responde correctamente")
            print_status("JWT Token", True, f"Token obtenido: {token[:20]}...")
            
            # Probar endpoint de IA
            ai_response = requests.post(
                'http://localhost:5000/api/ai-chat',
                json={'message': 'Hola'},
                headers={'Authorization': f'Bearer {token}'},
                timeout=15
            )
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                reply = ai_data.get('reply', '')
                print_status("Endpoint IA", True, f"Respuesta: {reply[:50]}...")
                return True
            else:
                print_status("Endpoint IA", False, f"Status: {ai_response.status_code}")
                print(f"   Respuesta: {ai_response.text[:100]}...")
                return False
        else:
            print_status("Servidor Flask", False, f"Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status("Servidor Flask", False, "No está ejecutándose en puerto 5000")
        print("   💡 Ejecuta: python run.py")
        return False
    except Exception as e:
        print_status("Endpoint IA", False, f"Error: {e}")
        return False

def generar_solucion():
    """Generar recomendaciones de solución"""
    print("\n🔧 RECOMENDACIONES DE SOLUCIÓN")
    print("="*50)
    
    print("Para completar la configuración:")
    print()
    print("1. 🚀 INICIAR SERVIDOR:")
    print("   python run.py")
    print()
    print("2. 🌐 ABRIR NAVEGADOR:")
    print("   http://localhost:5000")
    print()
    print("3. 🔐 HACER LOGIN:")
    print("   Email: admin@alimentos-enriko.com")
    print("   Pass: admin123")
    print()
    print("4. 🤖 PROBAR IA:")
    print("   - Haz clic en el botón 🤖 (esquina inferior derecha)")
    print("   - Escribe 'Hola' y presiona Enter")
    print("   - Debería responder con opciones de ayuda")
    print()
    print("5. 📝 CREAR PQR:")
    print("   - Ve a 'Nueva PQR'")
    print("   - Llena todos los campos obligatorios")
    print("   - Sube los documentos requeridos")

def main():
    print("""
🤖 DIAGNÓSTICO DEL ASISTENTE IA
===============================
Verificando configuración completa...
""")
    
    # 1. Verificar variables de entorno
    env_ok = verificar_variables_entorno()
    
    # 2. Verificar importaciones
    import_ok = verificar_importaciones()
    
    # 3. Probar conexión directa
    if env_ok and import_ok:
        conexion_ok = probar_conexion_openai()
    else:
        conexion_ok = False
    
    # 4. Verificar endpoint (solo si el servidor está corriendo)
    try:
        endpoint_ok = verificar_endpoint_flask()
    except:
        endpoint_ok = False
        print_status("Servidor Flask", False, "No ejecutándose")
    
    # Resultado final
    print("\n📊 RESUMEN DEL DIAGNÓSTICO")
    print("="*50)
    
    total_checks = 4
    passed = sum([env_ok, import_ok, conexion_ok, endpoint_ok])
    
    print(f"✅ Verificaciones exitosas: {passed}/{total_checks}")
    
    if passed == 4:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("🚀 La IA está lista para usar")
    elif passed == 3 and not endpoint_ok:
        print("⚠️  IA configurada correctamente - Solo falta iniciar servidor")
        print("🚀 Ejecuta: python run.py")
    elif conexion_ok:
        print("⚠️  IA funciona pero hay problemas menores")
    elif env_ok and import_ok:
        print("❌ Problema con API Key o créditos de OpenAI")
    else:
        print("❌ Problemas de configuración básica")
    
    # Mostrar recomendaciones
    generar_solucion()

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para salir...")