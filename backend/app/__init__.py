# backend/app/__init__.py
# Création et configuration de l'application Flask DAKARTECH

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Initialisation de la base de données (instance partagée)
db = SQLAlchemy()


def create_app():
    """Fabrique d'application Flask"""
    app = Flask(__name__)

    # --- Configuration ---
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-changez-en-prod')
    database_url = os.getenv(
        'DATABASE_URL',
        'sqlite:///dakartech.db'
    )
    # Render et Heroku fournissent souvent 'postgres://' au lieu de 'postgresql://'
    # SQLAlchemy 2+ avec psycopg2 nécessite le dialecte 'postgresql+psycopg2://'
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif database_url.startswith('postgresql://') and not database_url.startswith('postgresql+'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False

    # Configuration CORS (autorise le frontend à communiquer avec l'API)
    CORS(app)

    # --- Initialisation extensions ---
    db.init_app(app)

    # --- Enregistrement des blueprints (routes) ---
    from .routes.products import products_bp
    from .routes.orders import orders_bp
    from .routes.auth import auth_bp

    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # --- Route de santé ---
    @app.route('/api/health')
    def health():
        return {
            'status': 'ok',
            'site': os.getenv('SITE_NAME', 'DAKARTECH'),
            'version': '1.0.0'
        }

    # --- Route pour les informations de paiement ---
    @app.route('/api/config/payment')
    def payment_config():
        return {
            'wave_phone': os.getenv('MERCHANT_WAVE_PHONE', '+221701234567'),
            'orange_phone': os.getenv('MERCHANT_ORANGE_PHONE', '+221771234567'),
            'whatsapp': os.getenv('MERCHANT_WHATSAPP', '+221701234567')
        }

    return app
