/* ═══════════════════════════════════════════════════════════════
   HopeBridge — Main JavaScript
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initScrollAnimations();
    initCountUpAnimations();
    initMobileMenu();
    initAlertDismiss();
    initPasswordToggle();
    initProfilePicPreview();
});

/* ── Navbar Scroll Effect ────────────────────────────────────── */
function initNavbar() {
    const navbar = document.querySelector('.hb-navbar');
    if (!navbar) return;

    const onScroll = () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // Run once on load
}

/* ── Scroll-Triggered Animations ─────────────────────────────── */
function initScrollAnimations() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    if (!elements.length) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15, rootMargin: '0px 0px -50px 0px' }
    );

    elements.forEach((el) => observer.observe(el));
}

/* ── Count-Up Animation ──────────────────────────────────────── */
function initCountUpAnimations() {
    const counters = document.querySelectorAll('[data-count-to]');
    if (!counters.length) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );

    counters.forEach((el) => observer.observe(el));
}

function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-count-to'), 10);
    const duration = parseInt(el.getAttribute('data-duration') || '2000', 10);
    const prefix = el.getAttribute('data-prefix') || '';
    const suffix = el.getAttribute('data-suffix') || '';
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease-out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * eased);

        el.textContent = prefix + current.toLocaleString('en-IN') + suffix;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/* ── Mobile Menu Toggle ──────────────────────────────────────── */
function initMobileMenu() {
    const toggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    const navActions = document.querySelector('.nav-actions');
    if (!toggle) return;

    toggle.addEventListener('click', () => {
        navLinks?.classList.toggle('active');
        navActions?.classList.toggle('active');

        // Toggle icon
        const icon = toggle.querySelector('span');
        if (icon) {
            icon.textContent = navLinks?.classList.contains('active') ? '✕' : '☰';
        }
    });

    // Close on link click
    navLinks?.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            navActions?.classList.remove('active');
        });
    });
}

/* ── Alert Auto-Dismiss ──────────────────────────────────────── */
function initAlertDismiss() {
    const alerts = document.querySelectorAll('.hb-alert, .alert');
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}

/* ── Password Visibility Toggle ──────────────────────────────── */
function initPasswordToggle() {
    document.querySelectorAll('.password-toggle').forEach((btn) => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            if (input && input.type === 'password') {
                input.type = 'text';
                btn.textContent = '🙈';
            } else if (input) {
                input.type = 'password';
                btn.textContent = '👁️';
            }
        });
    });
}

/* ── Profile Picture Preview ─────────────────────────────────── */
function initProfilePicPreview() {
    const input = document.querySelector('#id_profile_picture');
    const preview = document.querySelector('.profile-pic-preview');
    if (!input || !preview) return;

    input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (ev) => {
                preview.src = ev.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
}

/* ── Notification Bell ───────────────────────────────────────── */
function markNotificationRead(notificationId) {
    fetch(`/notifications/mark-read/${notificationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
    }).then((res) => {
        if (res.ok) {
            const badge = document.querySelector('.notification-bell .badge');
            if (badge) {
                const count = parseInt(badge.textContent) - 1;
                if (count <= 0) {
                    badge.style.display = 'none';
                } else {
                    badge.textContent = count;
                }
            }
        }
    });
}

function markAllNotificationsRead() {
    fetch('/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
    }).then((res) => {
        if (res.ok) {
            const badge = document.querySelector('.notification-bell .badge');
            if (badge) badge.style.display = 'none';
        }
    });
}

/* ── Utility: Get CSRF Token ─────────────────────────────────── */
function getCsrfToken() {
    const cookie = document.cookie
        .split(';')
        .find((c) => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}
