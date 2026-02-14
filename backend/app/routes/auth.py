# backend/app/routes/auth.py
# Routes d'authentification DAKARTECH

import hashlib
import os
from flask import Blueprint, request, jsonify
from .. import db
from ..models import User

auth_bp = Blueprint('auth', __name__)


def hash_password(password):
    """Hache un mot de passe avec sel"""
    salt = os.getenv('SECRET_KEY', 'dakartech-salt')
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def validate_phone(phone):
    """Valide un numéro de téléphone sénégalais"""
    # Accepter: +2217XXXXXXXX, 7XXXXXXXX, 77XXXXXXXX
    phone = phone.strip().replace(' ', '').replace('-', '')
    if phone.startswith('+221'):
        return phone
    elif phone.startswith('221'):
        return f'+{phone}'
    elif len(phone) == 9 and phone[0] in ['7', '3']:
        return f'+221{phone}'
    return None


@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    data = request.get_json()

    # Validation
    required = ['email', 'phone', 'full_name']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Le champ {field} est requis'}), 400

    # Vérifier si l'email existe déjà
    existing = User.query.filter_by(email=data['email'].lower()).first()
    if existing:
        return jsonify({'success': False, 'error': 'Cet email est déjà utilisé'}), 409

    # Valider et formater le téléphone
    formatted_phone = validate_phone(data['phone'])
    if not formatted_phone:
        return jsonify({'success': False, 'error': 'Numéro de téléphone invalide'}), 400

    # Créer l'utilisateur
    user = User(
        email=data['email'].lower().strip(),
        phone=formatted_phone,
        full_name=data['full_name'].strip(),
        password_hash=hash_password(data.get('password', '')) if data.get('password') else None
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Compte créé avec succès! Bienvenue sur DAKARTECH!',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Email et mot de passe requis'}), 400

    user = User.query.filter_by(email=data['email'].lower().strip()).first()

    if not user or user.password_hash != hash_password(data['password']):
        return jsonify({'success': False, 'error': 'Email ou mot de passe incorrect'}), 401

    return jsonify({
        'success': True,
        'message': f'Bienvenue {user.full_name}!',
        'user': user.to_dict()
    })


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Récupère le profil d'un utilisateur"""
    user_id = request.args.get('user_id', type=int)

    if not user_id:
        return jsonify({'success': False, 'error': 'user_id requis'}), 400

    user = User.query.get_or_404(user_id)

    # Récupérer les commandes de l'utilisateur
    orders = [o.to_dict() for o in user.orders]

    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'orders': orders,
        'orders_count': len(orders)
    })
