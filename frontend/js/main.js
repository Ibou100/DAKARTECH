// frontend/js/main.js
// JavaScript global DAKARTECH - Utilitaires et gestion du panier

// === CONFIGURATION ===
const API_BASE = 'https://dakartech-backend.onrender.com/api';
// === UTILITAIRES ===

/**
 * Formate un prix en FCFA
 * @param {number} amount - Montant en FCFA
 * @returns {string} - Ex: "15 000 FCFA"
 */
function formatPrix(amount) {
  if (!amount && amount !== 0) return '—';
  return new Intl.NumberFormat('fr-FR').format(amount) + ' FCFA';
}

/**
 * Effectue une requête API
 * @param {string} endpoint - Chemin de l'API
 * @param {object} options - Options fetch
 */
async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Erreur serveur');
    return data;
  } catch (error) {
    console.error('Erreur API:', error);
    throw error;
  }
}

/**
 * Affiche une notification toast
 * @param {string} message - Message à afficher
 * @param {string} type - 'success', 'error', 'warning'
 */
function showToast(message, type = 'success') {
  const container = document.querySelector('.toast-container') || createToastContainer();
  const toast = document.createElement('div');
  const icons = { success: '✅', error: '❌', warning: '⚠️' };
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || '💬'}</span> ${message}`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3500);
}

function createToastContainer() {
  const div = document.createElement('div');
  div.className = 'toast-container';
  document.body.appendChild(div);
  return div;
}

/**
 * Tronque un texte à N caractères
 */
function truncate(text, max = 80) {
  if (!text) return '';
  return text.length > max ? text.substring(0, max) + '…' : text;
}

// === GESTION DU PANIER ===

const Panier = {
  STORAGE_KEY: 'dakartech_panier',

  /** Récupère le panier depuis localStorage */
  get() {
    try {
      return JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || [];
    } catch { return []; }
  },

  /** Sauvegarde le panier dans localStorage */
  save(items) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(items));
    this.updateUI();
  },

  /** Ajoute un produit au panier */
  ajouter(produit, quantite = 1) {
    const items = this.get();
    const existant = items.find(i => i.id === produit.id);
    if (existant) {
      existant.quantite += quantite;
    } else {
      items.push({
        id: produit.id,
        name: produit.name,
        price: produit.price,
        image_url: produit.image_url,
        category: produit.category,
        quantite
      });
    }
    this.save(items);
    showToast(`${produit.name} ajouté au panier! 🛒`);
    this.ouvrirSidebar();
  },

  /** Supprime un article du panier */
  supprimer(produitId) {
    const items = this.get().filter(i => i.id !== produitId);
    this.save(items);
  },

  /** Modifie la quantité d'un article */
  modifierQuantite(produitId, nouvelleQte) {
    const items = this.get();
    const item = items.find(i => i.id === produitId);
    if (item) {
      if (nouvelleQte <= 0) {
        this.supprimer(produitId);
      } else {
        item.quantite = nouvelleQte;
        this.save(items);
      }
    }
  },

  /** Vide le panier */
  vider() {
    this.save([]);
  },

  /** Calcule le sous-total */
  sousTotal() {
    return this.get().reduce((sum, item) => sum + item.price * item.quantite, 0);
  },

  /** Nombre total d'articles */
  nombreArticles() {
    return this.get().reduce((sum, item) => sum + item.quantite, 0);
  },

  /** Met à jour le compteur dans le header */
  updateUI() {
    const countEl = document.querySelector('.cart-count');
    const total = this.nombreArticles();
    if (countEl) {
      countEl.textContent = total;
      countEl.style.display = total > 0 ? 'flex' : 'none';
    }
    this.renderSidebar();
  },

  /** Ouvre le sidebar panier */
  ouvrirSidebar() {
    const sidebar = document.querySelector('.cart-sidebar');
    const overlay = document.querySelector('.cart-overlay');
    if (sidebar) sidebar.classList.add('open');
    if (overlay) overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  },

  /** Ferme le sidebar panier */
  fermerSidebar() {
    const sidebar = document.querySelector('.cart-sidebar');
    const overlay = document.querySelector('.cart-overlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
    document.body.style.overflow = '';
  },

  /** Affiche les articles dans le sidebar */
  renderSidebar() {
    const itemsContainer = document.querySelector('.cart-items');
    const footerEl = document.querySelector('.cart-footer');
    if (!itemsContainer) return;

    const items = this.get();

    if (items.length === 0) {
      itemsContainer.innerHTML = `
        <div class="cart-empty">
          <div class="icon">🛒</div>
          <p>Votre panier est vide</p>
          <a href="produits.html" class="btn btn-primary btn-sm" style="margin-top:12px">
            Voir les produits
          </a>
        </div>`;
      if (footerEl) footerEl.style.display = 'none';
      return;
    }

    if (footerEl) footerEl.style.display = 'block';

    itemsContainer.innerHTML = items.map(item => `
      <div class="cart-item" data-id="${item.id}">
        <img src="${item.image_url || 'img/placeholder.png'}" alt="${item.name}" 
             onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23e8f5ee%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2260%22 font-size=%2240%22 text-anchor=%22middle%22>📱</text></svg>'">
        <div class="cart-item-info">
          <div class="cart-item-name">${truncate(item.name, 45)}</div>
          <div class="cart-item-price">${formatPrix(item.price)}</div>
          <div class="qty-control">
            <button class="qty-btn" onclick="Panier.modifierQuantite(${item.id}, ${item.quantite - 1})">−</button>
            <span class="qty-value">${item.quantite}</span>
            <button class="qty-btn" onclick="Panier.modifierQuantite(${item.id}, ${item.quantite + 1})">+</button>
          </div>
        </div>
        <button class="remove-btn" onclick="Panier.supprimer(${item.id})" title="Supprimer">🗑️</button>
      </div>
    `).join('');

    // Mettre à jour le total dans le footer
    const totalEl = document.querySelector('.cart-total .amount');
    if (totalEl) totalEl.textContent = formatPrix(this.sousTotal());
  }
};

// === HEADER ET NAVIGATION ===

function initHeader() {
  const hamburger = document.querySelector('.hamburger');
  const nav = document.querySelector('.nav');
  const cartBtn = document.querySelector('.cart-btn');
  const closeCart = document.querySelector('.close-btn');
  const overlay = document.querySelector('.cart-overlay');

  // Menu hamburger
  if (hamburger && nav) {
    hamburger.addEventListener('click', () => nav.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (!hamburger.contains(e.target) && !nav.contains(e.target)) {
        nav.classList.remove('open');
      }
    });
  }

  // Ouvrir/fermer le panier
  if (cartBtn) cartBtn.addEventListener('click', () => Panier.ouvrirSidebar());
  if (closeCart) closeCart.addEventListener('click', () => Panier.fermerSidebar());
  if (overlay) overlay.addEventListener('click', () => Panier.fermerSidebar());

  // Marquer le lien actif
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a').forEach(link => {
    if (link.getAttribute('href') === currentPage) link.classList.add('active');
  });
}

// === GÉNÈRE LE HTML DU HEADER ===

function renderHeader(page = '') {
  const headerEl = document.getElementById('header');
  if (!headerEl) return;

  headerEl.innerHTML = `
    <header class="header">
      <div class="header-inner">
        <a href="index.html" class="logo">
          <div class="logo-icon">💻</div>
          <div class="logo-text">
            <div class="brand">DAKARTECH</div>
            <div class="tagline">Votre boutique tech à Dakar</div>
          </div>
        </a>
        <button class="hamburger" aria-label="Menu">
          <span></span><span></span><span></span>
        </button>
        <nav class="nav">
          <a href="index.html" ${page==='accueil'?'class="active"':''}>Accueil</a>
          <a href="produits.html" ${page==='produits'?'class="active"':''}>Produits</a>
          <a href="#contact" ${page==='contact'?'class="active"':''}>Contact</a>
        </nav>
        <div class="header-actions">
          <button class="cart-btn" aria-label="Panier">
            🛒 <span class="cart-label">Panier</span>
            <span class="cart-count" style="display:none">0</span>
          </button>
        </div>
      </div>
    </header>
    <!-- Sidebar panier -->
    <div class="cart-overlay"></div>
    <aside class="cart-sidebar">
      <div class="cart-header">
        <h3>🛒 Mon Panier</h3>
        <button class="close-btn" aria-label="Fermer">✕</button>
      </div>
      <div class="cart-items"></div>
      <div class="cart-footer" style="display:none">
        <div class="cart-total">
          <span class="label">Sous-total:</span>
          <span class="amount">0 FCFA</span>
        </div>
        <a href="commande.html" class="btn btn-primary btn-full">
          Commander maintenant →
        </a>
        <p style="font-size:0.8rem;color:var(--gray);text-align:center;margin-top:8px">
          Frais de livraison calculés à l'étape suivante
        </p>
      </div>
    </aside>
  `;

  initHeader();
}

// === GÉNÈRE LE HTML DU FOOTER ===

function renderFooter() {
  const footerEl = document.getElementById('footer');
  if (!footerEl) return;

  footerEl.innerHTML = `
    <footer class="footer" id="contact">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <div class="logo-text">
              <div class="brand">💻 DAKARTECH</div>
            </div>
            <p>Votre boutique tech de confiance à Dakar. 
            Téléphones, ordinateurs et accessoires de qualité à prix juste.</p>
            <p style="color:#4ADE80;font-style:italic;margin-top:8px">
              "Teknoloji bi nekk ci sa loxo" 🇸🇳
            </p>
          </div>
          <div class="footer-links">
            <h4>Navigation</h4>
            <a href="index.html">🏠 Accueil</a>
            <a href="produits.html">📱 Tous les produits</a>
            <a href="panier.html">🛒 Mon panier</a>
          </div>
          <div class="footer-links">
            <h4>Catégories</h4>
            <a href="produits.html?cat=telephones">📱 Téléphones</a>
            <a href="produits.html?cat=ordinateurs">💻 Ordinateurs</a>
            <a href="produits.html?cat=accessoires">🎧 Accessoires</a>
            <a href="produits.html?cat=tablettes">📱 Tablettes</a>
          </div>
          <div class="footer-links">
            <h4>Contact & Paiement</h4>
            <div class="footer-contact">
              <span class="icon">📞</span>
              <a href="tel:+221701234567">+221 70 123 45 67</a>
            </div>
            <div class="footer-contact">
              <span class="icon">💬</span>
              <a href="https://wa.me/221701234567" target="_blank">WhatsApp</a>
            </div>
            <div class="footer-contact">
              <span class="icon">📍</span>
              <span>Dakar, Sénégal</span>
            </div>
            <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">
              <span style="background:#00B4D8;color:#fff;padding:4px 10px;border-radius:50px;font-size:0.75rem;font-weight:700">Wave</span>
              <span style="background:#FF6B00;color:#fff;padding:4px 10px;border-radius:50px;font-size:0.75rem;font-weight:700">Orange Money</span>
              <span style="background:var(--vert);color:#fff;padding:4px 10px;border-radius:50px;font-size:0.75rem;font-weight:700">Livraison</span>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2024 DAKARTECH - Tous droits réservés</p>
          <div class="footer-flags">🇸🇳</div>
        </div>
      </div>
    </footer>
  `;
}

// === INITIALISATION ===

document.addEventListener('DOMContentLoaded', () => {
  // Initialiser le panier
  Panier.updateUI();
});
