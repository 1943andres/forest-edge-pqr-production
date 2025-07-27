# models.py - Versión simplificada y funcional
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, date
import uuid

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='cliente')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

class PQR(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Información básica de la PQR
    type = db.Column(db.String(50), nullable=False)  # peticion, queja, reclamo, sugerencia
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Información del producto
    product_name = db.Column(db.String(200), nullable=False)
    batch_number = db.Column(db.String(100), nullable=False)
    expiration_date = db.Column(db.Date, nullable=True)
    quantity_grams = db.Column(db.Integer, nullable=True)
    devolution_type = db.Column(db.String(50), nullable=True)  # parcial, completa, no-aplica
    
    # Información del cliente
    client_name = db.Column(db.String(200), nullable=True)
    client_email = db.Column(db.String(120), nullable=True)
    
    # Temperatura
    ideal_temperature_range = db.Column(db.String(100), nullable=True)
    
    # Gestión y estado
    status = db.Column(db.String(50), default='abierto')  # abierto, en_proceso, cerrado
    priority = db.Column(db.String(20), default='baja')  # baja, media, alta
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    author = db.relationship('User', foreign_keys=[user_id], backref='pqrs_created')
    assigned_agent = db.relationship('User', foreign_keys=[assigned_agent_id], backref='pqrs_assigned')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'author_name': self.author.name if self.author else None,
            'assigned_agent_name': self.assigned_agent.name if self.assigned_agent else None,
            'type': self.type,
            'subject': self.subject,
            'description': self.description,
            'product_name': self.product_name,
            'batch_number': self.batch_number,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'quantity_grams': self.quantity_grams,
            'devolution_type': self.devolution_type,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'ideal_temperature_range': self.ideal_temperature_range,
            'status': self.status,
            'priority': self.priority,
            'assigned_agent_id': self.assigned_agent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PQRComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pqr_id = db.Column(db.String(50), db.ForeignKey('pqr.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100))
    is_internal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    pqr = db.relationship('PQR', backref='comments')
    author = db.relationship('User', backref='comments_made')
    
    def to_dict(self):
        return {
            'id': self.id,
            'pqr_id': self.pqr_id,
            'user_id': self.user_id,
            'author_name': self.author_name or (self.author.name if self.author else None),
            'comment_text': self.comment_text,
            'is_internal': self.is_internal,
            'created_at': self.created_at.isoformat()
        }