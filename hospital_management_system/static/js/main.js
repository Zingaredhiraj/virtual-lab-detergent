/**
 * Hospital Management System - Client-side JavaScript
 */

// Sidebar toggle
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
        sidebar.classList.toggle('mobile-open');
        toggleOverlay();
    } else {
        sidebar.classList.toggle('collapsed');
    }
}

// Mobile overlay
function toggleOverlay() {
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.onclick = function() {
            document.getElementById('sidebar').classList.remove('mobile-open');
            this.classList.remove('active');
        };
        document.body.appendChild(overlay);
    }
    overlay.classList.toggle('active');
}

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function() { alert.remove(); }, 300);
        }, 5000);
    });
});

// Confirm delete actions
document.addEventListener('DOMContentLoaded', function() {
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Already handled by inline onsubmit
        });
    });
});
