#!/usr/bin/env python3
"""
Script de debug detallado para ver exactamente qué error ocurre al crear usuarios
"""

import requests
import json

def debug_crear_usuario():
    print("🔍 DEBUG DETALLADO - CREACIÓN DE USUARIOS")
    print("="*50)
    
    # 1. Login
    print("1. 🔐 Haciendo login...")
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
            user_info = data.get('user', {})
            print(f"✅ Login exitoso")
            print(f"   Token: {token[:30]}...")
            print(f"   Usuario: {user_info.get('name')} ({user_info.get('role')})")
        else:
            print(f"❌ Error en login: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # 2. Probar con datos mínimos
    print(f"\n2. 📝 Probando creación con datos básicos...")
    
    user_data = {
        'name': 'Test User',
        'email': 'test@ejemplo.com',
        'password': 'test123',
        'role': 'cliente'
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"📤 Enviando datos:")
    for key, value in user_data.items():
        if key == 'password':
            print(f"   {key}: [HIDDEN]")
        else:
            print(f"   {key}: {value}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/users',
            json=user_data,
            headers=headers,
            timeout=10
        )
        
        print(f"\n📨 RESPUESTA DEL SERVIDOR:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        # Mostrar el contenido completo de la respuesta
        try:
            response_data = response.json()
            print(f"   JSON Response:")
            print(json.dumps(response_data, indent=4, ensure_ascii=False))
        except:
            print(f"   Raw Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ ¡Usuario creado exitosamente!")
        else:
            print("❌ Error en creación de usuario")
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")
    
    # 3. Probar diferentes variaciones
    print(f"\n3. 🧪 Probando con email diferente...")
    
    user_data2 = {
        'name': 'Otro Test',
        'email': 'otro@test.com',
        'password': 'pass123',
        'role': 'registrador'
    }
    
    try:
        response2 = requests.post(
            'http://localhost:5000/api/users',
            json=user_data2,
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response2.status_code}")
        if response2.status_code != 201:
            try:
                error_data = response2.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw: {response2.text}")
        else:
            print("   ✅ Usuario creado correctamente")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 4. Verificar usuarios existentes
    print(f"\n4. 👥 Verificando usuarios existentes...")
    try:
        response3 = requests.get(
            'http://localhost:5000/api/users',
            headers=headers,
            timeout=10
        )
        
        if response3.status_code == 200:
            users = response3.json()
            print(f"   ✅ {len(users)} usuarios encontrados:")
            for user in users:
                print(f"     - {user.get('name')} ({user.get('email')}) - {user.get('role')}")
        else:
            print(f"   ❌ Error obteniendo usuarios: {response3.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_crear_usuario()
    input("\nPresiona Enter para salir...")