# my_pqr_backend/crm/sales_models.py

from database import db # CAMBIO IMPORTANTE: Importamos db desde el nuevo archivo database.py
from datetime import datetime
from sqlalchemy import ForeignKey

class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, ForeignKey('customer.id'), nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    # Si deseas que las ventas estén asociadas a un representante de ventas:
    # sales_rep_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)

    customer = db.relationship('Customer', backref='sales', lazy=True)
    # Si añades sales_rep_id, también necesitas la relación aquí:
    # sales_rep = db.relationship('User', backref='sales_recorded', foreign_keys=[sales_rep_id])

    def __repr__(self):
        return f'<Sale {self.id} for Customer {self.customer_id}>'