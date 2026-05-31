const ROLES = {
    ADMIN: 'admin',
    MANAGER: 'manager',
    WAREHOUSE: 'warehouse'
};

const PERMISSIONS = {
    [ROLES.ADMIN]: {
        canViewDashboard: true,
        canViewProducts: true,
        canAddProducts: true,
        canEditProducts: true,
        canDeleteProducts: true,
        canViewInventory: true,
        canViewMovements: true,
        canCreateMovements: true,
        canViewReservations: true,
        canCreateReservations: true,
        canViewReports: true,
        canManageUsers: true,
        canManagePeriods: true
    },
    [ROLES.MANAGER]: {
        canViewDashboard: true,
        canViewProducts: true,
        canAddProducts: true,
        canEditProducts: true,
        canDeleteProducts: false,
        canViewInventory: true,
        canViewMovements: true,
        canCreateMovements: false,
        canRequestMovement: true,
        canViewReservations: true,
        canCreateReservations: true,
        canViewReports: true,
        canViewSales: true,
        canPlaceOrders: true,
        canManageUsers: false,
        canManagePeriods: false
    },
    [ROLES.WAREHOUSE]: {
        canViewDashboard: true,
        canViewProducts: true,
        canAddProducts: false,
        canEditProducts: false,
        canDeleteProducts: false,
        canViewInventory: true,
        canUpdateInventory: true,
        canViewMovements: true,
        canCreateMovements: true,
        canProcessRequests: true,
        canViewReservations: true,
        canViewReports: true,
        canViewCompanyInfo: true,
        canManageUsers: false,
        canManagePeriods: false
    }
};

function getCurrentUser() {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    if (!token) return null;
    
    // Decode token (в реальности нужно правильно декодировать JWT)
    return {
        username: username,
        role: localStorage.getItem('role') || ROLES.ADMIN
    };
}

function hasPermission(permission) {
    const user = getCurrentUser();
    if (!user) return false;
    
    const rolePermissions = PERMISSIONS[user.role];
    return rolePermissions && rolePermissions[permission];
}

function checkRole(allowedRoles) {
    const user = getCurrentUser();
    if (!user) return false;
    
    return allowedRoles.includes(user.role);
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    window.location.href = '/login.html';
}

function initAuth() {
    const user = getCurrentUser();
    if (!user) {
        window.location.href = '/login.html';
        return;
    }
    
    document.getElementById('userName').textContent = user.username;
    document.getElementById('userRole').textContent = getRoleName(user.role);
    
    applyRoleBasedUI(user.role);
}

function getRoleName(role) {
    const roles = {
        [ROLES.ADMIN]: 'Администратор',
        [ROLES.MANAGER]: 'Менеджер',
        [ROLES.WAREHOUSE]: 'Кладовщик'
    };
    return roles[role] || role;
}

function applyRoleBasedUI(role) {
    // Скрываем/показываем элементы в зависимости от роли
    const permissions = PERMISSIONS[role];
    
    if (!permissions.canAddProducts) {
        document.querySelectorAll('.btn-add-product').forEach(btn => btn.style.display = 'none');
    }
    
    if (!permissions.canCreateMovements) {
        document.querySelectorAll('.btn-create-movement').forEach(btn => btn.style.display = 'none');
    }
    
    if (!permissions.canCreateReservations) {
        document.querySelectorAll('.btn-create-reservation').forEach(btn => btn.style.display = 'none');
    }
    
    // Показываем/скрываем разделы
    if (!permissions.canViewReports) {
        document.querySelector('[data-section="reports"]').style.display = 'none';
    }
}