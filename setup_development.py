#!/usr/bin/env python3
# setup_development.py - Configuración para desarrollo local

import os
import sys
import subprocess
from pathlib import Path

class DevelopmentSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / '.env'
        
    def print_step(self, step, message, status="INFO"):
        status_emoji = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ "
        }.get(status, "📋")
        
        print(f"{status_emoji} Paso {step}: {message}")
    
    def check_python_version(self):
        """Verificar versión de Python"""
        self.print_step(1, "Verificando versión de Python...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.print_step(1, f"Python {version.major}.{version.minor}.{version.micro} ✓", "SUCCESS")
            return True
        else:
            self.print_step(1, f"Python {version.major}.{version.minor}.{version.micro} - Se requiere Python 3.8+", "ERROR")
            return False
    
    def create_virtual_environment(self):
        """Crear entorno virtual"""
        self.print_step(2, "Configurando entorno virtual...")
        
        venv_path = self.project_root / 'venv'
        
        if venv_path.exists():
            self.print_step(2, "Entorno virtual ya existe", "INFO")
            return True
        
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], 
                         cwd=self.project_root, check=True)
            self.print_step(2, "Entorno virtual creado", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.print_step(2, f"Error creando entorno virtual: {e}", "ERROR")
            return False
    
    def install_dependencies(self):
        """Instalar dependencias"""
        self.print_step(3, "Instalando dependencias...")
        
        # Determinar el comando pip para el entorno virtual
        if os.name == 'nt':  # Windows
            pip_cmd = str(self.project_root / 'venv' / 'Scripts' / 'pip')
        else:  # Unix/Linux/macOS
            pip_cmd = str(self.project_root / 'venv' / 'bin' / 'pip')
        
        try:
            # Actualizar pip primero
            subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], 
                         cwd=self.project_root, check=True)
            
            # Instalar dependencias
            subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], 
                         cwd=self.project_root, check=True)
            
            self.print_step(3, "Dependencias instaladas correctamente", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.print_step(3, f"Error instalando dependencias: {e}", "ERROR")
            return False
        except FileNotFoundError:
            self.print_step(3, "No se encontró el archivo requirements.txt", "ERROR")
            return False
    
    def create_env_file(self):
        """Crear archivo .env para desarrollo"""
        self.print_step(4, "Configurando archivo .env...")
        
        if self.env_file.exists():
            self.print_step(4, "Archivo .env ya existe", "INFO")
            return True
        
        env_content = """# Forest Edge PQR + CRM - Configuración de Desarrollo
# =====================================================

# Claves secretas para desarrollo (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=forest-edge-dev-secret-key-2024
JWT_SECRET_KEY=forest-edge-dev-jwt-secret-key-2024

# Base de datos para desarrollo local
DATABASE_URL=sqlite:///database.db

# OpenAI para asistente IA (opcional - obtener en https://platform.openai.com/api-keys)
OPENAI_API_KEY=tu_clave_openai_aqui

# Configuración de desarrollo
FLASK_DEBUG=true
FLASK_ENV=development
PRODUCTION=false

# Configuración JWT
JWT_ACCESS_TOKEN_EXPIRES=86400

# Crear datos demo automáticamente
CREATE_DEMO_DATA=true

# Probar OpenAI al iniciar (opcional)
TEST_OPENAI_ON_STARTUP=false

# Configuración de archivos
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# Configuración CORS para desarrollo
CORS_ORIGINS=http://localhost:3000,http://localhost:5000,http://127.0.0.1:5000

# Puerto para desarrollo local
PORT=5000
HOST=127.0.0.1
"""
        
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            self.print_step(4, "Archivo .env creado", "SUCCESS")
            print("   📝 Recuerda configurar OPENAI_API_KEY si quieres IA completa")
            return True
        except Exception as e:
            self.print_step(4, f"Error creando .env: {e}", "ERROR")
            return False
    
    def create_directories(self):
        """Crear directorios necesarios"""
        self.print_step(5, "Creando directorios...")
        
        directories = [
            'uploads',
            'templates', 
            'static',
            'static/css',
            'static/js', 
            'static/images',
            'crm'
        ]
        
        created = 0
        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                created += 1
        
        # Crear .gitkeep en uploads
        gitkeep_path = self.project_root / 'uploads' / '.gitkeep'
        if not gitkeep_path.exists():
            gitkeep_path.touch()
        
        self.print_step(5, f"Directorios verificados ({created} creados)", "SUCCESS")
        return True
    
    def test_imports(self):
        """Probar que los imports funcionen"""
        self.print_step(6, "Verificando imports del proyecto...")
        
        try:
            # Cambiar al directorio del proyecto para imports relativos
            os.chdir(self.project_root)
            
            # Probar imports críticos
            import config
            import database
            import models
            
            # Probar CRM
            try:
                import crm
                crm_status = "✅ CRM disponible"
            except ImportError:
                crm_status = "⚠️ CRM con problemas"
            
            self.print_step(6, f"Imports principales ✓", "SUCCESS")
            print(f"   {crm_status}")
            return True
            
        except ImportError as e:
            self.print_step(6, f"Error en imports: {e}", "ERROR")
            return False
    
    def display_next_steps(self):
        """Mostrar siguientes pasos"""
        print("\n" + "="*60)
        print("🎉 ¡CONFIGURACIÓN DE DESARROLLO COMPLETADA!")
        print("="*60)
        
        # Comando para activar entorno virtual
        if os.name == 'nt':  # Windows
            activate_cmd = ".\\venv\\Scripts\\activate"
        else:  # Unix/Linux/macOS  
            activate_cmd = "source venv/bin/activate"
        
        print(f"""
📋 SIGUIENTES PASOS:

1️⃣ Activar entorno virtual:
   {activate_cmd}

2️⃣ Configurar OpenAI (opcional):
   - Ve a: https://platform.openai.com/api-keys
   - Genera una API key
   - Actualiza OPENAI_API_KEY en .env

3️⃣ Iniciar servidor de desarrollo:
   python app.py
   
   O alternativamente:
   python run.py

4️⃣ Abrir en navegador:
   http://localhost:5000

👥 USUARIOS DE PRUEBA:
   📧 admin@alimentos-enriko.com / admin123
   🔬 calidad@alimentos-enriko.com / calidad123
   👤 cliente@kfc.com / cliente123
   📝 registrador@alimentos-enriko.com / registrador123

🚀 PARA RAILWAY:
   - Seguir la guía de despliegue incluida
   - Configurar PostgreSQL automáticamente
   - Configurar variables de entorno en Railway

💡 TIPS:
   - Los archivos se guardan en uploads/
   - La base de datos SQLite se crea automáticamente
   - El sistema funciona sin OpenAI (IA limitada)
   - CRM está completamente integrado con PQR
        """)
        
        print("="*60)
    
    def run_setup(self):
        """Ejecutar configuración completa"""
        print("🌲 FOREST EDGE PQR + CRM - CONFIGURACIÓN DE DESARROLLO")
        print("="*60)
        
        steps = [
            ("Verificar Python", self.check_python_version),
            ("Entorno Virtual", self.create_virtual_environment),
            ("Dependencias", self.install_dependencies),
            ("Archivo .env", self.create_env_file),
            ("Directorios", self.create_directories),
            ("Imports", self.test_imports)
        ]
        
        results = []
        for step_name, step_func in steps:
            try:
                result = step_func()
                results.append((step_name, result))
                if not result:
                    print(f"\n❌ Setup falló en: {step_name}")
                    return False
            except Exception as e:
                print(f"\n❌ Error inesperado en {step_name}: {e}")
                return False
        
        # Mostrar siguientes pasos si todo salió bien
        if all(result for _, result in results):
            self.display_next_steps()
            return True
        else:
            print("\n❌ Setup incompleto - revisar errores arriba")
            return False

def main():
    """Función principal"""
    setup = DevelopmentSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()