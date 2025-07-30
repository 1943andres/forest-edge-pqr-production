# crm/__init__.py - MÓDULO CRM INTEGRADO

"""
Módulo CRM integrado con el sistema PQR Forest Edge
Proporciona funcionalidades completas de gestión de clientes,
productos, ventas y actividades comerciales.
"""

# Importar todos los modelos CRM desde models.py principal
# ya que ahora están integrados en un solo archivo
try:
    from models import (
        Customer, CustomerContact, CustomerActivity,
        Product, ProductCategory, 
        Sale, SaleItem
    )
    
    CRM_MODELS_AVAILABLE = True
    
except ImportError as e:
    print(f"⚠️ Error importando modelos CRM: {e}")
    CRM_MODELS_AVAILABLE = False
    
    # Definir clases vacías como fallback
    class Customer: pass
    class CustomerContact: pass
    class CustomerActivity: pass
    class Product: pass
    class ProductCategory: pass
    class Sale: pass
    class SaleItem: pass

# Exportar todos los modelos
__all__ = [
    'Customer', 'CustomerContact', 'CustomerActivity',
    'Product', 'ProductCategory',
    'Sale', 'SaleItem',
    'CRM_MODELS_AVAILABLE'
]

# Información del módulo
__version__ = '1.0.0'
__author__ = 'Forest Edge Development Team'
__description__ = 'Módulo CRM integrado para gestión completa de clientes y ventas'

# Configuración del módulo CRM
CRM_CONFIG = {
    'version': __version__,
    'integrated_with_pqr': True,
    'supports_postgresql': True,
    'supports_railway': True,
    'ai_assistant_enabled': True,
    'features': [
        'customer_management',
        'product_catalog',
        'sales_tracking',
        'activity_logging',
        'pqr_integration',
        'dashboard_metrics',
        'api_endpoints'
    ]
}

def get_crm_info():
    """Obtener información del módulo CRM"""
    return {
        'module': 'Forest Edge CRM',
        'version': __version__,
        'models_available': CRM_MODELS_AVAILABLE,
        'config': CRM_CONFIG,
        'integration_status': 'active' if CRM_MODELS_AVAILABLE else 'error'
    }

def verify_crm_setup():
    """Verificar que el CRM esté configurado correctamente"""
    issues = []
    
    if not CRM_MODELS_AVAILABLE:
        issues.append("Modelos CRM no disponibles - verificar imports")
    
    # Verificar modelos específicos
    required_models = [Customer, Product, Sale]
    for model in required_models:
        if not hasattr(model, '__tablename__'):
            issues.append(f"Modelo {model.__name__} no es válido")
    
    return {
        'status': 'ok' if not issues else 'error',
        'issues': issues,
        'models_count': len(__all__) - 1  # Excluir CRM_MODELS_AVAILABLE
    }

# Ejecutar verificación al importar
if CRM_MODELS_AVAILABLE:
    print("✅ Módulo CRM cargado correctamente")
    verification = verify_crm_setup()
    if verification['status'] == 'error':
        print(f"⚠️ Problemas en CRM: {verification['issues']}")
else:
    print("❌ Módulo CRM con errores - funcionalidad limitada")