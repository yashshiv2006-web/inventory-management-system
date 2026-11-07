/**
 * Retail Stock Optimization and Sales Intelligence Platform
 * Products Management Client-Side Script
 *
 * Why this file exists:
 * Provides instantaneous client-side table filtering, asset valuation previews,
 * and deletion confirmation alerts without reloading the browser.
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Instant Client-Side Table Filter
    setupProductFilter();

    // 2. Add / Edit Product Live Valuation Estimator
    setupValuationCalculator();
});

/**
 * Filters the product table rows instantly as the user types in the search input.
 */
function setupProductFilter() {
    const searchInput = document.getElementById('productClientSearch');
    const table = document.getElementById('productsTable');

    if (!searchInput || !table) return;

    searchInput.addEventListener('keyup', function () {
        const query = searchInput.value.toLowerCase().trim();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(function (row) {
            const text = row.innerText.toLowerCase();
            if (text.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

/**
 * Calculates total inventory asset value in real time while typing price & initial stock.
 */
function setupValuationCalculator() {
    const priceInput = document.getElementById('productPriceInput');
    const stockInput = document.getElementById('productStockInput');
    const valuationDisplay = document.getElementById('assetValuationPreview');

    if (!priceInput || !stockInput || !valuationDisplay) return;

    function updateValuation() {
        const price = parseFloat(priceInput.value || '0');
        const stock = parseInt(stockInput.value || '0');
        const valuation = price * stock;

        valuationDisplay.innerText = `$${valuation.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;
    }

    priceInput.addEventListener('input', updateValuation);
    stockInput.addEventListener('input', updateValuation);
}

/**
 * Confirms deletion to prevent accidental catalog removals.
 */
function confirmDelete(productName) {
    return confirm(`Are you sure you want to permanently delete '${productName}' and all its inventory ledger records?`);
}
