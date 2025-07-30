# crm/crm_routes.py - Rutas del CRM
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User

def register_crm_routes(app):
    """Registrar todas las rutas del CRM"""
    
    @app.route('/api/crm/dashboard')
    @jwt_required()
    def crm_dashboard():
        """Dashboard principal del CRM"""
        try:
            current_user_id = int(get_jwt_identity())
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            dashboard_data = {
                'total_customers': 45,
                'active_opportunities': 12,
                'total_sales_ytd': 850000000,
                'pipeline_value': 120000000,
                'user_role': current_user.role,
                'user_name': current_user.name,
                'monthly_target': 75000000,
                'monthly_progress': 68
            }
            
            return jsonify(dashboard_data), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/crm/test')
    @jwt_required()
    def crm_test():
        """Endpoint de prueba para verificar que CRM funciona"""
        return jsonify({
            'message': 'CRM funcionando correctamente',
            'status': 'success',
            'modules': ['clientes', 'ventas', 'productos'],
            'version': '1.0.0',
            'integrations': ['PQR', 'AI Assistant']
        }), 200
    
    @app.route('/api/crm/customers')
    @jwt_required()
    def get_customers():
        """Obtener lista de clientes (simulada)"""
        try:
            customers_demo = [
                {
                    'id': 1,
                    'customer_code': 'KFC001',
                    'company_name': 'KFC Colombia S.A.S.',
                    'contact_name': 'Juan Pérez',
                    'email': 'juan.perez@kfc.com.co',
                    'phone': '+57 300 123 4567',
                    'city': 'Bogotá',
                    'segment': 'Premium',
                    'status': 'Activo',
                    'total_sales_ytd': 45000000,
                    'satisfaction_score': 8.5
                },
                {
                    'id': 2,
                    'customer_code': 'PIZ001',
                    'company_name': 'Pizzamania S.A.',
                    'contact_name': 'Ana López',
                    'email': 'ana.lopez@pizzamania.com',
                    'phone': '+57 301 987 6543',
                    'city': 'Cali',
                    'segment': 'Standard',
                    'status': 'Activo',
                    'total_sales_ytd': 28000000,
                    'satisfaction_score': 9.1
                }
            ]
            
            return jsonify(customers_demo), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500