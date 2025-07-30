# my_pqr_backend/crm/product_models.py

from database import db # CAMBIO IMPORTANTE: Importamos db desde el nuevo archivo database.py
from datetime import datetime
from sqlalchemy import ForeignKey

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)
    category_id = db.Column(db.Integer, ForeignKey('product_category.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('ProductCategory', backref='products', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<ProductCategory {self.name}>'