const API_BASE = 'http://localhost:8000';

// навигация
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(sectionId).classList.add('active');
    event.target.classList.add('active');
    
    if (sectionId === 'products') loadProducts();
    if (sectionId === 'movements') loadMovements();
    if (sectionId === 'inventory') loadInventoryProducts();
    if (sectionId === 'reports') loadStockReport();
}

// Products
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/api/products`);
        const products = await response.json();
        
        const tbody = document.getElementById('productsTableBody');
        tbody.innerHTML = products.map(product => `
            <tr>
                <td>${product.sku}</td>
                <td>${product.name}</td>
                <td>${product.category || '-'}</td>
                <td>
                    <span class="badge ${product.quantity <= product.min_stock ? 'badge-danger' : 'badge-success'}">
                        ${product.quantity} ${product.unit}
                    </span>
                </td>
                <td>${product.unit}</td>
                <td>${product.cell || '-'}</td>
                <td>${product.expiration_date || 'Не указан'}</td>
                <td>
                    <button class="btn btn-warning" onclick="editProduct(${product.id})">✏️</button>
                </td>
            </tr>
        `).join('');
        
        // обновление products
        updateProductSelects(products);
    } catch (error) {
        console.error('Error loading products:', error);
        alert('Ошибка загрузки товаров');
    }
}

function updateProductSelects(products) {
    const selects = ['movementProduct', 'inventoryProduct'];
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            select.innerHTML = products.map(p => 
                `<option value="${p.id}">${p.sku} - ${p.name}</option>`
            ).join('');
        }
    });
}

async function createProduct(event) {
    event.preventDefault();
    
    const product = {
        sku: document.getElementById('productSku').value,
        name: document.getElementById('productName').value,
        category: document.getElementById('productCategory').value,
        unit: document.getElementById('productUnit').value,
        quantity: parseFloat(document.getElementById('productQuantity').value) || 0,
        min_stock: parseFloat(document.getElementById('productMinStock').value) || 0,
        price: parseFloat(document.getElementById('productPrice').value) || 0,
        cell: document.getElementById('productCell').value,
        expiration_date: document.getElementById('productExpiration').value || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(product)
        });
        
        if (response.ok) {
            closeModal('productModal');
            loadProducts();
            document.getElementById('productForm').reset();
            alert('Товар успешно добавлен');
        } else {
            alert('Ошибка при добавлении товара');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка соединения с сервером');
    }
}

function searchProducts() {
    const searchTerm = document.getElementById('productSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#productsTableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// Movements
async function createMovement(event) {
    event.preventDefault();
    
    const movement = {
        movement_type: document.getElementById('movementType').value,
        product_id: parseInt(document.getElementById('movementProduct').value),
        quantity: parseFloat(document.getElementById('movementQuantity').value),
        batch: document.getElementById('movementBatch').value,
        note: document.getElementById('movementNote').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/movements`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(movement)
        });
        
        if (response.ok) {
            document.getElementById('movementForm').reset();
            loadProducts();
            alert('Операция успешно выполнена');
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка соединения с сервером');
    }
}

async function loadMovements() {
    // загрузка истории передвижений
}

// Inventory
async function loadInventoryProducts() {
    const response = await fetch(`${API_BASE}/api/products`);
    const products = await response.json();
    
    const select = document.getElementById('inventoryProduct');
    select.innerHTML = products.map(p => 
        `<option value="${p.id}">${p.sku} - ${p.name}</option>`
    ).join('');
    
    if (products.length > 0) {
        loadProductInfo();
    }
}

async function loadProductInfo() {
    const productId = document.getElementById('inventoryProduct').value;
    const response = await fetch(`${API_BASE}/api/products`);
    const products = await response.json();
    const product = products.find(p => p.id == productId);
    
    if (product) {
        document.getElementById('currentQuantity').value = product.quantity;
        document.getElementById('inventoryCell').value = product.cell || '';
        document.getElementById('inventoryExpiration').value = product.expiration_date || '';
    }
}

async function submitInventory(event) {
    event.preventDefault();
    
    const inventory = {
        product_id: parseInt(document.getElementById('inventoryProduct').value),
        actual_quantity: parseFloat(document.getElementById('actualQuantity').value),
        cell: document.getElementById('inventoryCell').value,
        expiration_date: document.getElementById('inventoryExpiration').value || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/inventory/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inventory)
        });
        
        if (response.ok) {
            document.getElementById('inventoryForm').reset();
            alert('Инвентаризация успешно проведена');
        } else {
            alert('Ошибка при проведении инвентаризации');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка соединения с сервером');
    }
}

// Reports
async function loadStockReport() {
    try {
        const response = await fetch(`${API_BASE}/api/reports/stock`);
        const report = await response.json();
        
        document.getElementById('totalProducts').textContent = report.total_products;
        document.getElementById('totalQuantity').textContent = report.total_quantity;
        document.getElementById('totalValue').textContent = report.total_value.toFixed(2) + ' ₽';
        document.getElementById('lowStockCount').textContent = report.low_stock.length;
        
        const lowStockAlert = document.getElementById('lowStockAlert');
        const lowStockList = document.getElementById('lowStockList');
        
        if (report.low_stock.length > 0) {
            lowStockAlert.style.display = 'block';
            lowStockList.innerHTML = report.low_stock.map(p => 
                `<li>${p.name} (${p.sku}) - осталось: ${p.quantity} ${p.unit}</li>`
            ).join('');
        } else {
            lowStockAlert.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading report:', error);
    }
}

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// скрытие модала когда курсор нажал не на него
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// инитиализьон
document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
});