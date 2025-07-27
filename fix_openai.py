#!/usr/bin/env python3
"""
Script para arreglar la versión de OpenAI y configurar la IA correctamente
"""

import os
import sys
import subprocess

def print_step(step, description):
    print(f"\n{'='*60}")
    print(f"PASO {step}: {description}")
    print('='*60)

def run_command(command, description):
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Éxito")
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        return False

def get_pip_command():
    """Obtener el comando pip correcto"""
    if os.path.exists('venv'):
        if os.name == 'nt':  # Windows
            return 'venv\\Scripts\\pip.exe'
        else:  # Unix/Linux/macOS
            return 'venv/bin/pip'
    else:
        return 'pip'

def main():
    print("""
🤖 REPARADOR DE OPENAI
=====================
Arreglando la versión de OpenAI para que la IA funcione...
""")
    
    print_step(1, "Desinstalando versión antigua de OpenAI")
    pip_cmd = get_pip_command()
    
    if not run_command(f"{pip_cmd} uninstall openai -y", "Desinstalar OpenAI antigua"):
        print("⚠️  No se pudo desinstalar la versión anterior, continuando...")
    
    print_step(2, "Instalando OpenAI versión correcta")
    if not run_command(f"{pip_cmd} install openai==1.3.0", "Instalar OpenAI 1.3.0"):
        print("❌ Error crítico: No se pudo instalar OpenAI")
        return False
    
    print_step(3, "Verificando instalación")
    try:
        # Probar importación
        import openai
        print(f"✅ OpenAI versión: {openai.__version__}")
        
        # Probar nueva API
        from openai import OpenAI
        print("✅ Nueva API OpenAI disponible")
        
        # Probar cliente
        client = OpenAI(api_key="test-key")
        print("✅ Cliente OpenAI se puede crear")
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False
    
    print_step(4, "Probando conectividad con OpenAI")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key.startswith('tu_clave'):
            print("⚠️  API Key no configurada correctamente")
            print("🔧 Configura OPENAI_API_KEY en .env con tu clave real")
            return False
        
        client = OpenAI(api_key=api_key)
        
        # Consulta de prueba
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Responde solo 'OK'"}],
            max_tokens=5
        )
        
        reply = response.choices[0].message.content.strip()
        print(f"✅ OpenAI responde: '{reply}'")
        
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            print("❌ API Key inválida")
            print("🔧 Ve a https://platform.openai.com/api-keys y genera una nueva")
        elif "quota" in error_msg.lower():
            print("❌ Sin créditos en OpenAI")
            print("🔧 Ve a https://platform.openai.com/account/billing")
        else:
            print(f"❌ Error: {error_msg}")
        return False
    
    print(f"""
🎉 ¡OPENAI REPARADO EXITOSAMENTE!

✅ Versión correcta instalada
✅ API funcionando
✅ Conectividad verificada

🚀 SIGUIENTES PASOS:
1. Reinicia el servidor: python run.py
2. Abre: http://localhost:5000
3. Haz login y prueba el botón 🤖
4. La IA debería funcionar perfectamente

""")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ No se pudo reparar OpenAI completamente")
        print("🔧 Revisa las recomendaciones arriba")
    
    input("\nPresiona Enter para continuar...")