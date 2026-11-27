/**
 * Atelier Nilaya — Admin Panel Vanilla JS
 * Handles Live Price Math, 4-Step Form, Photo Drag/Reorder, Search, Safe Delete, Toasts
 */

document.addEventListener('DOMContentLoaded', () => {

  // 1. Mobile Sidebar Toggle
  const navToggle = document.getElementById('mobileNavToggle');
  const sidebar = document.querySelector('.admin-sidebar');
  if (navToggle && sidebar) {
    navToggle.addEventListener('click', () => {
      sidebar.classList.toggle('is-open');
    });
    // Close sidebar on outside click
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !navToggle.contains(e.target) && sidebar.classList.contains('is-open')) {
        sidebar.classList.remove('is-open');
      }
    });
  }

  // 2. Toast Notification Auto-Dismiss
  const toast = document.querySelector('.toast-msg');
  if (toast) {
    setTimeout(() => {
      toast.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(20px)';
      setTimeout(() => toast.remove(), 500);
    }, 4000);
  }

  // 3. Live Price Calculator in Piece Form
  const weightInput = document.getElementById('goldWeightInput');
  const puritySelect = document.getElementById('metalPuritySelect');
  const makingTypeSelect = document.getElementById('makingTypeSelect');
  const makingValInput = document.getElementById('makingValInput');
  const stoneValInput = document.getElementById('stoneValInput');
  const rate22kMeta = parseFloat(document.body.dataset.rate22k || 7200);
  const rate18kMeta = parseFloat(document.body.dataset.rate18k || 5890);
  const rateSilverMeta = parseFloat(document.body.dataset.rateSilver || 92);

  function calculateLivePrice() {
    if (!weightInput) return;

    const weight = parseFloat(weightInput.value) || 0;
    const purity = puritySelect ? puritySelect.value : '22K';
    let rate = rate22kMeta;
    if (purity.includes('18K')) rate = rate18kMeta;
    else if (purity.includes('Silver') || purity.includes('925')) rate = rateSilverMeta;

    const rawMetalPrice = weight * rate;

    const makingType = makingTypeSelect ? makingTypeSelect.value : 'percent';
    const makingVal = parseFloat(makingValInput ? makingValInput.value : 0) || 0;
    let makingCharge = 0;
    if (makingType === 'percent') {
      makingCharge = rawMetalPrice * (makingVal / 100);
    } else {
      makingCharge = makingVal;
    }

    const stoneVal = parseFloat(stoneValInput ? stoneValInput.value : 0) || 0;
    const taxableSubtotal = rawMetalPrice + makingCharge + stoneVal;
    const gst = taxableSubtotal * 0.03; // 3% GST on fine jewellery in India
    const finalTotal = Math.round(taxableSubtotal + gst);

    // Update DOM display
    const elMetal = document.getElementById('calcMetalCost');
    const elMaking = document.getElementById('calcMakingCharge');
    const elStone = document.getElementById('calcStoneVal');
    const elGst = document.getElementById('calcGst');
    const elTotal = document.getElementById('calcFinalTotal');
    const hiddenPriceInput = document.getElementById('finalCalculatedPrice');

    if (elMetal) elMetal.innerText = '₹' + Math.round(rawMetalPrice).toLocaleString('en-IN');
    if (elMaking) elMaking.innerText = '₹' + Math.round(makingCharge).toLocaleString('en-IN');
    if (elStone) elStone.innerText = '₹' + Math.round(stoneVal).toLocaleString('en-IN');
    if (elGst) elGst.innerText = '₹' + Math.round(gst).toLocaleString('en-IN');
    if (elTotal) elTotal.innerText = '₹' + finalTotal.toLocaleString('en-IN');
    if (hiddenPriceInput) hiddenPriceInput.value = finalTotal;
  }

  if (weightInput) {
    [weightInput, puritySelect, makingTypeSelect, makingValInput, stoneValInput].forEach(el => {
      if (el) el.addEventListener('input', calculateLivePrice);
    });
    calculateLivePrice();
  }

  // 4. 4-Step Piece Form Navigation
  const stepBtns = document.querySelectorAll('.form-step-btn');
  const stepPanels = document.querySelectorAll('.form-step-panel');
  if (stepBtns.length > 0 && stepPanels.length > 0) {
    stepBtns.forEach((btn, idx) => {
      btn.addEventListener('click', () => {
        stepBtns.forEach(b => b.classList.remove('active'));
        stepPanels.forEach(p => p.style.display = 'none');

        btn.classList.add('active');
        const targetId = btn.dataset.target;
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) targetPanel.style.display = 'block';
      });
    });

    // Next step helper buttons
    document.querySelectorAll('[data-next-step]').forEach(btn => {
      btn.addEventListener('click', () => {
        const nextId = btn.dataset.nextStep;
        const matchingTab = document.querySelector(`.form-step-btn[data-target="${nextId}"]`);
        if (matchingTab) matchingTab.click();
      });
    });
  }

  // 5. Client-Side Table Search & Filter
  const tableSearchInput = document.getElementById('tableSearchInput');
  if (tableSearchInput) {
    tableSearchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      const rows = document.querySelectorAll('.admin-table tbody tr');
      rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
      });
    });
  }

  // 6. Safe Delete Confirmation Modal
  const deleteModal = document.getElementById('deleteConfirmModal');
  const deleteForm = document.getElementById('deleteActionForm');
  const deleteItemName = document.getElementById('deleteItemNameSpan');

  document.querySelectorAll('[data-confirm-delete]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const actionUrl = btn.dataset.actionUrl;
      const itemName = btn.dataset.itemName || 'this piece';
      if (deleteModal && deleteForm) {
        deleteForm.action = actionUrl;
        if (deleteItemName) deleteItemName.innerText = itemName;
        deleteModal.classList.add('is-active');
      }
    });
  });

  const cancelDeleteBtn = document.getElementById('cancelDeleteModalBtn');
  if (cancelDeleteBtn && deleteModal) {
    cancelDeleteBtn.addEventListener('click', () => {
      deleteModal.classList.remove('is-active');
    });
  }

  // 7. Unsaved Changes Warning
  let hasUnsavedChanges = false;
  const forms = document.querySelectorAll('form[data-track-changes]');
  forms.forEach(form => {
    form.addEventListener('input', () => { hasUnsavedChanges = true; });
    form.addEventListener('submit', () => { hasUnsavedChanges = false; });
  });

  window.addEventListener('beforeunload', (e) => {
    if (hasUnsavedChanges) {
      e.preventDefault();
      e.returnValue = 'You have unsaved changes. Leave anyway?';
    }
  });

});
