/**
 * AuraStyle — Main Frontend JavaScript
 * Handles search (text / image / voice / multimodal), product display,
 * filters, modal, theme toggle, and UI state.
 */

/* ── State ──────────────────────────────────────────────────── */
const state = {
  mode: 'text',           // 'text' | 'image' | 'voice' | 'multimodal'
  isListening: false,
  selectedFiles: [],
  allProducts: [],
  currentResults: [],
  recognition: null,
  filters: {
    category: '',
    gender: '',
    color: '',
    material: '',
    season: '',
    maxPrice: 25000,
    minRating: 0,
  }
};

/* ── DOM refs ────────────────────────────────────────────────── */
const $ = id => document.getElementById(id);

const searchInput      = $('search-input');
const searchBtn        = $('search-btn');
const voiceBtn         = $('voice-btn');
const uploadBtn        = $('upload-btn');
const fileInput        = $('file-input');
const imageUploadArea  = $('image-upload-area');
const imagePreviewGrid = $('image-preview-grid');
const voiceStatus      = $('voice-status');
const voiceText        = $('voice-text');
const productGrid      = $('product-grid');
const allProductsGrid  = $('all-products-grid');
const resultsSection   = $('results-section');
const allSection       = $('all-products-section');
const resultCount      = $('result-count');
const resultQuery      = $('result-query');
const loadingOverlay   = $('loading-overlay');
const productModal     = $('product-modal');
const themeToggle      = $('theme-toggle');
const navLinks         = document.querySelectorAll('.nav-links a');

/* ── Search Mode Tabs ────────────────────────────────────────── */
document.querySelectorAll('.search-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    state.mode = tab.dataset.mode;
    updateSearchUI();
  });
});

function setMode(newMode) {
  state.mode = newMode;
  updateSearchUI();
  // Reset voice state when leaving voice mode
  if (newMode !== 'voice' && state.isListening) {
    state.isListening = false;
    state.recognition && state.recognition.stop();
    voiceBtn.classList.remove('active-voice');
    voiceStatus.classList.remove('visible');
  }
}
/* ── Voice Search ────────────────────────────────────────────── */
voiceBtn.addEventListener('click', toggleVoice);

function toggleVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    showToast('Voice search is not supported in this browser.', 'error');
    // Switch to text mode
    setMode('text');
    return;
  }

  if (state.isListening) {
    state.recognition && state.recognition.stop();
    stopListening();
    return;
  }

  // Switch to voice mode tab
  setMode('voice');

  state.recognition = new SpeechRecognition();
  state.recognition.lang = 'en-US';
  state.recognition.interimResults = true;
  state.recognition.maxAlternatives = 1;

  state.recognition.onstart = () => {
    state.isListening = true;
    voiceBtn.classList.add('active-voice');
    voiceStatus.classList.add('visible');
  };

  state.recognition.onresult = e => {
    const transcript = Array.from(e.results)
      .map(r => r[0].transcript)
      .join('');
    searchInput.value = transcript;
    voiceText.textContent = `Heard: "${transcript}"`;
  };

  state.recognition.onend = () => {
    stopListening();
    if (searchInput.value.trim()) {
      performSearch();
    }
  };

  state.recognition.onerror = err => {
    stopListening();
    showToast(`Voice error: ${err.error}`, 'error');
  };

  state.recognition.start();
}

function stopListening() {
  state.isListening = false;
  voiceBtn.classList.remove('active-voice');
  voiceStatus.classList.remove('visible');
}

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll('.search-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.mode === mode);
  });
  updateSearchUI();
}

/* ── Image Upload ────────────────────────────────────────────── */
uploadBtn.addEventListener('click', () => {
  setMode(state.mode === 'text' ? 'image' : state.mode);
  fileInput.click();
});

imageUploadArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', e => {
  addFiles(Array.from(e.target.files));
});

// Drag-and-drop
imageUploadArea.addEventListener('dragover', e => {
  e.preventDefault();
  imageUploadArea.classList.add('drag-over');
});
imageUploadArea.addEventListener('dragleave', () => {
  imageUploadArea.classList.remove('drag-over');
});
imageUploadArea.addEventListener('drop', e => {
  e.preventDefault();
  imageUploadArea.classList.remove('drag-over');
  addFiles(Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/')));
});

function addFiles(files) {
  state.selectedFiles = [...state.selectedFiles, ...files];
  renderPreviews();
}

function renderPreviews() {
  imagePreviewGrid.innerHTML = '';
  state.selectedFiles.forEach((file, i) => {
    const url = URL.createObjectURL(file);
    const img = document.createElement('img');
    img.src = url;
    img.className = 'preview-thumb';
    img.title = file.name;
    img.addEventListener('click', () => {
      state.selectedFiles.splice(i, 1);
      renderPreviews();
    });
    imagePreviewGrid.appendChild(img);
  });
}

/* ── Search ──────────────────────────────────────────────────── */
searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') performSearch();
});

async function performSearch() {
  const query = searchInput.value.trim();
  const hasImages = state.selectedFiles.length > 0;

  if (!query && !hasImages) {
    showToast('Please enter a search term or upload an image.', 'error');
    return;
  }

  showLoading(true);
  try {
    let data;

    if (query && hasImages) {
      // Multimodal
      const fd = new FormData();
      fd.append('query', query);
      fd.append('image', state.selectedFiles[0]);
      data = await postForm('/search/multimodal', fd);
    } else if (hasImages) {
      // Image only
      const fd = new FormData();
      fd.append('image', state.selectedFiles[0]);
      data = await postForm('/search/image', fd);
    } else if (state.mode === 'voice') {
      // Voice
      data = await postJSON('/voice-search', { transcript: query });
    } else {
      // Text
      data = await postJSON('/search/text', { query });
    }

    if (!data.success) throw new Error(data.error || 'Search failed');

    state.currentResults = data.results || [];
    displayResults(state.currentResults, data.query || query || '(image)');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    showLoading(false);
  }
}

function displayResults(products, query) {
  allSection.classList.add('hidden');
  resultsSection.classList.add('visible');

  resultCount.textContent = products.length;
  resultQuery.textContent = `"${query}"`;

  renderGrid(productGrid, applyFilters(products), true);
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ── Filters ─────────────────────────────────────────────────── */
function applyFilters(products) {
  return products.filter(p => {
    if (state.filters.category && p.category !== state.filters.category) return false;
    if (state.filters.gender && p.gender !== state.filters.gender && p.gender !== 'Unisex') return false;
    if (state.filters.season && p.season && !p.season.includes(state.filters.season)) return false;
    if (state.filters.color && p.colors && !p.colors.some(c => c.toLowerCase().includes(state.filters.color.toLowerCase()))) return false;
    if (state.filters.material && p.material && !p.material.toLowerCase().includes(state.filters.material.toLowerCase())) return false;
    if (p.price > state.filters.maxPrice) return false;
    if (p.rating < state.filters.minRating) return false;
    return true;
  });
}

// Wire up filter controls
['filter-category','filter-gender','filter-season'].forEach(id => {
  const el = $(id);
  if (!el) return;
  const key = id.replace('filter-', '');
  el.addEventListener('change', () => {
    state.filters[key] = el.value;
    rerender();
  });
});

const priceRange = $('price-range');
const priceDisplay = $('price-display');
if (priceRange) {
  priceRange.addEventListener('input', () => {
    state.filters.maxPrice = parseInt(priceRange.value);
    priceDisplay.textContent = `₹${Number(priceRange.value).toLocaleString('en-IN')}`;
    rerender();
  });
}

const ratingRange = $('rating-range');
if (ratingRange) {
  ratingRange.addEventListener('input', () => {
    state.filters.minRating = parseFloat(ratingRange.value);
    $('rating-display').textContent = `${ratingRange.value}★+`;
    rerender();
  });
}

function rerender() {
  const source = state.currentResults.length ? state.currentResults : state.allProducts;
  const grid = state.currentResults.length ? productGrid : allProductsGrid;
  renderGrid(grid, applyFilters(source), state.currentResults.length > 0);
}

/* ── Render Grid ─────────────────────────────────────────────── */
function showSkeletons(grid, count = 8) {
  grid.innerHTML = Array.from({ length: count }).map(() => `
    <div class="skeleton-card">
      <div class="skeleton-img"></div>
      <div class="skeleton-body">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line med"></div>
        <div class="skeleton-line short"></div>
      </div>
    </div>`).join('');
}

function renderGrid(grid, products, withScore = false) {
  if (!products.length) {
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px 0;color:var(--c-text-muted)">
      <div style="font-size:3rem;margin-bottom:16px">✦</div>
      <p>No products match your search. Try adjusting filters.</p>
    </div>`;
    return;
  }

  grid.innerHTML = products.map(p => productCard(p, withScore)).join('');

  // Attach click handlers
  grid.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('click', () => openModal(card.dataset.id));
  });
}

function stars(rating) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(5 - full - (half ? 1 : 0));
}

function productCard(p, withScore) {
  const score = withScore && p.similarity_score != null
    ? `<div class="card-score">${p.similarity_score}%</div>` : '';
  const badge = p.rating >= 4.7 ? `<div class="card-badge">Top Pick</div>` : '';

  return `
    <div class="product-card" data-id="${p._id}">
      <div class="card-image">
        <img src="${p.image_url}" alt="${p.name}" loading="lazy"
             onerror="this.src='https://images.unsplash.com/photo-1445205170230-053b83016050?w=400'">
        ${score}
        ${badge}
      </div>
      <div class="card-body">
        <div class="card-brand">${p.brand}</div>
        <div class="card-name">${p.name}</div>
        <div class="card-meta">
          <div class="card-price">₹${Number(p.price).toLocaleString('en-IN')}</div>
          <div class="card-rating"><span class="star">★</span> ${p.rating}</div>
        </div>
        <div class="card-category">${p.category} · ${p.gender}</div>
        <button class="card-cta">View Details →</button>
      </div>
    </div>`;
}

/* ── Modal ───────────────────────────────────────────────────── */
async function openModal(id) {
  showLoading(true);
  try {
    const data = await getJSON(`/product/${id}`);
    if (!data.success) throw new Error(data.error);
    renderModal(data.product);
    productModal.classList.add('open');
    document.body.style.overflow = 'hidden';
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    showLoading(false);
  }
}

function renderModal(p) {
  const sizeTags = (p.sizes || []).map(s => `<span class="modal-tag">${s}</span>`).join('');
  const colorTags = (p.colors || []).map(c => `<span class="modal-tag">${c}</span>`).join('');

  $('modal-image').innerHTML = `<img src="${p.image_url}" alt="${p.name}"
    onerror="this.src='https://images.unsplash.com/photo-1445205170230-053b83016050?w=600'">`;

  $('modal-inner').innerHTML = `
    <div class="modal-brand">${p.brand}</div>
    <h2 class="modal-name">${p.name}</h2>
    <div class="modal-rating">
      <span class="modal-stars">${stars(p.rating)}</span>
      <span>${p.rating} / 5.0</span>
    </div>
    <div class="modal-price">₹${Number(p.price).toLocaleString('en-IN')}</div>
    <p class="modal-desc">${p.description}</p>
    <div class="modal-attrs">
      <div class="modal-attr">
        <label>Category</label>
        <p>${p.category} · ${p.gender}</p>
      </div>
      <div class="modal-attr">
        <label>Material</label>
        <p>${p.material}</p>
      </div>
      <div class="modal-attr">
        <label>Season</label>
        <p>${p.season}</p>
      </div>
      <div class="modal-attr">
        <label>Sizes</label>
        <div class="modal-tags">${sizeTags}</div>
      </div>
      <div class="modal-attr">
        <label>Colors</label>
        <div class="modal-tags">${colorTags}</div>
      </div>
    </div>`;
}

document.querySelector('.modal-close').addEventListener('click', closeModal);
document.querySelector('.modal-backdrop').addEventListener('click', closeModal);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

function closeModal() {
  productModal.classList.remove('open');
  document.body.style.overflow = '';
}

/* ── Load All Products ───────────────────────────────────────── */
async function loadAllProducts() {
  showSkeletons(allProductsGrid, 12);
  try {
    const data = await getJSON('/products');
    state.allProducts = data.products || [];
    renderGrid(allProductsGrid, applyFilters(state.allProducts), false);
  } catch (err) {
    showToast('Could not load products. Is the server running?', 'error');
    allProductsGrid.innerHTML = `<p style="color:var(--c-text-muted);padding:40px 0">
      Could not connect to AuraStyle API.</p>`;
  }
}

/* ── Theme Toggle ────────────────────────────────────────────── */
const savedTheme = localStorage.getItem('aurastyle-theme');
if (savedTheme === 'light') document.body.classList.add('light-mode');
updateThemeIcon();

themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('light-mode');
  const theme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
  localStorage.setItem('aurastyle-theme', theme);
  updateThemeIcon();
});

function updateThemeIcon() {
  themeToggle.textContent = document.body.classList.contains('light-mode') ? '☀️' : '🌙';
}

/* ── Navigation ──────────────────────────────────────────────── */
navLinks.forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const target = link.getAttribute('href');
    if (target && target.startsWith('#')) {
      document.querySelector(target)?.scrollIntoView({ behavior: 'smooth' });
    }
    navLinks.forEach(l => l.classList.remove('active'));
    link.classList.add('active');
  });
});

// Show back to home link when results visible
$('back-to-all')?.addEventListener('click', () => {
  resultsSection.classList.remove('visible');
  allSection.classList.remove('hidden');
  state.currentResults = [];
});

/* ── Helpers: Loading & Toast ────────────────────────────────── */
function showLoading(on) {
  loadingOverlay.classList.toggle('visible', on);
}

function showToast(msg, type = 'success') {
  const container = $('toast-container');
  const icon = type === 'success' ? '✓' : '⚠';
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span class="toast-icon">${icon}</span><span>${msg}</span>`;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

/* ── Helpers: API ────────────────────────────────────────────── */
async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function postForm(url, formData) {
  const res = await fetch(url, { method: 'POST', body: formData });
  return res.json();
}

/* ── Init ────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  loadAllProducts();
  updateSearchUI();

  // Mobile Hamburger menu toggle
  const hamburger = document.querySelector('.nav-hamburger');
  const navLinksContainer = document.querySelector('.nav-links');
  if (hamburger && navLinksContainer) {
    hamburger.addEventListener('click', () => {
      const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
      hamburger.setAttribute('aria-expanded', !isExpanded);
      hamburger.classList.toggle('active');
      navLinksContainer.classList.toggle('open');
    });

    // Close mobile menu when clicking a link
    navLinksContainer.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.classList.remove('active');
        navLinksContainer.classList.remove('open');
      });
    });
  }
});
