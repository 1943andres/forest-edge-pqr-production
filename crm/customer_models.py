# my_pqr_backend/crm/customer_models.py

from database import db # CAMBIO IMPORTANTE: Importamos db desde el nuevo archivo database.py
from datetime import datetime
from sqlalchemy import ForeignKey

class Customer(db.Model):
    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sales_rep_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)

    pqrs = db.relationship('PQR', backref='customer', lazy=True)

    sales_rep = db.relationship('User', backref='customers_as_sales_rep',
                                foreign_keys=[sales_rep_id])

    def __repr__(self):
        return f'<Customer {self.name}>'

class CustomerContact(db.Model):
    __tablename__ = 'customer_contact'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, ForeignKey('customer.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50))

    customer = db.relationship('Customer', backref='contacts', lazy=True)

    def __repr__(self):
        return f'<CustomerContact {self.name} for Customer {self.customer_id}>'

class CustomerActivity(db.Model):
    __tablename__ = 'customer_activity'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, ForeignKey('customer.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    activity_date = db.Column(db.DateTime, default=datetime.utcnow)
    recorded_by_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)

    customer = db.relationship('Customer', backref='activities', lazy=True)
    recorded_by = db.relationship('User', backref='recorded_activities',
                                  foreign_keys=[recorded_by_id])

    def __repr__(self):
        return f'<CustomerActivity {self.activity_type} for Customer {self.customer_id}>'