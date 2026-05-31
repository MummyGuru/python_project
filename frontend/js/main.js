let currentUser = null;

document.addEventListener('DOMContentLoaded', function() {
    initAuth();
    initNavigation();
    loadDashboardData();
});

function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    
    navButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.dataset.section;
            
            navButtons.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(`${section}-section`).classList.add('active');
            
            loadSectionData(section);
        });
    });
}

function loadSectionData(section) {
    switch(section) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'products':
            loadProducts();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'movements':
            loadMovements();
            break;
        case 'reservations':
            loadReservations();
            break;
        case 'reports':
            // Отчеты загружаются по клику
            break;
    }
}

async function loadDashboardData() {
    try {
        const response = await fetch('/api/reports/stock', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateDashboardStats(data);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateDashboardStats(data) {
    document.getElementById('totalProducts').textContent = data.total_products || 0;
    document.getElementById('totalQuantity').textContent = data.total_quantity || 0;
    document.getElementById('lowStock').textContent = data.low_stock?.length || 0;
    document.getElementById('totalValue').textContent = `${data.total_value?.toFixed(2) || 0} ₽`;
}

function showModal(content) {
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modalBody');
    
    modalBody.innerHTML = content;
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

// Закрытие модалки при клике вне её
window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        closeModal();
    }
}