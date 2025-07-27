#!/usr/bin/env python3
"""
Script para probar la creación de usuarios directamente
"""

import requests
import json

def test_crear_usuario():
    print("🧪 PROBANDO CREACIÓN DE USUARIOS")
    print("="*40)
    
    # 1. Hacer login como admin
    print("1. Haciendo login como admin...")
    login_data = {
        'email': 'admin@alimentos-enriko.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/login',
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login exitoso. Token: {token[:20]}...")
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 ¿Está corriendo el servidor en python run.py?")
        return
    
    # 2. Probar creación de usuario
    print("\n2. Creando usuario de prueba...")
    user_data = {
        'name': 'Usuario de Prueba',
        'email': 'prueba@test.com',
        'password': 'test123',
        'role': 'cliente'
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/users',
            json=user_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Usuario creado exitosamente!")
            print(f"   ID: {data['user']['id']}")
            print(f"   Nombre: {data['user']['name']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Rol: {data['user']['role']}")
        else:
            print("❌ Error creando usuario:")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Error desconocido')}")
                if 'details' in error_data:
                    print(f"   Detalles: {error_data['details']}")
            except:
                print(f"   Respuesta: {response.text}")
                
    except Exception as e:
        print(f"❌ Error en petición: {e}")
    
    print(f"\n📋 RESUMEN:")
    print(f"   - Login: ✅")
    print(f"   - Crear usuario: {'✅' if response.status_code == 201 else '❌'}")

if __name__ == "__main__":
    test_crear_usuario()
    input("\nPresiona Enter para salir...")