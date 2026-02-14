// frontend/js/panier.js
// Gestion de la page panier DAKARTECH

document.addEventListener('DOMContentLoaded', () => {
  renderHeader('');
  renderFooter();
  afficherPanier();
});

// === AFFICHAGE DU PANIER ===

function afficherPanier() {
  const items = Panier.get();
  const container = document.getElementById('panier-items');
  const resumeEl = document.getElementById('panier-resume');
  const videEl = document.getElementById('panier-vide');
  const contentEl = document.getElementById('panier-content');

  if (items.length === 0) {
    if (videEl) videEl.style.display = 'block';
    if (contentEl) contentEl.style.display = 'none';
    return;
  }

  if (videEl) videEl.style.display = 'none';
  if (contentEl) contentEl.style.display = 'grid';

  // Afficher les articles
  if (container) {
    container.innerHTML = items.map(item => `
      <div class="panier-item" data-id="${item.id}" style="
        display:grid;grid-template-columns:80px 1fr auto;gap:16px;align-items:center;
        padding:20px;background:#fff;border-radius:var(--radius);border:1px solid var(--border);
        margin-bottom:12px;
      ">
        <!-- Image -->
        <div style="width:80px;height:80px;border-radius:var(--radius-sm);
             background:linear-gradient(135deg,#E8F5EE,#C6E8D4);
             display:flex;align-items:center;justify-content:center;font-size:2rem">
          ${item.category === 'telephones' ? '📱' : item.category === 'ordinateurs' ? '💻' : '🎧'}
        </div>

        <!-- Info produit -->
        <div>
          <div style="font-weight:700;font-size:1rem;margin-bottom:4px">${item.name}</div>
          <div style="font-size:0.85rem;color:var(--gray);text-transform:capitalize;margin-bottom:8px">${item.category}</div>
          <div style="font-size:1.1rem;font-weight:800;color:var(--vert)">${formatPrix(item.price)}</div>

          <!-- Contrôle quantité mobile -->
          <div class="qty-control" style="margin-top:10px">
            <button class="qty-btn" onclick="modifierQte(${item.id}, ${item.quantite - 1})">−</button>
            <span class="qty-value">${item.quantite}</span>
            <button class="qty-btn" onclick="modifierQte(${item.id}, ${item.quantite + 1})">+</button>
            <span style="margin-left:12px;font-size:0.85rem;color:var(--gray)">
              = ${formatPrix(item.price * item.quantite)}
            </span>
          </div>
        </div>

        <!-- Bouton supprimer -->
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px">
          <button onclick="supprimerItem(${item.id})" title="Supprimer"
            style="background:none;border:none;cursor:pointer;font-size:1.3rem;color:var(--rouge)">
            🗑️
          </button>
        </div>
      </div>
    `).join('');
  }

  // Calcul du résumé
  mettreAJourResume();
}

function mettreAJourResume() {
  const items = Panier.get();
  const sousTotal = Panier.sousTotal();
  const nombreArticles = Panier.nombreArticles();

  const resumeEl = document.getElementById('panier-resume');
  if (!resumeEl) return;

  resumeEl.innerHTML = `
    <h3 style="font-size:1.1rem;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--border)">
      🧾 Récapitulatif
    </h3>

    <!-- Articles -->
    ${items.map(item => `
      <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:0.9rem">
        <span style="color:var(--gray)">${truncate(item.name, 30)} × ${item.quantite}</span>
        <span style="font-weight:600">${formatPrix(item.price * item.quantite)}</span>
      </div>
    `).join('')}

    <hr style="border:none;border-top:1px solid var(--border);margin:16px 0">

    <div style="display:flex;justify-content:space-between;margin-bottom:8px">
      <span style="font-weight:600">Sous-total (${nombreArticles} article${nombreArticles > 1 ? 's' : ''})</span>
      <span style="font-weight:700">${formatPrix(sousTotal)}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:16px;font-size:0.9rem;color:var(--gray)">
      <span>Frais de livraison</span>
      <span>Calculés à l'étape suivante</span>
    </div>

    <div style="background:var(--vert-light);border:2px solid var(--vert);border-radius:var(--radius);padding:14px;display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <span style="font-weight:800;font-size:1rem">Total estimé</span>
      <span style="font-size:1.4rem;font-weight:800;color:var(--vert)">${formatPrix(sousTotal)}</span>
    </div>

    <a href="commande.html" class="btn btn-primary btn-full btn-lg" style="margin-bottom:12px">
      ✅ Passer la commande
    </a>
    <a href="produits.html" class="btn btn-secondary btn-full">
      ← Continuer mes achats
    </a>

    <div style="margin-top:16px;padding:12px;background:#FFF8E1;border-radius:var(--radius-sm);font-size:0.82rem;color:#7D6600">
      🚗 Livraison gratuite dès 100 000 FCFA dans Dakar intra-muros
    </div>

    <!-- Modes de paiement acceptés -->
    <div style="margin-top:16px;text-align:center">
      <p style="font-size:0.8rem;color:var(--gray);margin-bottom:8px">Paiements acceptés:</p>
      <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap">
        <span style="background:#E0F7FA;color:#00B4D8;padding:4px 10px;border-radius:50px;font-size:0.75rem;font-weight:700">Wave</span>
        <span style="background:#FFF3E0;color:#FF6B00;padding:4px 10px;border-radius:50px;font-size:0.75rem;font-weight:700">Orange Money</span>
        <span style="background:var(--vert-light);color:var(--vert);padding:4px 10px;border-radius:50px;font-size:0.75rem;font-weight:700">Livraison</span>
      </div>
    </div>
  `;
}

// === ACTIONS ===

function modifierQte(produitId, nouvelleQte) {
  Panier.modifierQuantite(produitId, nouvelleQte);
  afficherPanier();
}

function supprimerItem(produitId) {
  Panier.supprimer(produitId);
  afficherPanier();
  showToast('Article retiré du panier', 'warning');
}

function viderPanier() {
  if (confirm('Voulez-vous vraiment vider votre panier?')) {
    Panier.vider();
    afficherPanier();
    showToast('Panier vidé', 'warning');
  }
}
