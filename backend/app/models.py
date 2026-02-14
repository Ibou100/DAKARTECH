# backend/app/models.py
# Modèles SQLAlchemy pour DAKARTECH

from datetime import datetime
from . import db


class User(db.Model):
    """Modèle utilisateur - clients de la boutique"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    orders = db.relationship('Order', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'phone': self.phone,
            'full_name': self.full_name,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }


class Product(db.Model):
    """Modèle produit - articles en vente"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False)  # Prix en FCFA
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Catégories disponibles
    CATEGORIES = ['telephones', 'ordinateurs', 'accessoires', 'tablettes', 'montres']

    # Relations
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'price_formatted': f"{self.price:,} FCFA".replace(',', ' '),
            'stock': self.stock,
            'category': self.category,
            'image_url': self.image_url or '/frontend/img/placeholder.png',
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class Order(db.Model):
    """Modèle commande - achats des clients"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Montants
    subtotal = db.Column(db.Integer, nullable=False)       # Sous-total en FCFA
    delivery_fees = db.Column(db.Integer, default=0)       # Frais de livraison
    total_amount = db.Column(db.Integer, nullable=False)   # Total à payer

    # Paiement
    payment_type = db.Column(db.String(20), nullable=False)    # 'mobile' ou 'livraison'
    payment_status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    mobile_method = db.Column(db.String(20), nullable=True)    # 'wave' ou 'orange'
    mobile_phone = db.Column(db.String(20), nullable=True)     # Numéro Wave/Orange du client
    transaction_ref = db.Column(db.String(100), nullable=True) # Référence transaction

    # Livraison
    delivery_address = db.Column(db.String(500), nullable=False)
    delivery_phone = db.Column(db.String(20), nullable=False)
    delivery_city = db.Column(db.String(100), nullable=False)
    delivery_notes = db.Column(db.Text, nullable=True)

    # Statuts commande
    status = db.Column(db.String(30), default='en_attente')
    # Statuts: en_attente, paiement_confirme, en_preparation, en_livraison, livree, annulee

    # Informations client (pour commandes sans compte)
    customer_name = db.Column(db.String(100), nullable=True)
    customer_email = db.Column(db.String(120), nullable=True)

    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_date = db.Column(db.DateTime, nullable=True)
    delivery_date = db.Column(db.DateTime, nullable=True)

    # Relations
    items = db.relationship('OrderItem', backref='order', lazy=True)

    # Statuts lisibles
    STATUS_LABELS = {
        'en_attente': 'En attente de paiement',
        'paiement_confirme': 'Paiement confirmé',
        'en_preparation': 'En préparation',
        'en_livraison': 'En cours de livraison',
        'livree': 'Livrée',
        'annulee': 'Annulée'
    }

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subtotal': self.subtotal,
            'subtotal_formatted': f"{self.subtotal:,} FCFA".replace(',', ' '),
            'delivery_fees': self.delivery_fees,
            'delivery_fees_formatted': f"{self.delivery_fees:,} FCFA".replace(',', ' '),
            'total_amount': self.total_amount,
            'total_formatted': f"{self.total_amount:,} FCFA".replace(',', ' '),
            'payment_type': self.payment_type,
            'payment_status': self.payment_status,
            'mobile_method': self.mobile_method,
            'mobile_phone': self.mobile_phone,
            'transaction_ref': self.transaction_ref,
            'delivery_address': self.delivery_address,
            'delivery_phone': self.delivery_phone,
            'delivery_city': self.delivery_city,
            'delivery_notes': self.delivery_notes,
            'status': self.status,
            'status_label': self.STATUS_LABELS.get(self.status, self.status),
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'created_at': self.created_at.isoformat(),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'items': [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    """Modèle article de commande - détail des produits commandés"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Integer, nullable=False)  # Prix au moment de l'achat

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'product_image': self.product.image_url if self.product else None,
            'quantity': self.quantity,
            'price_at_time': self.price_at_time,
            'price_formatted': f"{self.price_at_time:,} FCFA".replace(',', ' '),
            'line_total': self.quantity * self.price_at_time,
            'line_total_formatted': f"{self.quantity * self.price_at_time:,} FCFA".replace(',', ' ')
        }
