/**
 * Retail Stock Optimization and Sales Intelligence Platform
 * Dashboard & Interactive Controls Module
 *
 * Why this file exists:
 * Powers responsive layout interactions, modal dialogs, real-time POS calculations,
 * and AJAX communication with the Flask backend APIs.
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Sidebar Toggle for Mobile View
    setupSidebarToggle();

    // 2. Real-Time Point-of-Sale Calculator in Sales Modal
    setupPosCalculator();

    // 3. Quick Restock Modal Handler
    setupRestockModal();
});

/**
 * Handles sidebar expansion and collapsing for small screens.
 */
function setupSidebarToggle() {
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('active');
        });
    }
}

/**
 * Calculates final sale total in real time when cashier changes quantity or discount.
 */
function setupPosCalculator() {
    const productSelect = document.getElementById('saleProductSelect');
    const quantityInput = document.getElementById('saleQuantityInput');
    const discountInput = document.getElementById('saleDiscountInput');
    const totalDisplay = document.getElementById('saleTotalDisplay');

    if (!productSelect || !quantityInput || !totalDisplay) return;

    function recalculate() {
        const selectedOption = productSelect.options[productSelect.selectedIndex];
        const unitPrice = parseFloat(selectedOption?.dataset?.price || '0');
        const quantity = parseInt(quantityInput.value || '1');
        const discount = parseFloat(discountInput?.value || '0');

        const subtotal = unitPrice * quantity;
        const discountAmt = subtotal * (discount / 100.0);
        const finalTotal = Math.max(0, subtotal - discountAmt);

        totalDisplay.innerText = `$${finalTotal.toFixed(2)}`;
    }

    productSelect.addEventListener('change', recalculate);
    quantityInput.addEventListener('input', recalculate);
    if (discountInput) discountInput.addEventListener('input', recalculate);
}

/**
 * Populates restock modal with product details when clicking 'Quick Restock'.
 */
function setupRestockModal() {
    const restockModal = document.getElementById('restockModal');
    if (!restockModal) return;

    restockModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        if (!button) return;

        const productId = button.getAttribute('data-product-id');
        const productName = button.getAttribute('data-product-name');
        const currentStock = button.getAttribute('data-current-stock');

        const modalProdId = restockModal.querySelector('#modalProductId');
        const modalProdName = restockModal.querySelector('#modalProductName');
        const modalCurrentStock = restockModal.querySelector('#modalCurrentStock');

        if (modalProdId) modalProdId.value = productId;
        if (modalProdName) modalProdName.innerText = productName;
        if (modalCurrentStock) modalCurrentStock.innerText = currentStock;
    });
}
