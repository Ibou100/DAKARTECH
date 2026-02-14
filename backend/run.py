# backend/run.py
# Point d'entrée de l'application DAKARTECH

import os
from app import create_app, db
from app.models import Product, User

app = create_app()


def seed_database():
    """Insère des données de démonstration dans la base de données"""
    with app.app_context():
        # Vérifier si des produits existent déjà
        if Product.query.count() > 0:
            print("✅ Base de données déjà peuplée.")
            return

        print("🌱 Insertion des données de démonstration...")

        # --- Produits exemple ---
        produits = [
            Product(
                name="Samsung Galaxy A54 5G",
                description="Smartphone Samsung Galaxy A54 5G - Écran 6.4\" Super AMOLED, 128GB stockage, 8GB RAM, Triple caméra 50MP, Batterie 5000mAh. Garantie 1 an.",
                price=285000,
                stock=15,
                category="telephones",
                image_url="https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400"
            ),
            Product(
                name="iPhone 14 - 128GB",
                description="Apple iPhone 14 128GB - Écran 6.1\" Super Retina, Puce A15 Bionic, Double caméra 12MP, iOS 16. Déverrouillé tous opérateurs.",
                price=485000,
                stock=8,
                category="telephones",
                image_url="https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=400"
            ),
            Product(
                name="Tecno Spark 20 Pro",
                description="Tecno Spark 20 Pro - Écran 6.78\" FHD+, 256GB, 8GB RAM, Caméra 108MP, Batterie 5000mAh, Android 13. Parfait rapport qualité-prix.",
                price=115000,
                stock=25,
                category="telephones",
                image_url="https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400"
            ),
            Product(
                name="HP Laptop 15 - Core i5",
                description="Ordinateur portable HP 15 pouces - Intel Core i5 12ème génération, 8GB RAM, 512GB SSD, Windows 11, Écran Full HD 15.6\".",
                price=395000,
                stock=10,
                category="ordinateurs",
                image_url="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400"
            ),
            Product(
                name="MacBook Air M2",
                description="Apple MacBook Air 13\" avec puce M2 - 8GB RAM, 256GB SSD, Écran Liquid Retina, Autonomie 18h, Design ultra-fin.",
                price=895000,
                stock=5,
                category="ordinateurs",
                image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"
            ),
            Product(
                name="Lenovo IdeaPad 3 - AMD",
                description="Lenovo IdeaPad 3 - AMD Ryzen 5, 8GB RAM, 256GB SSD, Écran 15.6\" FHD, Windows 11 Home. Idéal pour le bureau et les études.",
                price=285000,
                stock=12,
                category="ordinateurs",
                image_url="https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400"
            ),
            Product(
                name="AirPods Pro 2ème génération",
                description="Apple AirPods Pro 2ème gen - Réduction active du bruit, Son Spatial, Résistant à l'eau, Autonomie 6h (30h avec boîtier).",
                price=145000,
                stock=20,
                category="accessoires",
                image_url="https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=400"
            ),
            Product(
                name="Clavier Bluetooth Logitech MX Keys",
                description="Clavier Logitech MX Keys - Bluetooth, Compatible Windows/Mac/Linux, Rétroéclairage intelligent, Recharge USB-C, Multi-appareils.",
                price=95000,
                stock=18,
                category="accessoires",
                image_url="https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400"
            ),
            Product(
                name="Souris Logitech MX Master 3",
                description="Souris sans fil Logitech MX Master 3 - Ergonomique, 7 boutons, Molette MagSpeed, Compatible toutes surfaces, Recharge rapide.",
                price=75000,
                stock=22,
                category="accessoires",
                image_url="https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"
            ),
            Product(
                name="Samsung Galaxy Tab S9",
                description="Samsung Galaxy Tab S9 - Écran 11\" AMOLED, Snapdragon 8 Gen 2, 128GB, S Pen inclus, Wi-Fi 6E, Résistant à l'eau IP68.",
                price=395000,
                stock=7,
                category="tablettes",
                image_url="https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400"
            ),
            Product(
                name="Chargeur USB-C 65W GaN",
                description="Chargeur USB-C 65W GaN - Compatible iPhone, Samsung, MacBook, Recharge rapide, Design compact, 2 ports USB-C + 1 USB-A.",
                price=18500,
                stock=50,
                category="accessoires",
                image_url="https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400"
            ),
            Product(
                name="Disque SSD Externe Samsung T7 1TB",
                description="Disque SSD externe Samsung T7 1TB - USB 3.2, Vitesse 1050 MB/s, Compact et léger, Protection mot de passe, Compatible PC/Mac.",
                price=85000,
                stock=14,
                category="accessoires",
                image_url="https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=400"
            ),
        ]

        for produit in produits:
            db.session.add(produit)

        # --- Utilisateur admin de démonstration ---
        import hashlib
        salt = os.getenv('SECRET_KEY', 'dakartech-salt')
        admin_hash = hashlib.sha256(f"admin2024{salt}".encode()).hexdigest()

        admin = User(
            email="admin@dakartech.sn",
            phone="+221701234567",
            full_name="Administrateur DAKARTECH",
            password_hash=admin_hash,
            is_admin=True
        )
        db.session.add(admin)

        db.session.commit()
        print(f"✅ {len(produits)} produits et 1 admin créés avec succès!")
        print("   Admin: admin@dakartech.sn / admin2024")


if __name__ == '__main__':
    with app.app_context():
        # Création des tables si elles n'existent pas
        db.create_all()
        print("✅ Tables de base de données créées/vérifiées.")

        # Insertion des données de démonstration
        seed_database()

    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', '1') == '1'

    print(f"\n🚀 DAKARTECH API démarrée sur http://{host}:{port}")
    print(f"   Mode debug: {'Activé' if debug else 'Désactivé'}")
    print(f"   Documentation API: http://{host}:{port}/api/health\n")

    app.run(host=host, port=port, debug=debug)
