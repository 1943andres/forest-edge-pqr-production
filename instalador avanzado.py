#!/usr/bin/env python3
"""
Instalador Avanzado - Forest Edge PQR
Instalación automática con configuración inteligente para diferentes entornos
"""

import os
import sys
import subprocess
import platform
import socket
import json
import time
from datetime import datetime
import urllib.request
import ssl

class AdvancedInstaller:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.python_version = sys.version_info
        self.errors = []
        self.warnings = []
        self.installed_packages = []
        
    def print_header(self):
        """Mostrar header del instalador"""
        print("="*60)
        print("🌲 FOREST EDGE PQR - INSTALADOR AVANZADO")
        print("="*60)
        print(f"🖥️  Sistema Operativo: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {sys.version}")
        print(f"📁 Directorio: {os.getcwd()}")
        print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

    def check_requirements(self):
        """Verificar requisitos del sistema"""
        print("\n🔍 VERIFICANDO REQUISITOS DEL SISTEMA...")
        
        # Verificar Python
        if self.python_version < (3, 8):
            self.errors.append(f"Python 3.8+ requerido. Actual: {self.python_version.major}.{self.python_version.minor}")
            return False
        print(f"✅ Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        
        # Verificar pip
        try:
            import pip
            print("✅ pip disponible")
        except ImportError:
            self.errors.append("pip no está instalado")
            return False
        
        # Verificar conexión a internet
        if self.check_internet_connection():
            print("✅ Conexión a internet disponible")
        else:
            self.warnings.append("Sin conexión a internet - instalación offline")
        
        # Verificar espacio en disco
        free_space = self.get_free_space_mb()
        if free_space < 500:  # Menos de 500 MB
            self.warnings.append(f"Espacio en disco bajo: {free_space:.0f} MB")
        else:
            print(f"✅ Espacio disponible: {free_space:.0f} MB")
        
        return len(self.errors) == 0

    def check_internet_connection(self):
        """Verificar conexión a internet"""
        try:
            # Crear contexto SSL que ignore certificados
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # Intentar conectar a PyPI
            urllib.request.urlopen('https://pypi.org', timeout=5, context=ctx)
            return True
        except:
            try:
                # Intentar con Google como fallback
                urllib.request.urlopen('https://google.com', timeout=5, context=ctx)
                return True
            except:
                return False

    def get_free_space_mb(self):
        """Obtener espacio libre en MB"""
        try:
            if self.os_type == 'windows':
                import shutil
                total, used, free = shutil.disk_usage('.')
                return free / (1024 * 1024)
            else:
                statvfs = os.statvfs('.')
                return statvfs.f_bavail * statvfs.f_frsize / (1024 * 1024)
        except:
            return 1000  # Asumir suficiente espacio si no se puede verificar

    def get_local_ip(self):
        """Obtener IP local del sistema"""
        try:
            # Conectar a una dirección externa para obtener IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def detect_environment(self):
        """Detectar tipo de entorno"""
        print("\n🔍 DETECTANDO ENTORNO DE INSTALACIÓN...")
        
        env_type = "desarrollo"  # Por defecto
        
        # Detectar si es servidor
        if self.os_type == 'linux':
            # Verificar si hay interfaz gráfica
            if not os.environ.get('DISPLAY'):
                env_type = "servidor"
                print("🖥️  Entorno detectado: Servidor Linux (sin interfaz gráfica)")
            else:
                print("🖥️  Entorno detectado: Linux con interfaz gráfica")
        elif self.os_type == 'windows':
            print("🖥️  Entorno detectado: Windows")
        elif self.os_type == 'darwin':
            print("🖥️  Entorno detectado: macOS")
        
        # Detectar si es contenedor Docker
        if os.path.exists('/.dockerenv'):
            env_type = "docker"
            print("🐳 Entorno Docker detectado")
        
        # Detectar si es entorno cloud
        cloud_indicators = [
            '/var/lib/cloud',  # Cloud-init
            '/sys/class/dmi/id/product_name'  # DMI info
        ]
        
        for indicator in cloud_indicators:
            if os.path.exists(indicator):
                env_type = "cloud"
                print("☁️  Entorno cloud detectado")
                break
        
        return env_type

    def setup_virtual_environment(self):
        """Configurar entorno virtual"""
        print("\n📦 CONFIGURANDO ENTORNO VIRTUAL...")
        
        venv_path = 'venv'
        
        if os.path.exists(venv_path):
            print("ℹ️  Entorno virtual ya existe")
            return True
        
        try:
            # Crear entorno virtual
            subprocess.run([sys.executable, '-m', 'venv', venv_path], 
                         check=True, capture_output=True)
            print("✅ Entorno virtual creado")
            return True
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Error creando entorno virtual: {e}")
            return False

    def get_package_manager_commands(self):
        """Obtener comandos del gestor de paquetes según SO"""
        if self.os_type == 'windows':
            return {
                'pip': 'venv\\Scripts\\pip.exe',
                'python': 'venv\\Scripts\\python.exe',
                'activate': 'venv\\Scripts\\activate.bat'
            }
        else:
            return {
                'pip': 'venv/bin/pip',
                'python': 'venv/bin/python',
                'activate': 'source venv/bin/activate'
            }

    def install_dependencies(self):
        """Instalar dependencias de Python"""
        print("\n📚 INSTALANDO DEPENDENCIAS...")
        
        commands = self.get_package_manager_commands()
        
        # Actualizar pip
        try:
            subprocess.run([commands['pip'], 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            print("✅ pip actualizado")
        except subprocess.CalledProcessError:
            self.warnings.append("No se pudo actualizar pip")
        
        # Instalar dependencias desde requirements.txt
        if os.path.exists('requirements.txt'):
            try:
                result = subprocess.run([commands['pip'], 'install', '-r', 'requirements.txt'], 
                                      check=True, capture_output=True, text=True)
                print("✅ Dependencias instaladas desde requirements.txt")
                
                # Parsear paquetes instalados
                for line in result.stdout.split('\n'):
                    if 'Successfully installed' in line:
                        packages = line.replace('Successfully installed', '').strip().split()
                        self.installed_packages.extend(packages)
                
            except subprocess.CalledProcessError as e:
                self.errors.append(f"Error instalando dependencias: {e}")
                return False
        else:
            # Instalar dependencias manualmente
            required_packages = [
                'Flask==2.3.3',
                'Flask-SQLAlchemy==3.0.5',
                'Flask-CORS==4.0.0',
                'Flask-JWT-Extended==4.5.3',
                'Flask-Bcrypt==1.0.1',
                'python-dotenv==1.0.0',
                'openai==1.3.0',
                'Werkzeug==2.3.7',
                'SQLAlchemy==2.0.23'
            ]
            
            for package in required_packages:
                try:
                    subprocess.run([commands['pip'], 'install', package], 
                                 check=True, capture_output=True)
                    print(f"✅ {package}")
                    self.installed_packages.append(package)
                except subprocess.CalledProcessError:
                    self.errors.append(f"Error instalando {package}")
        
        return len(self.errors) == 0

    def setup_directories(self):
        """Crear directorios necesarios"""
        print("\n📁 CONFIGURANDO DIRECTORIOS...")
        
        directories = ['uploads', 'respaldos', 'logs']
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✅ Directorio {directory} creado")
            else:
                print(f"ℹ️  Directorio {directory} ya existe")

    def configure_environment(self):
        """Configurar archivo de entorno"""
        print("\n⚙️  CONFIGURANDO ENTORNO...")
        
        if os.path.exists('.env'):
            print("ℹ️  Archivo .env ya existe")
            
            # Verificar configuración existente
            with open('.env', 'r') as f:
                env_content = f.read()
            
            if 'tu_clave_openai_aqui' in env_content:
                self.warnings.append("OpenAI API Key no configurada en .env")
            
            return True
        
        # Generar configuración automática
        local_ip = self.get_local_ip()
        
        env_template = f"""# Forest Edge PQR - Configuración de Entorno
# Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Claves de seguridad (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=forest-edge-{datetime.now().strftime('%Y%m%d')}-secret-key-{hash(local_ip) % 10000}
JWT_SECRET_KEY=forest-edge-{datetime.now().strftime('%Y%m%d')}-jwt-key-{hash(local_ip + 'jwt') % 10000}

# OpenAI Configuration (Opcional)
OPENAI_API_KEY=tu_clave_openai_aqui

# Base de datos
DATABASE_URL=sqlite:///database.db

# Configuración de desarrollo
FLASK_DEBUG=True
FLASK_ENV=development

# Configuración de red
HOST=0.0.0.0
PORT=5000

# Límites de archivos (16MB)
MAX_CONTENT_LENGTH=16777216

# Información del sistema
INSTALLATION_DATE={datetime.now().isoformat()}
SYSTEM_IP={local_ip}
PYTHON_VERSION={sys.version}
"""
        
        try:
            with open('.env', 'w') as f:
                f.write(env_template)
            print("✅ Archivo .env configurado")
            print(f"🌐 IP local detectada: {local_ip}")
            return True
        except Exception as e:
            self.errors.append(f"Error configurando .env: {e}")
            return False

    def test_installation(self):
        """Probar la instalación"""
        print("\n🧪 PROBANDO INSTALACIÓN...")
        
        commands = self.get_package_manager_commands()
        
        # Test 1: Importar módulos principales
        test_script = """
import sys
sys.path.insert(0, '.')

try:
    from app import app
    from models import User, PQR, db
    print("✅ Módulos principales importados correctamente")
except Exception as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

try:
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada")
except Exception as e:
    print(f"❌ Error con base de datos: {e}")
    sys.exit(1)

print("✅ Pruebas básicas completadas")
"""
        
        try:
            with open('test_installation.py', 'w') as f:
                f.write(test_script)
            
            result = subprocess.run([commands['python'], 'test_installation.py'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Pruebas de instalación exitosas")
                os.remove('test_installation.py')
                return True
            else:
                print(f"❌ Error en pruebas: {result.stderr}")
                self.errors.append("Falló la prueba de instalación")
                return False
                
        except subprocess.TimeoutExpired:
            self.errors.append("Timeout en pruebas de instalación")
            return False
        except Exception as e:
            self.errors.append(f"Error ejecutando pruebas: {e}")
            return False

    def create_startup_scripts(self):
        """Crear scripts de inicio"""
        print("\n📜 CREANDO SCRIPTS DE INICIO...")
        
        commands = self.get_package_manager_commands()
        
        # Script para Windows
        if self.os_type == 'windows':
            bat_script = f"""@echo off
echo Iniciando Forest Edge PQR...
cd /d "{os.getcwd()}"
call {commands['activate']}
echo Servidor iniciándose en http://localhost:5000
echo Presiona Ctrl+C para detener
{commands['python']} run.py
pause
"""
            with open('iniciar_forest_edge.bat', 'w') as f:
                f.write(bat_script)
            print("✅ Script de inicio Windows creado: iniciar_forest_edge.bat")
        
        # Script para Unix/Linux/macOS
        else:
            sh_script = f"""#!/bin/bash
echo "Iniciando Forest Edge PQR..."
cd "{os.getcwd()}"
{commands['activate']}
echo "Servidor iniciándose en http://localhost:5000"
echo "Presiona Ctrl+C para detener"
{commands['python']} run.py
"""
            with open('iniciar_forest_edge.sh', 'w') as f:
                f.write(sh_script)
            
            # Dar permisos de ejecución
            os.chmod('iniciar_forest_edge.sh', 0o755)
            print("✅ Script de inicio Unix creado: iniciar_forest_edge.sh")

    def create_service_files(self):
        """Crear archivos de servicio para producción"""
        print("\n🔧 CREANDO ARCHIVOS DE SERVICIO...")
        
        # Archivo de servicio systemd para Linux
        if self.os_type == 'linux':
            service_content = f"""[Unit]
Description=Forest Edge PQR System
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'www-data')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getcwd()}/venv/bin
ExecStart={os.getcwd()}/venv/bin/python run.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
            
            service_dir = 'service_files'
            if not os.path.exists(service_dir):
                os.makedirs(service_dir)
            
            with open(f'{service_dir}/forest-edge-pqr.service', 'w') as f:
                f.write(service_content)
            
            print("✅ Archivo de servicio systemd creado en service_files/")
            print("   Para instalar: sudo cp service_files/forest-edge-pqr.service /etc/systemd/system/")
            print("   Luego: sudo systemctl enable forest-edge-pqr")

    def generate_installation_report(self):
        """Generar reporte de instalación"""
        print("\n📋 GENERANDO REPORTE DE INSTALACIÓN...")
        
        report = {
            "installation_info": {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "os": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine(),
                    "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}"
                },
                "network": {
                    "local_ip": self.get_local_ip(),
                    "internet_connection": self.check_internet_connection()
                }
            },
            "installation_results": {
                "success": len(self.errors) == 0,
                "errors": self.errors,
                "warnings": self.warnings,
                "installed_packages": self.installed_packages
            },
            "next_steps": {
                "manual_configuration": [
                    "Configurar OPENAI_API_KEY en .env si desea funcionalidad IA",
                    "Revisar configuración de red si se requiere acceso remoto",
                    "Configurar respaldos automáticos"
                ],
                "startup_commands": {
                    "windows": "iniciar_forest_edge.bat",
                    "unix": "./iniciar_forest_edge.sh",
                    "manual": f"{self.get_package_manager_commands()['python']} run.py"
                }
            }
        }
        
        with open('installation_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("✅ Reporte guardado en: installation_report.json")
        return report

    def show_final_instructions(self):
        """Mostrar instrucciones finales"""
        local_ip = self.get_local_ip()
        commands = self.get_package_manager_commands()
        
        print("\n" + "="*60)
        print("🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        
        if self.errors:
            print(f"⚠️  Se encontraron {len(self.errors)} errores:")
            for error in self.errors:
                print(f"   ❌ {error}")
        
        if self.warnings:
            print(f"\n⚠️  Advertencias ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   ⚠️  {warning}")
        
        print(f"\n🚀 INSTRUCCIONES DE INICIO:")
        print(f"="*30)
        
        if self.os_type == 'windows':
            print(f"📝 Método 1 (Recomendado): Doble clic en 'iniciar_forest_edge.bat'")
        else:
            print(f"📝 Método 1 (Recomendado): ./iniciar_forest_edge.sh")
        
        print(f"📝 Método 2 (Manual):")
        print(f"   1. {commands['activate']}")
        print(f"   2. {commands['python']} run.py")
        
        print(f"\n🌐 ACCESO AL SISTEMA:")
        print(f"="*25)
        print(f"🖥️  Local: http://localhost:5000")
        print(f"🌐 Red local: http://{local_ip}:5000")
        
        print(f"\n👥 USUARIOS DE PRUEBA:")
        print(f"="*22)
        print(f"📧 Admin: admin@alimentos-enriko.com / admin123")
        print(f"🔬 Calidad: calidad@alimentos-enriko.com / calidad123")
        print(f"👤 Cliente: cliente@kfc.com / cliente123")
        print(f"📝 Registrador: registrador@alimentos-enriko.com / registrador123")
        
        print(f"\n🔧 CONFIGURACIÓN ADICIONAL:")
        print(f"="*30)
        print(f"• Editar .env para configurar OpenAI API Key")
        print(f"• Configurar firewall para acceso remoto si es necesario")
        print(f"• Ejecutar respaldos regulares con: python sistema_respaldo.py")
        
        print(f"\n📚 ARCHIVOS ÚTILES:")
        print(f"="*20)
        print(f"📄 installation_report.json - Reporte de instalación")
        print(f"🔧 verificador_sistema.py - Verificar estado del sistema")
        print(f"💾 sistema_respaldo.py - Gestión de respaldos")
        print(f"📖 Manual de usuario por roles disponible")
        
        print("="*60)

    def run_installation(self):
        """Ejecutar instalación completa"""
        self.print_header()
        
        # Verificar requisitos
        if not self.check_requirements():
            print("\n❌ No se cumplen los requisitos mínimos")
            for error in self.errors:
                print(f"   • {error}")
            return False
        
        # Detectar entorno
        env_type = self.detect_environment()
        
        # Configurar entorno virtual
        if not self.setup_virtual_environment():
            print("\n❌ Error configurando entorno virtual")
            return False
        
        # Instalar dependencias
        if not self.install_dependencies():
            print("\n❌ Error instalando dependencias")
            return False
        
        # Configurar directorios
        self.setup_directories()
        
        # Configurar entorno
        if not self.configure_environment():
            print("\n❌ Error configurando entorno")
            return False
        
        # Probar instalación
        if not self.test_installation():
            print("\n❌ Falló la prueba de instalación")
            return False
        
        # Crear scripts de inicio
        self.create_startup_scripts()
        
        # Crear archivos de servicio
        self.create_service_files()
        
        # Generar reporte
        self.generate_installation_report()
        
        # Mostrar instrucciones finales
        self.show_final_instructions()
        
        return len(self.errors) == 0

def main():
    """Función principal"""
    installer = AdvancedInstaller()
    
    print("🌲 Forest Edge PQR - Instalador Avanzado")
    print("\n¿Desea continuar con la instalación automática?")
    confirm = input("Escriba 'sí' para continuar: ").lower()
    
    if confirm not in ['sí', 'si', 'yes', 'y']:
        print("❌ Instalación cancelada")
        return 1
    
    success = installer.run_installation()
    
    if success:
        print("\n🎉 ¡Instalación completada exitosamente!")
        
        # Preguntar si quiere iniciar el sistema ahora
        start_now = input("\n¿Desea iniciar el sistema ahora? (sí/no): ").lower()
        if start_now in ['sí', 'si', 'yes', 'y']:
            print("\n🚀 Iniciando sistema...")
            commands = installer.get_package_manager_commands()
            try:
                subprocess.run([commands['python'], 'run.py'])
            except KeyboardInterrupt:
                print("\n🛑 Sistema detenido")
        
        return 0
    else:
        print("\n❌ La instalación falló")
        print("📄 Revisa installation_report.json para más detalles")
        return 1

if __name__ == "__main__":
    sys.exit(main())