// frontend/js/commande.js
// Gestion du formulaire de commande DAKARTECH

// Frais de livraison par ville (miroir du backend)
const FRAIS_LIVRAISON = {
  'dakar': 1500, 'plateau': 1500, 'medina': 1500, 'point_e': 1500,
  'sacre_coeur': 1500, 'mermoz': 1500, 'fann': 1500,
  'yoff': 2000, 'ngor': 2000, 'ouakam': 2000, 'almadies': 2000,
  'pikine': 2500, 'guediawaye': 2500, 'thiaroye': 2500,
  'rufisque': 3000, 'bargny': 3500, 'sebikotane': 4000,
  'thies': 5000, 'mbour': 6000, 'saly': 7000,
  'kaolack': 10000, 'saint_louis': 12000, 'ziguinchor': 15000,
  'touba': 10000, 'diourbel': 9000, 'louga': 10000,
  'tambacounda': 15000, 'kolda': 18000, 'kedougou': 20000,
};
const FRAIS_DEFAUT = 5000;

document.addEventListener('DOMContentLoaded', () => {
  renderHeader('');
  renderFooter();

  const items = Panier.get();
  if (items.length === 0) {
    window.location.href = 'panier.html';
    return;
  }

  afficherRecapitulatif();
  initFormulaire();
});

// === RÉCAPITULATIF ===

function afficherRecapitulatif() {
  const items = Panier.get();
  const container = document.getElementById('recap-items');
  const sousTotal = Panier.sousTotal();

  if (!container) return;

  container.innerHTML = `
    <h3 style="font-size:1rem;font-weight:700;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--border)">
      🧾 Votre commande
    </h3>
    ${items.map(item => `
      <div style="display:flex;gap:10px;margin-bottom:10px;align-items:center">
        <div style="width:44px;height:44px;border-radius:8px;background:var(--gray-light);
             display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0">
          ${item.category === 'telephones' ? '📱' : item.category === 'ordinateurs' ? '💻' : '🎧'}
        </div>
        <div style="flex:1">
          <div style="font-size:0.85rem;font-weight:600">${truncate(item.name, 35)}</div>
          <div style="font-size:0.8rem;color:var(--gray)">Qté: ${item.quantite}</div>
        </div>
        <div style="font-weight:700;font-size:0.9rem;color:var(--vert)">${formatPrix(item.price * item.quantite)}</div>
      </div>
    `).join('')}
    <hr style="border:none;border-top:1px solid var(--border);margin:12px 0">
    <div style="display:flex;justify-content:space-between;margin-bottom:6px">
      <span style="font-weight:600">Sous-total</span>
      <span style="font-weight:700">${formatPrix(sousTotal)}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:12px" id="recap-livraison">
      <span style="color:var(--gray)">Livraison</span>
      <span style="color:var(--gray)">Choisissez une ville</span>
    </div>
    <div style="background:var(--vert-light);border:2px solid var(--vert);border-radius:var(--radius);padding:12px;display:flex;justify-content:space-between" id="recap-total">
      <span style="font-weight:800">Total</span>
      <span style="font-size:1.2rem;font-weight:800;color:var(--vert)">${formatPrix(sousTotal)}</span>
    </div>
  `;
}

function mettreAJourTotal(fraisLivraison) {
  const sousTotal = Panier.sousTotal();
  const total = sousTotal + fraisLivraison;

  const livraisonEl = document.getElementById('recap-livraison');
  const totalEl = document.getElementById('recap-total');

  if (livraisonEl) {
    livraisonEl.innerHTML = `
      <span style="color:var(--gray)">Livraison</span>
      <span style="font-weight:600;color:${fraisLivraison === 0 ? 'var(--vert)' : 'inherit'}">
        ${fraisLivraison === 0 ? '🎁 Gratuite' : formatPrix(fraisLivraison)}
      </span>`;
  }
  if (totalEl) {
    totalEl.innerHTML = `
      <span style="font-weight:800">Total</span>
      <span style="font-size:1.2rem;font-weight:800;color:var(--vert)">${formatPrix(total)}</span>`;
  }

  // Mettre à jour le total du bouton
  const btnTotal = document.getElementById('btn-total-montant');
  if (btnTotal) btnTotal.textContent = formatPrix(total);
}

// === FORMULAIRE ===

function initFormulaire() {
  // Changement de ville → mise à jour frais livraison
  const villeSelect = document.getElementById('ville');
  if (villeSelect) {
    villeSelect.addEventListener('change', () => {
      const ville = villeSelect.value;
      const frais = FRAIS_LIVRAISON[ville] ?? FRAIS_DEFAUT;
      mettreAJourTotal(frais);

      // Afficher info frais
      const infoEl = document.getElementById('info-livraison');
      if (infoEl) {
        infoEl.textContent = ville
          ? (frais === 0 ? '🎁 Livraison gratuite!' : `Frais de livraison: ${formatPrix(frais)}`)
          : '';
        infoEl.style.color = frais === 0 ? 'var(--vert)' : 'var(--gray)';
      }
    });
  }

  // Changement type paiement → afficher/masquer champs mobile
  document.querySelectorAll('input[name="payment_type"]').forEach(radio => {
    radio.addEventListener('change', () => {
      const champsMobile = document.getElementById('champs-mobile');
      if (champsMobile) {
        champsMobile.style.display = radio.value === 'mobile' ? 'block' : 'none';
      }
    });
  });

  // Soumission formulaire
  const form = document.getElementById('form-commande');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await soumettreCommande();
    });
  }
}

// === SOUMISSION ===

async function soumettreCommande() {
  const btnSubmit = document.getElementById('btn-commander');
  const erreurEl = document.getElementById('erreur-commande');

  // Valider le formulaire
  const erreur = validerFormulaire();
  if (erreur) {
    if (erreurEl) { erreurEl.textContent = erreur; erreurEl.style.display = 'block'; }
    showToast(erreur, 'error');
    return;
  }

  if (erreurEl) erreurEl.style.display = 'none';

  // Désactiver le bouton
  if (btnSubmit) {
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="loading-spinner"></span> Envoi en cours…';
  }

  // Construire les données
  const items = Panier.get();
  const ville = document.getElementById('ville').value;
  const fraisLivraison = FRAIS_LIVRAISON[ville] ?? FRAIS_DEFAUT;
  const paymentType = document.querySelector('input[name="payment_type"]:checked').value;

  const commandeData = {
    items: items.map(i => ({ product_id: i.id, quantity: i.quantite })),
    delivery_address: document.getElementById('adresse').value,
    delivery_phone: document.getElementById('tel-livraison').value,
    delivery_city: ville,
    delivery_notes: document.getElementById('notes')?.value || '',
    customer_name: document.getElementById('nom-client').value,
    customer_email: document.getElementById('email-client')?.value || '',
    payment_type: paymentType,
    mobile_method: paymentType === 'mobile' ? document.querySelector('input[name="mobile_method"]:checked')?.value : null,
    mobile_phone: paymentType === 'mobile' ? document.getElementById('tel-mobile')?.value : null,
  };

  try {
    const data = await apiRequest('/orders', {
      method: 'POST',
      body: JSON.stringify(commandeData)
    });

    // Succès → sauvegarder infos et rediriger
    localStorage.setItem('dakartech_last_order', JSON.stringify({
      order: data.order,
      payment_instructions: data.payment_instructions
    }));

    Panier.vider();
    window.location.href = 'confirmation.html';

  } catch (err) {
    showToast(`Erreur: ${err.message}`, 'error');
    if (erreurEl) { erreurEl.textContent = err.message; erreurEl.style.display = 'block'; }
    if (btnSubmit) {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = `✅ Confirmer la commande — <span id="btn-total-montant">${formatPrix(Panier.sousTotal() + (FRAIS_LIVRAISON[document.getElementById('ville').value] ?? FRAIS_DEFAUT))}</span>`;
    }
  }
}

function validerFormulaire() {
  const nom = document.getElementById('nom-client')?.value?.trim();
  const tel = document.getElementById('tel-livraison')?.value?.trim();
  const adresse = document.getElementById('adresse')?.value?.trim();
  const ville = document.getElementById('ville')?.value;
  const paymentType = document.querySelector('input[name="payment_type"]:checked');

  if (!nom) return 'Veuillez entrer votre nom complet';
  if (!tel || tel.length < 8) return 'Numéro de téléphone invalide';
  if (!adresse) return 'Veuillez entrer votre adresse de livraison';
  if (!ville) return 'Veuillez sélectionner votre ville';
  if (!paymentType) return 'Veuillez choisir un mode de paiement';

  if (paymentType.value === 'mobile') {
    const method = document.querySelector('input[name="mobile_method"]:checked');
    const telMobile = document.getElementById('tel-mobile')?.value?.trim();
    if (!method) return 'Veuillez choisir Wave ou Orange Money';
    if (!telMobile || telMobile.length < 8) return 'Veuillez entrer votre numéro Wave/Orange Money';
  }

  return null; // Pas d'erreur
}
