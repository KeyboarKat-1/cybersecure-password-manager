// Landing Page JavaScript - CyberSecure Theme
// Handles animations, interactions, and modern UI effects

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all landing page functionality
    initNavigation();
    initScrollAnimations();
    initHeroAnimations();
    initMobileMenu();
    initSmoothScrolling();
    initParticleEffects();
});

// Navigation functionality
function initNavigation() {
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScrollY = currentScrollY;
    });

    // Active link highlighting
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section[id]');

    window.addEventListener('scroll', () => {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;

            if (window.scrollY >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').slice(1) === current) {
                link.classList.add('active');
            }
        });
    });
}

// Mobile menu functionality
function initMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('mobile-active');
            mobileToggle.classList.toggle('active');

            // Animate hamburger menu
            const spans = mobileToggle.querySelectorAll('span');
            if (mobileToggle.classList.contains('active')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });

        // Close mobile menu when clicking a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('mobile-active');
                mobileToggle.classList.remove('active');

                const spans = mobileToggle.querySelectorAll('span');
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            });
        });
    }
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.offsetTop;
                const offsetPosition = elementPosition - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Scroll-triggered animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe all feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        observer.observe(card);
    });

    // Observe security items
    document.querySelectorAll('.security-item').forEach(item => {
        observer.observe(item);
    });

    // Observe diagram layers with staggered animation
    document.querySelectorAll('.diagram-layer').forEach((layer, index) => {
        layer.style.transitionDelay = `${index * 0.2}s`;
        observer.observe(layer);
    });
}

// Hero section animations
function initHeroAnimations() {
    // Typing effect for hero title (optional enhancement)
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        heroTitle.style.opacity = '0';
        heroTitle.style.transform = 'translateY(30px)';

        setTimeout(() => {
            heroTitle.style.transition = 'all 1s ease-out';
            heroTitle.style.opacity = '1';
            heroTitle.style.transform = 'translateY(0)';
        }, 300);
    }

    // Animate hero stats with counter effect
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        const target = parseInt(stat.textContent.replace(/\D/g, ''));
        animateCounter(stat, 0, target, 2000);
    });

    // Floating elements animation
    const floatingElements = document.querySelectorAll('.floating-element');
    floatingElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.5}s`;
    });
}

// Counter animation for statistics
function animateCounter(element, start, end, duration) {
    if (start === end) return;

    const range = end - start;
    const minTimer = 50;
    const stepTime = Math.abs(Math.floor(duration / range));
    const timer = stepTime < minTimer ? minTimer : stepTime;

    const startTime = new Date().getTime();
    const endTime = startTime + duration;

    function run() {
        const now = new Date().getTime();
        const remaining = Math.max((endTime - now) / duration, 0);
        const value = Math.round(end - (remaining * range));

        element.textContent = isNaN(value) ? element.textContent : value;
        if (value == end) {
            clearInterval(timer);
        }
    }

    const timer_id = setInterval(run, timer);
    run();
}

// Particle effects for background
function initParticleEffects() {
    // Create floating particles in hero background
    const heroSection = document.querySelector('.hero');
    if (!heroSection) return;

    for (let i = 0; i < 50; i++) {
        createParticle(heroSection);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';

    // Random properties
    const size = Math.random() * 4 + 1;
    const left = Math.random() * 100;
    const animationDuration = Math.random() * 10 + 10;
    const animationDelay = Math.random() * 5;

    particle.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: ${Math.random() > 0.5 ? 'var(--cyber-blue)' : 'var(--cyber-purple)'};
        border-radius: 50%;
        left: ${left}%;
        top: -10px;
        opacity: ${Math.random() * 0.5 + 0.1};
        animation: float-particle ${animationDuration}s linear ${animationDelay}s infinite;
        pointer-events: none;
    `;

    container.appendChild(particle);

    // Remove particle after animation
    setTimeout(() => {
        particle.remove();
    }, (animationDuration + animationDelay) * 1000);
}

// Add particle animation keyframes via JavaScript
const particleStyle = document.createElement('style');
particleStyle.textContent = `
    @keyframes float-particle {
        0% {
            transform: translateY(-10px) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: var(--particle-opacity, 0.3);
        }
        90% {
            opacity: var(--particle-opacity, 0.3);
        }
        100% {
            transform: translateY(100vh) rotate(360deg);
            opacity: 0;
        }
    }

    .navbar.scrolled {
        background: rgba(10, 10, 10, 0.98);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .nav-link.active {
        color: var(--cyber-blue);
    }

    .nav-link.active::after {
        width: 100%;
    }

    .nav-links.mobile-active {
        display: flex;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--cyber-dark);
        flex-direction: column;
        padding: 20px;
        border-top: 1px solid rgba(0, 212, 255, 0.1);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    .mobile-menu-toggle.active span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 5px);
    }

    .mobile-menu-toggle.active span:nth-child(2) {
        opacity: 0;
    }

    .mobile-menu-toggle.active span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -6px);
    }

    .animate-in {
        animation: fadeInUp 0.8s ease-out forwards;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .feature-card:hover .icon-bg {
        animation: bounce 0.6s ease;
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }

    .btn:hover {
        transform: translateY(-2px);
    }

    .btn:active {
        transform: translateY(0);
    }
`;
document.head.appendChild(particleStyle);

// Performance optimization - throttle scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Apply throttling to scroll events
window.addEventListener('scroll', throttle(() => {
    // Throttled scroll handlers can be added here
}, 16)); // ~60fps

// Add loading animation for page load
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// Add CSS for loaded state
const loadedStyle = document.createElement('style');
loadedStyle.textContent = `
    body {
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    body.loaded {
        opacity: 1;
    }
`;
document.head.appendChild(loadedStyle);

// Console welcome message for developers
console.log(`
🔐 CyberSecure Password Manager
   Enterprise-grade security for everyone

   Built with: Flask, AES-256, TOTP 2FA
   Theme: Cybersecurity Dark Mode
   Status: Production Ready

   Happy coding! 🚀
`);