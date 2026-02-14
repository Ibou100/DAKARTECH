# backend/app/services/payment.py
# Service de paiement pour DAKARTECH
# Phase 1: Paiement manuel (Wave/Orange Money) et paiement à la livraison

import os


class PaymentService:
    """Service principal de gestion des paiements"""

    # --- Frais de livraison par ville (en FCFA) ---
    DELIVERY_FEES = {
        'dakar': 1500,
        'plateau': 1500,
        'medina': 1500,
        'point_e': 1500,
        'sacre_coeur': 1500,
        'mermoz': 1500,
        'fann': 1500,
        'yoff': 2000,
        'ngor': 2000,
        'ouakam': 2000,
        'almadies': 2000,
        'pikine': 2500,
        'guediawaye': 2500,
        'thiaroye': 2500,
        'rufisque': 3000,
        'bargny': 3500,
        'sebikotane': 4000,
        'thies': 5000,
        'mbour': 6000,
        'saly': 7000,
        'kaolack': 10000,
        'saint_louis': 12000,
        'ziguinchor': 15000,
        'touba': 10000,
        'diourbel': 9000,
        'louga': 10000,
        'tambacounda': 15000,
        'kolda': 18000,
        'kedougou': 20000,
    }

    # Frais par défaut pour les villes non listées
    DEFAULT_FEES = 5000

    # Villes avec livraison gratuite (commandes > seuil)
    FREE_DELIVERY_THRESHOLD = 100000  # 100 000 FCFA

    @classmethod
    def calculate_delivery_fees(cls, city: str, subtotal: int = 0) -> int:
        """
        Calcule les frais de livraison selon la ville.
        Livraison gratuite pour les commandes > 100 000 FCFA dans les villes proches.
        """
        city_key = city.lower().strip().replace(' ', '_').replace('-', '_')
        fees = cls.DELIVERY_FEES.get(city_key, cls.DEFAULT_FEES)

        # Livraison gratuite pour Dakar intra-muros si commande > seuil
        dakar_cities = ['dakar', 'plateau', 'medina', 'point_e', 'sacre_coeur', 'mermoz', 'fann']
        if city_key in dakar_cities and subtotal >= cls.FREE_DELIVERY_THRESHOLD:
            return 0

        return fees

    @classmethod
    def get_all_cities(cls) -> list:
        """Retourne la liste de toutes les villes avec leurs frais"""
        cities = []
        for city, fees in cls.DELIVERY_FEES.items():
            city_name = city.replace('_', ' ').title()
            cities.append({
                'key': city,
                'name': city_name,
                'fees': fees,
                'fees_formatted': f"{fees:,} FCFA".replace(',', ' ')
            })
        return cities

    @classmethod
    def get_payment_instructions(cls, payment_type: str, mobile_method: str,
                                  total_amount: int, order_id: int) -> dict:
        """
        Génère les instructions de paiement selon la méthode choisie.
        Utilisé en phase 1 (paiement manuel).
        """
        if payment_type == 'livraison':
            return cls._get_delivery_payment_instructions(total_amount, order_id)
        elif payment_type == 'mobile':
            if mobile_method == 'wave':
                return cls._get_wave_instructions(total_amount, order_id)
            elif mobile_method == 'orange':
                return cls._get_orange_instructions(total_amount, order_id)

        return {'type': 'unknown', 'message': 'Type de paiement non reconnu'}

    @classmethod
    def _get_wave_instructions(cls, amount: int, order_id: int) -> dict:
        """Instructions pour paiement Wave"""
        wave_phone = os.getenv('MERCHANT_WAVE_PHONE', '+221701234567')
        whatsapp = os.getenv('MERCHANT_WHATSAPP', '+221701234567')
        amount_formatted = f"{amount:,} FCFA".replace(',', ' ')

        return {
            'type': 'wave',
            'title': 'Paiement via Wave',
            'steps': [
                f'Ouvrez l\'application Wave sur votre téléphone',
                f'Appuyez sur "Envoyer de l\'argent"',
                f'Entrez le numéro: {wave_phone}',
                f'Entrez le montant: {amount_formatted}',
                f'Dans la note/message: indiquez "Commande #{order_id}"',
                f'Confirmez l\'envoi et prenez une capture d\'écran',
                f'Envoyez la capture sur WhatsApp: {whatsapp}'
            ],
            'merchant_phone': wave_phone,
            'amount': amount,
            'amount_formatted': amount_formatted,
            'order_id': order_id,
            'whatsapp_link': f"https://wa.me/{whatsapp.replace('+', '')}?text=Bonjour%20DAKARTECH%2C%20je%20viens%20de%20payer%20par%20Wave%20pour%20la%20commande%20%23{order_id}%20-%20Montant%3A%20{amount_formatted}",
            'note': 'Votre commande sera traitée après confirmation du paiement (sous 30 minutes)'
        }

    @classmethod
    def _get_orange_instructions(cls, amount: int, order_id: int) -> dict:
        """Instructions pour paiement Orange Money"""
        orange_phone = os.getenv('MERCHANT_ORANGE_PHONE', '+221771234567')
        whatsapp = os.getenv('MERCHANT_WHATSAPP', '+221701234567')
        amount_formatted = f"{amount:,} FCFA".replace(',', ' ')

        return {
            'type': 'orange',
            'title': 'Paiement via Orange Money',
            'steps': [
                f'Composez le #144# ou ouvrez Orange Money',
                f'Choisissez "Transfert d\'argent"',
                f'Entrez le numéro: {orange_phone}',
                f'Entrez le montant: {amount_formatted}',
                f'Entrez votre code PIN Orange Money',
                f'Notez la référence de la transaction',
                f'Contactez-nous sur WhatsApp: {whatsapp}'
            ],
            'merchant_phone': orange_phone,
            'amount': amount,
            'amount_formatted': amount_formatted,
            'order_id': order_id,
            'whatsapp_link': f"https://wa.me/{whatsapp.replace('+', '')}?text=Bonjour%20DAKARTECH%2C%20j%27ai%20pay%C3%A9%20par%20Orange%20Money%20pour%20la%20commande%20%23{order_id}%20-%20Montant%3A%20{amount_formatted}",
            'note': 'Votre commande sera traitée après confirmation du paiement (sous 30 minutes)'
        }

    @classmethod
    def _get_delivery_payment_instructions(cls, amount: int, order_id: int) -> dict:
        """Instructions pour paiement à la livraison"""
        whatsapp = os.getenv('MERCHANT_WHATSAPP', '+221701234567')
        amount_formatted = f"{amount:,} FCFA".replace(',', ' ')

        return {
            'type': 'livraison',
            'title': 'Paiement à la livraison',
            'steps': [
                f'Votre commande #{order_id} a été enregistrée',
                f'Notre livreur vous contactera pour fixer l\'heure',
                f'Préparez la somme de {amount_formatted} en espèces',
                f'Vous pouvez aussi payer par Wave/Orange Money à la livraison',
                f'Durée: 24-48h selon votre ville'
            ],
            'amount': amount,
            'amount_formatted': amount_formatted,
            'order_id': order_id,
            'whatsapp_link': f"https://wa.me/{whatsapp.replace('+', '')}?text=Bonjour%20DAKARTECH%2C%20je%20voudrais%20suivre%20ma%20commande%20%23{order_id}",
            'note': 'Gardez votre téléphone à portée - notre livreur vous appellera'
        }
