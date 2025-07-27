# routes.py - Código completo con restricciones reforzadas para clientes
from flask import jsonify, request, url_for, send_from_directory, current_app
from models import db, User, PQR, PQRComment, bcrypt
from datetime import date, datetime
from werkzeug.utils import secure_filename
import os
import uuid
import json
from dotenv import load_dotenv
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

# Cargar variables de entorno
load_dotenv() 

# Configuración para subir archivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper functions para JWT
def get_current_user_id():
    """Helper para obtener el user_id actual como entero"""
    identity = get_jwt_identity()
    return int(identity) if identity else None

def get_current_user():
    """Helper para obtener el objeto User actual"""
    user_id = get_current_user_id()
    return User.query.get(user_id) if user_id else None

def require_admin(f):
    """Decorador para endpoints que requieren rol de administrador"""
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user or current_user.role != 'administrador':
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador.'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_non_client(f):
    """Decorador para endpoints que no permiten clientes"""
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user or current_user.role == 'cliente':
            return jsonify({'error': 'Acceso denegado. Los clientes no pueden acceder a esta función.'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def register_routes(app):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    @app.route('/api/register', methods=['POST'])
    def register_user():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'cliente')

        if not email or not password or not name:
            return jsonify({'message': 'Faltan datos requeridos (email, contraseña, nombre).'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'El email ya está registrado.'}), 409

        new_user = User(email=email, name=name, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuario registrado exitosamente.', 'user_id': new_user.id}), 201

    @app.route('/api/login', methods=['POST'])
    def login_user():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos.'}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Credenciales inválidas.'}), 401

        # CORREGIDO: Convertir user.id a string para JWT
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'message': 'Inicio de sesión exitoso.', 
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    @app.route('/api/pqrs', methods=['POST'])
    @jwt_required()
    def create_pqr():
        try:
            current_user_id = get_current_user_id()
            current_user = get_current_user()
            
            if not current_user:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            # Generar ticket ID único
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            ticket_id = f"PQR-{timestamp}-{str(uuid.uuid4())[:6].upper()}"

            # Debug: Mostrar datos recibidos
            print("🔍 Datos del formulario recibidos:")
            for key, value in request.form.items():
                print(f"   {key}: {value}")
            
            print("🔍 Archivos recibidos:")
            for key in request.files:
                file = request.files[key]
                print(f"   {key}: {file.filename if file.filename else 'Sin archivo'}")
            
            # Función para obtener valores de form con defaults
            def get_form_value(key, default=''):
                value = request.form.get(key, default)
                return value.strip() if value else default
            
            # Convertir fechas de manera segura
            def parse_date_safe(date_str):
                if not date_str or date_str.strip() == '':
                    return None
                try:
                    return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
                except Exception as e:
                    print(f"⚠️ Error parseando fecha '{date_str}': {e}")
                    return None

            # Obtener campos básicos
            email_contacto = get_form_value('email-contacto')
            cliente = get_form_value('cliente')
            tipo_pqr = get_form_value('tipo-pqr')
            asunto_detalle = get_form_value('asunto-detalle')
            nombre_producto = get_form_value('nombre-producto')
            lote = get_form_value('lote')
            descripcion = get_form_value('descripcion')
            numero_factura = get_form_value('numero-factura')
            devolucion = get_form_value('devolucion')
            
            # Validar campos obligatorios
            campos_requeridos = {
                'Email de contacto': email_contacto,
                'Cliente': cliente,
                'Tipo de PQR': tipo_pqr,
                'Asunto': asunto_detalle,
                'Nombre del producto': nombre_producto,
                'Número de lote': lote,
                'Descripción': descripcion
            }
            
            campos_faltantes = [campo for campo, valor in campos_requeridos.items() if not valor]
            
            if campos_faltantes:
                error_msg = f'Campos obligatorios faltantes: {", ".join(campos_faltantes)}'
                print(f"❌ {error_msg}")
                return jsonify({'error': error_msg}), 400

            # Procesar fechas
            fecha_vencimiento = parse_date_safe(get_form_value('fecha-vencimiento'))
            fecha_recepcion = parse_date_safe(get_form_value('fecha-recepcion-producto'))
            fecha_apertura = parse_date_safe(get_form_value('fecha-apertura-producto'))
            
            # Procesar cantidad
            cantidad_gramos = None
            cantidad_str = get_form_value('cantidad-gramos')
            if cantidad_str:
                try:
                    cantidad_gramos = int(cantidad_str)
                except ValueError:
                    print(f"⚠️ Error parseando cantidad: {cantidad_str}")
                    cantidad_gramos = 0

            print(f"✅ Campos validados correctamente")
            print(f"✅ Creando PQR con ticket: {ticket_id}")

            # Crear nueva PQR
            new_pqr = PQR(
                ticket_id=ticket_id,
                user_id=current_user_id,
                type=tipo_pqr,
                subject=asunto_detalle,
                description=descripcion,
                product_name=nombre_producto,
                batch_number=lote,
                expiration_date=fecha_vencimiento,
                quantity_grams=cantidad_gramos,
                devolution_type=devolucion,
                client_name=cliente,
                client_email=email_contacto,
                ideal_temperature_range='Temperatura ambiente',
                status='abierto',
                priority='media'
            )
            
            db.session.add(new_pqr)
            db.session.flush()  # Para obtener el ID sin hacer commit completo
            
            print(f"✅ PQR creada en BD con ID: {new_pqr.id}")
            
            # Procesar archivos
            archivos_guardados = []
            archivos_con_error = []
            
            archivos_esperados = [
                'archivo-factura',
                'foto-producto-novedad', 
                'foto-etiqueta-apertura',
                'archivo-temperaturas',
                'formato-recepcion-pv',
                'documentos-adicionales'
            ]
            
            for file_key in archivos_esperados:
                if file_key in request.files:
                    files = request.files.getlist(file_key)
                    for i, file in enumerate(files):
                        if file and file.filename and file.filename.strip() != '':
                            try:
                                # Crear nombre único para el archivo
                                filename = secure_filename(file.filename)
                                timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
                                unique_filename = f"{new_pqr.id}_{file_key}_{timestamp_file}_{i}_{filename}"
                                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                                
                                file.save(file_path)
                                archivos_guardados.append({
                                    'tipo': file_key,
                                    'nombre_original': filename,
                                    'nombre_guardado': unique_filename
                                })
                                print(f"✅ Archivo guardado: {filename} -> {unique_filename}")
                            except Exception as e:
                                archivos_con_error.append({
                                    'tipo': file_key,
                                    'nombre': file.filename,
                                    'error': str(e)
                                })
                                print(f"❌ Error guardando archivo {file.filename}: {e}")
            
            # Crear comentario inicial
            comentario_inicial = f"PQR registrada exitosamente.\n"
            comentario_inicial += f"Tipo: {new_pqr.type}\n"
            comentario_inicial += f"Producto: {new_pqr.product_name}\n"
            comentario_inicial += f"Cliente: {new_pqr.client_name}\n"
            comentario_inicial += f"Archivos adjuntos: {len(archivos_guardados)}"
            
            initial_comment = PQRComment(
                pqr_id=new_pqr.id,
                user_id=current_user_id,
                comment_text=comentario_inicial,
                author_name="Sistema Automatizado",
                is_internal=False
            )
            db.session.add(initial_comment)
            
            # Hacer commit final
            db.session.commit()
            
            print(f"✅ PQR {ticket_id} creada exitosamente")
            print(f"✅ Archivos procesados: {len(archivos_guardados)}")
            
            response_data = {
                'message': 'PQR creada exitosamente',
                'ticket_id': new_pqr.ticket_id,
                'pqr_id': new_pqr.id,
                'archivos_guardados': len(archivos_guardados),
                'detalles_archivos': archivos_guardados
            }
            
            if archivos_con_error:
                response_data['advertencias'] = f"{len(archivos_con_error)} archivos no se pudieron guardar"
                response_data['archivos_con_error'] = archivos_con_error
            
            return jsonify(response_data), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error completo al crear PQR:")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return jsonify({
                'error': 'Error interno del servidor al crear PQR',
                'details': str(e),
                'tipo': 'error_servidor'
            }), 500

    @app.route('/api/pqrs', methods=['GET'])
    @jwt_required()
    def get_pqrs():
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener parámetro de búsqueda si existe
        search_query = request.args.get('search', '').strip()

        # RESTRICCIÓN REFORZADA: Los clientes SOLO ven sus propias PQRs
        if current_user.role == 'cliente':
            query = PQR.query.filter_by(user_id=current_user.id)
            print(f"🔒 Cliente {current_user.email} - Solo ve sus PQRs (user_id={current_user.id})")
        elif current_user.role in ['administrador', 'registrador', 'calidad']:
            # Otros roles pueden ver todas las PQRs
            query = PQR.query
            print(f"👥 Usuario {current_user.email} ({current_user.role}) - Ve todas las PQRs")
        else:
            # Por seguridad, roles no reconocidos solo ven sus propias PQRs
            query = PQR.query.filter_by(user_id=current_user.id)
            print(f"⚠️ Rol desconocido {current_user.role} - Solo ve sus PQRs")

        # Aplicar filtro de búsqueda si existe
        if search_query:
            query = query.filter(
                db.or_(
                    PQR.ticket_id.contains(search_query),
                    PQR.client_name.contains(search_query),
                    PQR.client_email.contains(search_query),
                    PQR.product_name.contains(search_query),
                    PQR.batch_number.contains(search_query),
                    PQR.subject.contains(search_query)
                )
            )

        # Ordenar por fecha de creación descendente
        pqrs = query.order_by(PQR.created_at.desc()).all()
        print(f"📊 Devolviendo {len(pqrs)} PQRs para {current_user.email}")
        return jsonify([pqr.to_dict() for pqr in pqrs]), 200

    @app.route('/api/pqrs/<pqr_id>', methods=['GET'])
    @jwt_required()
    def get_pqr(pqr_id):
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        pqr = PQR.query.filter_by(id=pqr_id).first()

        if not pqr:
            return jsonify({'error': 'PQR no encontrada'}), 404

        # RESTRICCIÓN REFORZADA: Validación de acceso estricta
        if current_user.role == 'cliente' and pqr.user_id != current_user.id:
            print(f"🔒 ACCESO DENEGADO: Cliente {current_user.email} intentó acceder a PQR {pqr_id} de otro usuario")
            return jsonify({"error": "Acceso denegado. Solo puedes ver tus propias PQRs."}), 403

        return jsonify(pqr.to_dict()), 200

    @app.route('/api/pqrs/<pqr_id>', methods=['PUT'])
    @jwt_required()
    def update_pqr(pqr_id):
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        pqr = PQR.query.filter_by(id=pqr_id).first()

        if not pqr:
            return jsonify({'error': 'PQR no encontrada'}), 404

        # RESTRICCIÓN REFORZADA: Solo administradores y agentes asignados pueden editar
        # Los clientes NO pueden editar PQRs una vez creadas
        if current_user.role == 'cliente':
            return jsonify({"error": "Los clientes no pueden editar PQRs una vez creadas. Contacta al departamento de calidad."}), 403
        
        if current_user.role not in ['administrador'] and pqr.assigned_agent_id != current_user.id:
             return jsonify({"error": "Solo administradores o agentes asignados pueden editar PQRs"}), 403

        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'subject' in data:
            pqr.subject = data['subject']
        if 'description' in data:
            pqr.description = data['description']
        if 'status' in data:
            pqr.status = data['status']
        if 'priority' in data:
            pqr.priority = data['priority']
        if 'assigned_agent_id' in data:
            pqr.assigned_agent_id = data['assigned_agent_id']

        db.session.commit()
        return jsonify({'message': 'PQR actualizada exitosamente'}), 200

    @app.route('/api/pqrs/<pqr_id>/comments', methods=['GET'])
    @jwt_required()
    def get_pqr_comments(pqr_id):
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        pqr = PQR.query.filter_by(id=pqr_id).first()

        if not pqr:
            return jsonify({'error': 'PQR no encontrada'}), 404
        
        # RESTRICCIÓN REFORZADA: Validar acceso a comentarios
        if current_user.role == 'cliente' and pqr.user_id != current_user.id:
            return jsonify({"error": "Acceso denegado. Solo puedes ver comentarios de tus propias PQRs."}), 403

        # Obtener comentarios, filtrar internos si es cliente
        comments_query = PQRComment.query.filter_by(pqr_id=pqr_id)
        if current_user.role == 'cliente':
            # Los clientes NO ven comentarios internos
            comments_query = comments_query.filter_by(is_internal=False)
            print(f"🔒 Cliente {current_user.email} - Solo ve comentarios públicos")
        
        comments = comments_query.order_by(PQRComment.created_at.asc()).all()
        return jsonify([comment.to_dict() for comment in comments]), 200

    @app.route('/api/pqrs/<pqr_id>/comments', methods=['POST'])
    @jwt_required()
    def add_comment_to_pqr(pqr_id):
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        pqr = PQR.query.filter_by(id=pqr_id).first()

        if not pqr:
            return jsonify({'error': 'PQR no encontrada'}), 404
        
        # RESTRICCIÓN REFORZADA: Validar acceso para agregar comentarios
        if current_user.role == 'cliente' and pqr.user_id != current_user.id:
            return jsonify({"error": "Acceso denegado. Solo puedes comentar en tus propias PQRs."}), 403

        comment_text = request.form.get('comment_text')
        is_internal = request.form.get('is_internal', 'false').lower() == 'true'

        # RESTRICCIÓN: Los clientes NO pueden crear comentarios internos
        if current_user.role == 'cliente' and is_internal:
            is_internal = False
            print(f"🔒 Cliente {current_user.email} - Comentario convertido a público automáticamente")

        if not comment_text:
            return jsonify({"error": "Se requiere un comentario."}), 400

        new_comment = PQRComment(
            pqr_id=pqr_id,
            user_id=current_user.id,
            comment_text=comment_text or '',
            author_name=current_user.name,
            is_internal=is_internal
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comentario añadido exitosamente', 
            'comment': new_comment.to_dict()
        }), 201

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    @app.route('/api/stats', methods=['GET'])
    @jwt_required()
    def get_stats():
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        try:
            # RESTRICCIÓN REFORZADA: Estadísticas según rol
            if current_user.role == 'cliente':
                # Clientes SOLO ven sus propias estadísticas
                total_pqrs = PQR.query.filter_by(user_id=current_user.id).count()
                open_pqrs = PQR.query.filter_by(user_id=current_user.id, status='abierto').count()
                in_process_pqrs = PQR.query.filter_by(user_id=current_user.id, status='en_proceso').count()
                closed_pqrs = PQR.query.filter_by(user_id=current_user.id, status='cerrado').count()
                
                # PQRs por tipo para este cliente específico
                pqr_types = db.session.query(PQR.type, db.func.count(PQR.id))\
                    .filter_by(user_id=current_user.id)\
                    .group_by(PQR.type).all()
                
                print(f"📊 Cliente {current_user.email} - Estadísticas propias: {total_pqrs} PQRs")
            else:
                # Otros roles ven estadísticas globales
                total_pqrs = PQR.query.count()
                open_pqrs = PQR.query.filter_by(status='abierto').count()
                in_process_pqrs = PQR.query.filter_by(status='en_proceso').count()
                closed_pqrs = PQR.query.filter_by(status='cerrado').count()
                
                # PQRs por tipo globales
                pqr_types = db.session.query(PQR.type, db.func.count(PQR.id))\
                    .group_by(PQR.type).all()
                
                print(f"📊 Usuario {current_user.email} ({current_user.role}) - Estadísticas globales: {total_pqrs} PQRs")

            type_labels = [item[0] for item in pqr_types] if pqr_types else []
            type_data = [item[1] for item in pqr_types] if pqr_types else []

            # PQRs por agente (NO disponible para clientes)
            agent_labels = []
            agent_data = []
            if current_user.role in ['administrador', 'calidad', 'registrador']:
                pqr_agents = db.session.query(User.name, db.func.count(PQR.id))\
                    .join(PQR, User.id == PQR.assigned_agent_id)\
                    .group_by(User.name).all()
                agent_labels = [item[0] for item in pqr_agents] if pqr_agents else []
                agent_data = [item[1] for item in pqr_agents] if pqr_agents else []

            stats = {
                "total_pqrs": total_pqrs,
                "open_pqrs": open_pqrs,
                "in_process_pqrs": in_process_pqrs,
                "closed_pqrs": closed_pqrs,
                "pqr_by_type": {
                    "labels": type_labels,
                    "data": type_data
                },
                "pqr_by_agent": {
                    "labels": agent_labels,
                    "data": agent_data
                },
                # Agregar información específica para clientes
                "user_role": current_user.role,
                "is_client_view": current_user.role == 'cliente'
            }
            return jsonify(stats), 200
            
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500

    @app.route('/api/users', methods=['GET'])
    @jwt_required()
    @require_admin  # SOLO ADMINISTRADORES
    def get_users():
        try:
            users = User.query.all()
            print(f"👥 Administrador consultó lista de usuarios: {len(users)} usuarios")
            return jsonify([user.to_dict() for user in users]), 200
        except Exception as e:
            return jsonify({"error": "Error interno del servidor"}), 500

    @app.route('/api/users', methods=['POST'])
    @jwt_required()
    @require_admin  # SOLO ADMINISTRADORES
    def create_user_by_admin():
        try:
            # Obtener datos - manejar tanto JSON como FormData
            if request.is_json and request.json:
                data = request.json
            elif request.form:
                data = request.form.to_dict()
            else:
                return jsonify({'error': 'No se enviaron datos'}), 400
            
            # Extraer campos
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            role = data.get('role', 'cliente').strip()
            
            # Validar campos obligatorios
            if not name or not email or not password:
                missing = []
                if not name: missing.append('nombre')
                if not email: missing.append('email')
                if not password: missing.append('contraseña')
                return jsonify({'error': f'Faltan campos: {", ".join(missing)}'}), 400

            # Validar email único
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'El email ya está registrado'}), 409

            # Crear usuario
            new_user = User(email=email, name=name, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            print(f"👤 Administrador creó usuario: {email} ({role})")
            
            return jsonify({
                'message': 'Usuario creado exitosamente',
                'user': new_user.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creando usuario: {e}")
            return jsonify({
                'error': 'Error interno del servidor',
                'details': str(e)
            }), 500

    @app.route('/api/agents', methods=['GET'])
    @jwt_required()
    @require_non_client  # CLIENTES NO PUEDEN VER AGENTES
    def get_agents():
        """Endpoint para obtener lista de agentes - NO disponible para clientes"""
        try:
            # Obtener usuarios que pueden ser agentes (no clientes)
            agents = User.query.filter(User.role.in_(['administrador', 'calidad', 'registrador'])).all()
            
            agents_list = []
            for agent in agents:
                agent_info = agent.to_dict()
                # Agregar estadísticas del agente
                assigned_pqrs = PQR.query.filter_by(assigned_agent_id=agent.id).count()
                agent_info['assigned_pqrs_count'] = assigned_pqrs
                agents_list.append(agent_info)
            
            return jsonify(agents_list), 200
        except Exception as e:
            return jsonify({"error": "Error interno del servidor"}), 500

    @app.route('/api/test-openai', methods=['GET'])
    @jwt_required()
    def test_openai():
        """Endpoint para probar la conexión con OpenAI"""
        try:
            openai_client = current_app.config.get('OPENAI_CLIENT')
            if not openai_client:
                return jsonify({
                    "status": "error",
                    "message": "OpenAI no configurado",
                    "details": "No se encontró el cliente OpenAI en la configuración"
                }), 500

            # Hacer una consulta simple
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Responde solo 'OK' si me escuchas"}
                ],
                max_tokens=5,
                temperature=0
            )
            
            reply = response.choices[0].message.content.strip()
            
            return jsonify({
                "status": "success",
                "message": "OpenAI conectado correctamente",
                "response": reply
            }), 200
            
        except Exception as e:
            error_msg = str(e)
            
            # Determinar tipo de error
            if "api_key" in error_msg.lower():
                error_type = "invalid_key"
                user_message = "API Key inválida o no configurada"
            elif "quota" in error_msg.lower():
                error_type = "quota_exceeded"
                user_message = "Sin créditos en OpenAI"
            elif "rate_limit" in error_msg.lower():
                error_type = "rate_limit"
                user_message = "Límite de velocidad excedido"
            else:
                error_type = "unknown"
                user_message = "Error desconocido"
            
            return jsonify({
                "status": "error",
                "error_type": error_type,
                "message": user_message,
                "details": error_msg
            }), 500

    @app.route('/api/ai-chat', methods=['POST'])
    @jwt_required()
    def ai_chat():
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "Mensaje vacío"}), 400

        # Verificar si OpenAI está configurado
        openai_client = current_app.config.get('OPENAI_CLIENT')
        if not openai_client:
            return jsonify({
                "reply": "❌ El asistente de IA no está configurado.\n\n🔧 Para activarlo:\n1. Configura OPENAI_API_KEY en .env\n2. Reinicia el servidor\n3. Verifica con: python diagnostico_ia.py"
            }), 200

        try:
            # Obtener información del usuario actual para contexto
            current_user = get_current_user()
            if not current_user:
                return jsonify({"error": "Usuario no encontrado"}), 404
            
            # CONTEXTO ESPECÍFICO SEGÚN ROL
            if current_user.role == 'cliente':
                # Para clientes: solo información de sus propias PQRs
                recent_pqrs = PQR.query.filter_by(user_id=current_user.id).order_by(PQR.created_at.desc()).limit(3).all()
                role_context = "Eres un asistente para CLIENTES. Solo puedes ayudar con información relacionada a las PQRs del cliente actual. No proporciones información sobre otros clientes o funciones administrativas."
            else:
                # Para personal interno: información más amplia
                recent_pqrs = PQR.query.order_by(PQR.created_at.desc()).limit(5).all()
                role_context = f"Eres un asistente para personal interno ({current_user.role}). Puedes proporcionar información sobre gestión de PQRs, procesos internos y funciones administrativas según el rol del usuario."
            
            # Crear contexto con información relevante
            pqr_context = ""
            if recent_pqrs:
                pqr_context = f"\n\nPQRs recientes {'del cliente' if current_user.role == 'cliente' else 'en el sistema'}:\n"
                for pqr in recent_pqrs:
                    pqr_context += f"- {pqr.ticket_id}: {pqr.type} de {pqr.client_name} sobre {pqr.product_name} (Estado: {pqr.status})\n"
            
            # Contexto específico para el asistente de PQR
            system_context = f"""
            {role_context}
            
            Usuario actual: {current_user.name} ({current_user.role})
            Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            
            INFORMACIÓN DEL SISTEMA:
            - Alimentos Enriko es una empresa de alimentos que gestiona PQRs (Peticiones, Quejas, Reclamos, Sugerencias)
            - Los clientes incluyen: KFC, Pizzamania, Cubano Corral, Invertinos, etc.
            - El sistema maneja trazabilidad completa de productos alimentarios
            
            ROLES Y PERMISOS:
            - Clientes: Solo ven sus propias PQRs, no pueden gestionar usuarios o ver agentes
            - Administradores: Acceso completo a todas las funciones
            - Calidad/Registradores: Pueden ver todas las PQRs y gestionar asignaciones
            
            RESTRICCIONES IMPORTANTES:
            - Si el usuario es cliente, NUNCA menciones información de otros clientes
            - Solo proporciona información que el usuario tiene permiso de ver
            - Para clientes, enfócate en sus propias PQRs y procesos de registro
            
            {pqr_context}
            """

            # Detectar tipo de consulta para dar respuestas más específicas
            message_lower = user_message.lower()
            
            # Respuestas específicas para clientes
            if current_user.role == 'cliente':
                if any(word in message_lower for word in ['usuario', 'agente', 'administr', 'otros', 'ver todo']):
                    quick_response = f"🔒 Como cliente, solo tienes acceso a tus propias PQRs y funciones de registro.\n\nPuedo ayudarte con:\n• 📝 Cómo registrar nuevas PQRs\n• 🔍 Seguimiento de tus PQRs\n• 📎 Documentos requeridos\n• 📊 Estado de tus solicitudes\n\n¿En qué más puedo ayudarte con tus PQRs?"
                    return jsonify({"reply": quick_response}), 200
            
            # Respuestas rápidas para consultas comunes
            if any(word in message_lower for word in ['hola', 'buenas', 'ayuda', 'hi', 'hello']):
                if current_user.role == 'cliente':
                    quick_response = f"¡Hola {current_user.name}! 👋 Soy tu asistente para el sistema PQR.\n\n🔧 Como cliente, puedo ayudarte con:\n\n• 📝 Registro de nuevas PQRs\n• 🔍 Seguimiento de tus PQRs\n• 📎 Documentación requerida\n• 📊 Estado de tus solicitudes\n• 📋 Información sobre procesos\n\n¿En qué puedo ayudarte específicamente?"
                else:
                    quick_response = f"¡Hola {current_user.name}! 👋 Soy tu asistente para el sistema PQR.\n\n🔧 Como {current_user.role}, puedo ayudarte con:\n\n• 📝 Gestión completa de PQRs\n• 👥 Administración de usuarios\n• 📊 Estadísticas y reportes\n• 🔍 Procesos de calidad\n• 📋 Trazabilidad de productos\n\n¿En qué puedo ayudarte?"
                return jsonify({"reply": quick_response}), 200

            # Llamada a OpenAI usando la nueva API
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=800,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Post-procesar la respuesta para mejorarla
            if len(reply) > 600:
                # Si la respuesta es muy larga, resumirla un poco
                reply = reply[:600] + "...\n\n❓ ¿Te gustaría que profundice en algún punto específico?"
            
            return jsonify({"reply": reply}), 200
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error inesperado con OpenAI: {e}")
            
            # Respuestas específicas según el tipo de error
            if "api_key" in error_msg.lower():
                error_response = "🔑 **Error de API Key**\n\nLa clave de OpenAI no es válida.\n\n🔧 **Solución:**\n1. Ve a https://platform.openai.com/api-keys\n2. Genera una nueva clave\n3. Actualiza OPENAI_API_KEY en .env\n4. Reinicia el servidor"
            elif "quota" in error_msg.lower():
                error_response = "💳 **Sin créditos en OpenAI**\n\nTu cuenta no tiene créditos disponibles.\n\n🔧 **Solución:**\n1. Ve a https://platform.openai.com/account/billing\n2. Agrega créditos a tu cuenta\n3. Reinicia el servidor"
            elif "rate_limit" in error_msg.lower():
                error_response = "⏱️ **Límite de velocidad**\n\nDemasiadas consultas muy rápido.\n\n🔧 **Solución:**\nEspera unos segundos e intenta nuevamente."
            else:
                error_response = "❌ **Error del asistente IA**\n\nHubo un problema técnico.\n\n🔧 **Solución:**\n1. Ejecuta: python diagnostico_ia.py\n2. Revisa la configuración de OpenAI\n3. Contacta al administrador si persiste"
            
            return jsonify({"reply": error_response}), 200

    @app.route('/api/ai-suggestions', methods=['POST'])
    @jwt_required()
    def ai_suggestions():
        """Endpoint para obtener sugerencias contextuales de IA según rol"""
        try:
            current_user = get_current_user()
            if not current_user:
                return jsonify({"suggestions": []}), 200
                
            data = request.get_json()
            context = data.get('context', '')  # Por ejemplo: 'nueva-pqr', 'seguimiento', etc.
            
            suggestions = []
            
            # SUGERENCIAS ESPECÍFICAS SEGÚN ROL
            if current_user.role == 'cliente':
                if context == 'nueva-pqr':
                    suggestions = [
                        "¿Qué documentos debo adjuntar para una PQR de calidad?",
                        "¿Cuánto tiempo toma procesar mi reclamo?",
                        "¿Cómo completar el registro fotográfico del producto?",
                        "¿Qué información de temperatura necesito proporcionar?"
                    ]
                elif context == 'seguimiento':
                    suggestions = [
                        "¿Cómo consultar el estado de mi PQR?",
                        "¿Qué significa que mi PQR esté 'en proceso'?",
                        "¿Cuándo recibiré respuesta a mi solicitud?",
                        "¿Puedo agregar información adicional a mi PQR?"
                    ]
                elif context == 'dashboard':
                    suggestions = [
                        "¿Qué significan las estadísticas de mis PQRs?",
                        "¿Cómo interpretar el estado de mis solicitudes?",
                        "¿Cuántas PQRs puedo tener abiertas?",
                        "¿Cómo hacer seguimiento eficiente a mis casos?"
                    ]
                else:
                    suggestions = [
                        "¿Cómo registrar una nueva PQR?",
                        "¿Qué documentos necesito para reportar un problema?",
                        "¿Cómo consultar mis PQRs anteriores?",
                        "¿Cuáles son los tiempos de respuesta?"
                    ]
            else:
                # Sugerencias para personal interno
                if context == 'nueva-pqr':
                    suggestions = [
                        "¿Cómo asignar automáticamente una PQR a un agente?",
                        "¿Cuáles son los criterios de priorización?",
                        "¿Qué validaciones se hacen en los documentos?",
                        "¿Cómo notificar automáticamente al cliente?"
                    ]
                elif context == 'seguimiento':
                    suggestions = [
                        "¿Cómo filtrar PQRs por estado o prioridad?",
                        "¿Qué PQRs requieren atención urgente?",
                        "¿Cómo reasignar una PQR a otro agente?",
                        "¿Cómo generar reportes de seguimiento?"
                    ]
                elif context == 'dashboard' and current_user.role in ['administrador', 'calidad']:
                    suggestions = [
                        "¿Cuáles son las PQRs prioritarias hoy?",
                        "¿Cómo identificar tendencias en los reclamos?",
                        "¿Qué métricas son más importantes para calidad?",
                        "¿Cómo generar un reporte mensual?"
                    ]
                else:
                    suggestions = [
                        "¿Cómo optimizar el flujo de trabajo de PQRs?",
                        "¿Cuáles son las mejores prácticas para agentes?",
                        "¿Cómo configurar notificaciones automáticas?",
                        "¿Qué reportes están disponibles?"
                    ]
            
            return jsonify({"suggestions": suggestions}), 200
            
        except Exception as e:
            print(f"Error obteniendo sugerencias: {e}")
            return jsonify({"suggestions": []}), 200