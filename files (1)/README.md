# 💻 DAKARTECH — Boutique E-commerce Tech à Dakar

> Votre boutique tech de confiance à Dakar, Sénégal 🇸🇳  
> _"Teknoloji bi nekk ci sa loxo"_ — La technologie dans vos mains

## 📋 Description

DAKARTECH est une plateforme e-commerce complète, conçue spécifiquement pour le marché sénégalais. Elle permet la vente de produits technologiques (smartphones, ordinateurs, accessoires) avec paiement via **Wave**, **Orange Money** ou **paiement à la livraison**.

### Fonctionnalités principales

- 🛍️ Catalogue produits avec filtres et recherche
- 🛒 Panier persistant (localStorage)
- 📱 Paiement Wave / Orange Money (instructions manuelles - Phase 1)
- 🚗 Paiement à la livraison
- 📦 Calcul automatique des frais de livraison par ville
- 📊 Dashboard admin complet
- 📞 Intégration WhatsApp pour le suivi

---

## 🛠️ Technologies utilisées

| Couche | Technologies |
|--------|-------------|
| **Backend** | Python 3.10+, Flask, SQLAlchemy, PostgreSQL |
| **Frontend** | HTML5, CSS3, JavaScript Vanilla |
| **Base de données** | PostgreSQL |
| **API** | REST JSON |

---

## 📁 Structure du projet

```
dakartech/
├── backend/
│   ├── app/
│   │   ├── __init__.py         # Création app Flask
│   │   ├── models.py           # Modèles SQLAlchemy
│   │   ├── routes/
│   │   │   ├── products.py     # API produits
│   │   │   ├── orders.py       # API commandes
│   │   │   └── auth.py         # API authentification
│   │   └── services/
│   │       └── payment.py      # Service paiement + frais livraison
│   ├── .env                    # Variables d'environnement
│   ├── requirements.txt        # Dépendances Python
│   └── run.py                  # Point d'entrée + seed données
├── frontend/
│   ├── index.html              # Page d'accueil
│   ├── produits.html           # Catalogue produits
│   ├── panier.html             # Panier
│   ├── commande.html           # Formulaire commande
│   ├── confirmation.html       # Confirmation commande
│   ├── css/
│   │   └── style.css           # Styles CSS complets
│   └── js/
│       ├── main.js             # Utilitaires + gestion panier
│       ├── produits.js         # Page catalogue
│       ├── panier.js           # Page panier
│       └── commande.js         # Page commande
└── admin/
    ├── dashboard.html          # Dashboard admin
    ├── commandes.html          # Gestion commandes
    ├── produits-admin.html     # Gestion produits
    └── css/
        └── admin.css           # Styles admin
```

---

## ⚙️ Installation

### Prérequis

- Python 3.10+
- PostgreSQL 14+
- Navigateur web moderne

### 1. Cloner et configurer

```bash
git clone https://github.com/votre-user/dakartech.git
cd dakartech
```

### 2. Créer la base de données PostgreSQL

```bash
psql -U postgres
CREATE DATABASE DAKARTECH;
\q
```

### 3. Configurer le backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate   # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env .env.local
nano .env  # Modifier DATABASE_URL, téléphones marchands, etc.
```

### 4. Lancer le backend

```bash
python run.py
```

La première exécution crée les tables et insère des données de démonstration (12 produits).

```
✅ Tables de base de données créées/vérifiées.
🌱 Insertion des données de démonstration...
✅ 12 produits et 1 admin créés avec succès!
   Admin: admin@dakartech.sn / admin2024

🚀 DAKARTECH API démarrée sur http://0.0.0.0:5000
```

### 5. Lancer le frontend

Ouvrez directement `frontend/index.html` dans votre navigateur, ou utilisez un serveur local :

```bash
# Option 1: Python
cd frontend && python -m http.server 3000

# Option 2: Node.js
npx serve frontend -p 3000

# Option 3: VS Code Live Server
# Installez l'extension "Live Server" et cliquez "Go Live"
```

---

## ⚙️ Configuration (.env)

```env
# Base de données
DATABASE_URL=postgresql://postgres:motdepasse@localhost:5432/dakartech

# Sécurité
SECRET_KEY=changez-cette-cle-en-production
JWT_SECRET_KEY=changez-aussi-cette-cle

# Identité du site
SITE_NAME=DAKARTECH - Votre boutique tech à Dakar

# Numéros de paiement du marchand
MERCHANT_WAVE_PHONE=+221701234567
MERCHANT_ORANGE_PHONE=+221771234567
MERCHANT_WHATSAPP=+221701234567
```

---

## 🌐 API Endpoints

### Produits
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/products` | Liste avec filtres (category, search, page, min_price, max_price) |
| GET | `/api/products/featured` | 6 produits en vedette |
| GET | `/api/products/<id>` | Détail d'un produit |
| POST | `/api/products` | Créer un produit (admin) |
| PUT | `/api/products/<id>` | Modifier un produit (admin) |
| DELETE | `/api/products/<id>` | Supprimer un produit (admin) |

### Commandes
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/orders` | Créer une commande |
| GET | `/api/orders/<id>` | Détail d'une commande |
| POST | `/api/orders/<id>/confirm-payment` | Confirmer paiement (admin) |
| PUT | `/api/orders/<id>/status` | Changer statut (admin) |
| GET | `/api/admin/orders` | Liste toutes commandes avec filtres |

### Auth
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/register` | Inscription |
| POST | `/api/auth/login` | Connexion |
| GET | `/api/auth/profile` | Profil utilisateur |

### Utilitaires
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health` | Santé de l'API |
| GET | `/api/config/payment` | Numéros de paiement marchand |

---

## 💳 Frais de Livraison

| Zone | Frais |
|------|-------|
| Dakar centre | 1 500 FCFA |
| Yoff, Ngor, Ouakam, Almadies | 2 000 FCFA |
| Pikine, Guédiawaye, Thiaroye | 2 500 FCFA |
| Rufisque | 3 000 FCFA |
| Thiès | 5 000 FCFA |
| Kaolack, Touba | 10 000 FCFA |
| Saint-Louis | 12 000 FCFA |
| Ziguinchor | 15 000 FCFA |
| Livraison gratuite | Dakar centre + commande > 100 000 FCFA |

---

## 🔐 Accès Admin

Accédez au dashboard via `admin/dashboard.html`

**Compte de démonstration:**
- Email: `admin@dakartech.sn`
- Mot de passe: `admin2024`

> ⚠️ **Important:** Changez ces identifiants en production! L'interface admin n'a pas encore d'authentification (Phase 1). Protégez-la via votre serveur web (htpasswd, VPN, etc.)

---

## 📱 Paiement (Phase 1 - Manuel)

La Phase 1 utilise des paiements manuels:

1. **Wave:** Le client envoie l'argent au numéro marchand et envoie une capture WhatsApp
2. **Orange Money:** Le client transfère l'argent et envoie la référence
3. **Livraison:** Le livreur collecte l'argent ou le paiement mobile sur place

**Phase 2 (future):** Intégration API Wave ou Kkiapay pour paiements automatiques

---

## 🚀 Déploiement en Production

### Variables à changer
```env
SECRET_KEY=une-cle-tres-longue-et-aleatoire
JWT_SECRET_KEY=une-autre-cle-longue
DATABASE_URL=postgresql://user:password@host:5432/db_prod
FLASK_DEBUG=0
```

### Recommandations
- Utiliser **gunicorn** comme serveur WSGI
- Mettre en place **Nginx** comme proxy inverse
- Activer **HTTPS** (Let's Encrypt)
- Sauvegardes régulières PostgreSQL

```bash
# Lancer avec gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

---

## 📞 Support

- **WhatsApp:** +221 70 123 45 67
- **Téléphone:** +221 70 123 45 67
- **Email:** contact@dakartech.sn

---

## 📄 Licence

Projet privé — DAKARTECH © 2024 — Tous droits réservés 🇸🇳
