/**
 * Admin Panel Javascript
 * Handles sidebar behavior, dark mode toggle, dashboard filters, auto-refresh and interactivity.
 */

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSidebar();
    initDashboardInteractivity();
});

// Theme Management (Dark / Light Mode)
function initTheme() {
    const savedTheme = localStorage.getItem('admin_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleDarkMode() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('admin_theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('darkModeIcon');
    if (!icon) return;
    
    if (theme === 'dark') {
        icon.className = 'fa fa-sun';
    } else {
        icon.className = 'fa fa-moon';
    }
}

// Sidebar Behavior
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const savedState = localStorage.getItem('sidebar_collapsed') === 'true';
    
    if (savedState && sidebar) {
        sidebar.classList.add('collapsed');
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed'));
}

// Interactivity for tables and forms
function initDashboardInteractivity() {
    // Add row click navigation indicator if rows have locations
    const rows = document.querySelectorAll('.appt-row');
    rows.forEach(row => {
        row.style.cursor = 'pointer';
    });
}
