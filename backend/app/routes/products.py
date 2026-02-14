# backend/app/routes/products.py
# Routes API pour la gestion des produits

from flask import Blueprint, request, jsonify
from .. import db
from ..models import Product

products_bp = Blueprint('products', __name__)


@products_bp.route('/products', methods=['GET'])
def get_products():
    """Récupère tous les produits avec filtres optionnels"""
    # Filtres disponibles
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    # Construction de la requête
    query = Product.query.filter_by(is_active=True)

    if category:
        query = query.filter(Product.category == category)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if search:
        query = query.filter(
            Product.name.ilike(f'%{search}%') |
            Product.description.ilike(f'%{search}%')
        )

    # Pagination
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'products': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@products_bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    """Récupère les 6 produits en vedette pour la page d'accueil"""
    products = Product.query.filter_by(is_active=True)\
        .order_by(Product.created_at.desc())\
        .limit(6).all()

    return jsonify({
        'success': True,
        'products': [p.to_dict() for p in products]
    })


@products_bp.route('/products/categories', methods=['GET'])
def get_categories():
    """Récupère toutes les catégories disponibles"""
    categories = db.session.query(Product.category)\
        .filter_by(is_active=True)\
        .distinct().all()

    return jsonify({
        'success': True,
        'categories': [c[0] for c in categories]
    })


@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Récupère le détail d'un produit"""
    product = Product.query.get_or_404(product_id)

    if not product.is_active:
        return jsonify({'success': False, 'error': 'Produit non disponible'}), 404

    return jsonify({
        'success': True,
        'product': product.to_dict()
    })


@products_bp.route('/products', methods=['POST'])
def create_product():
    """Crée un nouveau produit (admin)"""
    data = request.get_json()

    # Validation des champs obligatoires
    required_fields = ['name', 'price', 'category']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Le champ {field} est requis'}), 400

    if data['category'] not in Product.CATEGORIES:
        return jsonify({
            'success': False,
            'error': f'Catégorie invalide. Options: {", ".join(Product.CATEGORIES)}'
        }), 400

    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=int(data['price']),
        stock=int(data.get('stock', 0)),
        category=data['category'],
        image_url=data.get('image_url', '')
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Produit créé avec succès',
        'product': product.to_dict()
    }), 201


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Modifie un produit existant (admin)"""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    # Mise à jour des champs fournis
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = int(data['price'])
    if 'stock' in data:
        product.stock = int(data['stock'])
    if 'category' in data:
        if data['category'] not in Product.CATEGORIES:
            return jsonify({'success': False, 'error': 'Catégorie invalide'}), 400
        product.category = data['category']
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'is_active' in data:
        product.is_active = bool(data['is_active'])

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Produit mis à jour',
        'product': product.to_dict()
    })


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Désactive un produit (suppression douce, admin)"""
    product = Product.query.get_or_404(product_id)

    # Suppression douce - on désactive plutôt que supprimer
    product.is_active = False
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Produit supprimé avec succès'
    })
