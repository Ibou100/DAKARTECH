# backend/app/routes/orders.py
# Routes API pour la gestion des commandes DAKARTECH

from datetime import datetime
from flask import Blueprint, request, jsonify
from .. import db
from ..models import Order, OrderItem, Product
from ..services.payment import PaymentService

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """Crée une nouvelle commande avec paiement mobile ou à la livraison"""
    data = request.get_json()

    # --- Validation des champs obligatoires ---
    required = ['items', 'delivery_address', 'delivery_phone', 'delivery_city', 'payment_type']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Le champ {field} est requis'}), 400

    if data['payment_type'] not in ['mobile', 'livraison']:
        return jsonify({'success': False, 'error': 'Type de paiement invalide'}), 400

    if data['payment_type'] == 'mobile':
        if not data.get('mobile_method'):
            return jsonify({'success': False, 'error': 'Méthode mobile requise (wave/orange)'}), 400
        if not data.get('mobile_phone'):
            return jsonify({'success': False, 'error': 'Numéro de téléphone mobile requis'}), 400

    # --- Vérification et calcul des articles ---
    if not data['items'] or len(data['items']) == 0:
        return jsonify({'success': False, 'error': 'Le panier est vide'}), 400

    subtotal = 0
    order_items_data = []

    for item in data['items']:
        product = Product.query.get(item.get('product_id'))
        if not product or not product.is_active:
            return jsonify({'success': False, 'error': f'Produit introuvable: {item.get("product_id")}'}), 400

        quantity = int(item.get('quantity', 1))
        if quantity < 1:
            return jsonify({'success': False, 'error': 'Quantité invalide'}), 400

        if product.stock < quantity:
            return jsonify({
                'success': False,
                'error': f'Stock insuffisant pour {product.name} (disponible: {product.stock})'
            }), 400

        subtotal += product.price * quantity
        order_items_data.append({
            'product': product,
            'quantity': quantity,
            'price': product.price
        })

    # --- Calcul des frais de livraison ---
    delivery_fees = PaymentService.calculate_delivery_fees(data['delivery_city'])
    total_amount = subtotal + delivery_fees

    # --- Création de la commande ---
    order = Order(
        user_id=data.get('user_id'),
        customer_name=data.get('customer_name', ''),
        customer_email=data.get('customer_email', ''),
        subtotal=subtotal,
        delivery_fees=delivery_fees,
        total_amount=total_amount,
        payment_type=data['payment_type'],
        payment_status='pending',
        mobile_method=data.get('mobile_method'),
        mobile_phone=data.get('mobile_phone'),
        delivery_address=data['delivery_address'],
        delivery_phone=data['delivery_phone'],
        delivery_city=data['delivery_city'],
        delivery_notes=data.get('delivery_notes', ''),
        status='en_attente'
    )

    db.session.add(order)
    db.session.flush()  # Obtenir l'ID sans valider

    # --- Création des articles de commande ---
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data['product'].id,
            quantity=item_data['quantity'],
            price_at_time=item_data['price']
        )
        db.session.add(order_item)

        # Déduire du stock
        item_data['product'].stock -= item_data['quantity']

    db.session.commit()

    # --- Préparer les instructions de paiement ---
    payment_instructions = PaymentService.get_payment_instructions(
        payment_type=data['payment_type'],
        mobile_method=data.get('mobile_method'),
        total_amount=total_amount,
        order_id=order.id
    )

    return jsonify({
        'success': True,
        'message': 'Commande créée avec succès!',
        'order': order.to_dict(),
        'payment_instructions': payment_instructions
    }), 201


@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Récupère les détails d'une commande pour le suivi"""
    order = Order.query.get_or_404(order_id)

    return jsonify({
        'success': True,
        'order': order.to_dict()
    })


@orders_bp.route('/orders/<int:order_id>/confirm-payment', methods=['POST'])
def confirm_payment(order_id):
    """Confirme la réception du paiement mobile (admin)"""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()

    if order.payment_type == 'livraison':
        return jsonify({'success': False, 'error': 'Commande avec paiement à la livraison'}), 400

    # Enregistrer la référence de transaction si fournie
    if data.get('transaction_ref'):
        order.transaction_ref = data['transaction_ref']

    order.payment_status = 'confirmed'
    order.payment_date = datetime.utcnow()
    order.status = 'paiement_confirme'

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Paiement confirmé!',
        'order': order.to_dict()
    })


@orders_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Met à jour le statut d'une commande (admin)"""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()

    valid_statuses = ['en_attente', 'paiement_confirme', 'en_preparation', 'en_livraison', 'livree', 'annulee']
    new_status = data.get('status')

    if not new_status or new_status not in valid_statuses:
        return jsonify({
            'success': False,
            'error': f'Statut invalide. Options: {", ".join(valid_statuses)}'
        }), 400

    order.status = new_status

    # Si livrée avec paiement à la livraison, confirmer paiement automatiquement
    if new_status == 'livree' and order.payment_type == 'livraison':
        order.payment_status = 'confirmed'
        order.payment_date = datetime.utcnow()
        order.delivery_date = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Statut mis à jour: {order.STATUS_LABELS.get(new_status, new_status)}',
        'order': order.to_dict()
    })


@orders_bp.route('/admin/orders', methods=['GET'])
def get_all_orders():
    """Récupère toutes les commandes avec filtres (admin)"""
    status = request.args.get('status', '')
    payment_type = request.args.get('payment_type', '')
    payment_status = request.args.get('payment_status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = Order.query

    if status:
        query = query.filter(Order.status == status)
    if payment_type:
        query = query.filter(Order.payment_type == payment_type)
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)

    # Pagination et tri par date décroissante
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Calcul des statistiques
    today = datetime.utcnow().date()
    orders_today = Order.query.filter(
        db.func.date(Order.created_at) == today
    ).count()

    revenue_today = db.session.query(db.func.sum(Order.total_amount)).filter(
        db.func.date(Order.created_at) == today,
        Order.payment_status == 'confirmed'
    ).scalar() or 0

    return jsonify({
        'success': True,
        'orders': [o.to_dict() for o in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'stats': {
            'orders_today': orders_today,
            'revenue_today': revenue_today,
            'revenue_today_formatted': f"{revenue_today:,} FCFA".replace(',', ' ')
        }
    })
