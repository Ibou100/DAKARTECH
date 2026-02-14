// frontend/js/produits.js
// Gestion de la page catalogue des produits DAKARTECH

// === ÉTAT DE LA PAGE ===
let etat = {
  page: 1,
  categorie: '',
  recherche: '',
  prixMin: null,
  prixMax: null,
  totalPages: 1
};

// === INITIALISATION ===

document.addEventListener('DOMContentLoaded', () => {
  renderHeader('produits');
  renderFooter();

  // Lire les paramètres URL
  const params = new URLSearchParams(window.location.search);
  if (params.get('cat')) etat.categorie = params.get('cat');

  // Initialiser les filtres
  initFiltres();
  chargerProduits();
});

// === FILTRES ===

function initFiltres() {
  // Sélectionner la catégorie depuis URL
  if (etat.categorie) {
    const btn = document.querySelector(`.filter-btn[data-cat="${etat.categorie}"]`);
    if (btn) btn.classList.add('active');
  } else {
    const tousBtn = document.querySelector('.filter-btn[data-cat=""]');
    if (tousBtn) tousBtn.classList.add('active');
  }

  // Boutons de catégorie
  document.querySelectorAll('.filter-btn[data-cat]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn[data-cat]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      etat.categorie = btn.dataset.cat;
      etat.page = 1;
      chargerProduits();
    });
  });

  // Recherche
  const searchInput = document.getElementById('recherche');
  if (searchInput) {
    searchInput.value = etat.recherche;
    searchInput.addEventListener('input', debounce(() => {
      etat.recherche = searchInput.value;
      etat.page = 1;
      chargerProduits();
    }, 400));
  }

  // Filtres prix
  const prixMinInput = document.getElementById('prix-min');
  const prixMaxInput = document.getElementById('prix-max');
  if (prixMinInput) {
    prixMinInput.addEventListener('change', () => {
      etat.prixMin = prixMinInput.value ? parseInt(prixMinInput.value) : null;
      etat.page = 1;
      chargerProduits();
    });
  }
  if (prixMaxInput) {
    prixMaxInput.addEventListener('change', () => {
      etat.prixMax = prixMaxInput.value ? parseInt(prixMaxInput.value) : null;
      etat.page = 1;
      chargerProduits();
    });
  }
}

// Fonction de debounce pour la recherche
function debounce(fn, delay) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}

// === CHARGEMENT DES PRODUITS ===

async function chargerProduits() {
  const container = document.getElementById('produits-grid');
  const totalEl = document.getElementById('total-produits');
  if (!container) return;

  // Afficher le chargement
  container.innerHTML = `
    <div class="loading-overlay" style="grid-column:1/-1">
      <div class="loading-spinner"></div>
      <p>Chargement des produits…</p>
    </div>`;

  // Construire l'URL avec les filtres
  const params = new URLSearchParams({ page: etat.page, per_page: 12 });
  if (etat.categorie) params.set('category', etat.categorie);
  if (etat.recherche) params.set('search', etat.recherche);
  if (etat.prixMin) params.set('min_price', etat.prixMin);
  if (etat.prixMax) params.set('max_price', etat.prixMax);

  try {
    const data = await apiRequest(`/products?${params.toString()}`);

    if (totalEl) totalEl.textContent = `${data.total} produit${data.total > 1 ? 's' : ''} trouvé${data.total > 1 ? 's' : ''}`;

    etat.totalPages = data.pages;

    if (!data.products || data.products.length === 0) {
      container.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--gray)">
          <div style="font-size:3rem;margin-bottom:12px">🔍</div>
          <h3 style="margin-bottom:8px">Aucun produit trouvé</h3>
          <p>Essayez d'autres filtres ou une recherche différente</p>
          <button class="btn btn-secondary" style="margin-top:16px" onclick="resetFiltres()">
            Réinitialiser les filtres
          </button>
        </div>`;
      renderPagination(0, 0);
      return;
    }

    container.innerHTML = data.products.map(p => renderCarteProduct(p)).join('');
    renderPagination(data.current_page, data.pages);

  } catch (err) {
    container.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--gray)">
        <div style="font-size:3rem;margin-bottom:12px">❌</div>
        <h3>Erreur de connexion</h3>
        <p>Le serveur est inaccessible. Vérifiez que le backend est démarré.</p>
        <code style="background:var(--gray-light);padding:8px 16px;border-radius:8px;display:inline-block;margin-top:12px;font-size:0.85rem">
          cd backend && python run.py
        </code>
      </div>`;
  }
}

// === CARTE PRODUIT ===

function renderCarteProduct(p) {
  const icon = {
    telephones: '📱', ordinateurs: '💻', tablettes: '📟',
    accessoires: '🎧', montres: '⌚'
  }[p.category] || '🛍️';

  const stockBadge = p.stock <= 5 && p.stock > 0
    ? `<div class="product-stock-low">⚡ Plus que ${p.stock} en stock!</div>`
    : p.stock === 0 ? `<div class="product-stock-low" style="color:var(--rouge)">❌ Rupture de stock</div>` : '';

  // Afficher vraie image si disponible, sinon emoji placeholder
  const imageHTML = p.image_url
    ? `<img
        src="${p.image_url}"
        alt="${p.name}"
        class="product-img"
        style="cursor:pointer"
        onclick="window.location.href='produits.html?id=${p.id}'"
        onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"
       >
       <div class="product-img-placeholder" style="display:none;cursor:pointer" onclick="window.location.href='produits.html?id=${p.id}'">${icon}</div>`
    : `<div class="product-img-placeholder" style="cursor:pointer" onclick="window.location.href='produits.html?id=${p.id}'">${icon}</div>`;

  return `
    <div class="product-card">
      ${imageHTML}
      <div class="product-info">
        <div class="product-category">${p.category}</div>
        <div class="product-name">${p.name}</div>
        <div class="product-desc">${truncate(p.description, 70)}</div>
        ${stockBadge}
        <div class="product-price">${formatPrix(p.price)}</div>
        <div class="product-actions">
          ${p.stock > 0
            ? `<button class="btn btn-primary btn-sm" style="flex:1" onclick='Panier.ajouter(${JSON.stringify(p)})'>
                🛒 Ajouter
              </button>`
            : `<button class="btn btn-sm" style="flex:1;background:var(--gray-light);color:var(--gray);cursor:not-allowed" disabled>
                Indisponible
              </button>`
          }
        </div>
      </div>
    </div>`;
}

// === PAGINATION ===

function renderPagination(currentPage, totalPages) {
  const container = document.getElementById('pagination');
  if (!container || totalPages <= 1) {
    if (container) container.innerHTML = '';
    return;
  }

  let html = '';

  // Bouton précédent
  if (currentPage > 1) {
    html += `<button class="page-btn" onclick="changerPage(${currentPage - 1})">←</button>`;
  }

  // Pages
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
      html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="changerPage(${i})">${i}</button>`;
    } else if (i === currentPage - 2 || i === currentPage + 2) {
      html += `<span style="padding:8px 4px;color:var(--gray)">…</span>`;
    }
  }

  // Bouton suivant
  if (currentPage < totalPages) {
    html += `<button class="page-btn" onclick="changerPage(${currentPage + 1})">→</button>`;
  }

  container.innerHTML = html;
}

function changerPage(page) {
  etat.page = page;
  chargerProduits();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// === RÉINITIALISATION DES FILTRES ===

function resetFiltres() {
  etat = { page: 1, categorie: '', recherche: '', prixMin: null, prixMax: null, totalPages: 1 };

  const searchInput = document.getElementById('recherche');
  if (searchInput) searchInput.value = '';

  const prixMin = document.getElementById('prix-min');
  const prixMax = document.getElementById('prix-max');
  if (prixMin) prixMin.value = '';
  if (prixMax) prixMax.value = '';

  document.querySelectorAll('.filter-btn[data-cat]').forEach(b => b.classList.remove('active'));
  const tousBtn = document.querySelector('.filter-btn[data-cat=""]');
  if (tousBtn) tousBtn.classList.add('active');

  chargerProduits();
}
