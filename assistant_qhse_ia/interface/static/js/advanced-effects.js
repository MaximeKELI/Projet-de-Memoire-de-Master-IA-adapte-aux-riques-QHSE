/**
 * EFFETS AVANCÉS QHSE IA v2.0
 * Animations JavaScript et effets visuels spectaculaires
 */

class AdvancedEffects {
    constructor() {
        this.init();
    }

    init() {
        this.setupParticleSystem();
        this.setupTypingEffects();
        this.setupScrollAnimations();
        this.setupHoverEffects();
        this.setupLoadingAnimations();
        this.setupDataVisualization();
        this.setupInteractiveElements();
    }

    // ========================================
    // SYSTÈME DE PARTICULES
    // ========================================
    
    setupParticleSystem() {
        this.createParticleCanvas();
        this.animateParticles();
    }

    createParticleCanvas() {
        const canvas = document.createElement('canvas');
        canvas.id = 'particle-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '1';
        canvas.style.opacity = '0.6';
        
        document.body.appendChild(canvas);
        
        this.particleCanvas = canvas;
        this.particleCtx = canvas.getContext('2d');
        this.particles = [];
        
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        this.particleCanvas.width = window.innerWidth;
        this.particleCanvas.height = window.innerHeight;
    }

    createParticle() {
        return {
            x: Math.random() * this.particleCanvas.width,
            y: Math.random() * this.particleCanvas.height,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2,
            size: Math.random() * 3 + 1,
            opacity: Math.random() * 0.5 + 0.2,
            color: this.getRandomColor()
        };
    }

    getRandomColor() {
        const colors = [
            '#00f2fe', '#4facfe', '#43e97b', '#f093fb', 
            '#667eea', '#764ba2', '#fa709a', '#fee140'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    animateParticles() {
        // Créer de nouvelles particules
        if (this.particles.length < 50) {
            this.particles.push(this.createParticle());
        }

        // Nettoyer le canvas
        this.particleCtx.clearRect(0, 0, this.particleCanvas.width, this.particleCanvas.height);

        // Animer les particules
        this.particles.forEach((particle, index) => {
            particle.x += particle.vx;
            particle.y += particle.vy;

            // Rebondir sur les bords
            if (particle.x < 0 || particle.x > this.particleCanvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > this.particleCanvas.height) particle.vy *= -1;

            // Dessiner la particule
            this.particleCtx.beginPath();
            this.particleCtx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.particleCtx.fillStyle = particle.color;
            this.particleCtx.globalAlpha = particle.opacity;
            this.particleCtx.fill();

            // Supprimer les particules trop anciennes
            if (particle.opacity <= 0) {
                this.particles.splice(index, 1);
            } else {
                particle.opacity -= 0.005;
            }
        });

        requestAnimationFrame(() => this.animateParticles());
    }

    // ========================================
    // EFFETS DE FRAPPE ET ÉCRITURE
    // ========================================
    
    setupTypingEffects() {
        this.typewriterElements = document.querySelectorAll('.typewriter');
        this.typewriterElements.forEach(element => {
            this.initTypewriter(element);
        });
    }

    initTypewriter(element) {
        const text = element.textContent;
        element.textContent = '';
        element.style.borderRight = '2px solid #00f2fe';
        
        let i = 0;
        const typeInterval = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(typeInterval);
                // Faire clignoter le curseur
                setInterval(() => {
                    element.style.borderRight = element.style.borderRight === 'none' ? '2px solid #00f2fe' : 'none';
                }, 500);
            }
        }, 100);
    }

    // ========================================
    // ANIMATIONS AU SCROLL
    // ========================================
    
    setupScrollAnimations() {
        this.observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateElement(entry.target);
                }
            });
        }, this.observerOptions);

        // Observer tous les éléments avec des classes d'animation
        const animatedElements = document.querySelectorAll('[class*="animate-"]');
        animatedElements.forEach(element => {
            this.observer.observe(element);
        });
    }

    animateElement(element) {
        const animationClass = Array.from(element.classList).find(cls => cls.startsWith('animate-'));
        if (animationClass) {
            element.classList.add('animation-running');
        }
    }

    // ========================================
    // EFFETS DE SURVOL
    // ========================================
    
    setupHoverEffects() {
        const hoverElements = document.querySelectorAll('.hover-effect, .card, .btn');
        
        hoverElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => this.onHoverEnter(e));
            element.addEventListener('mouseleave', (e) => this.onHoverLeave(e));
        });
    }

    onHoverEnter(e) {
        const element = e.target;
        element.style.transform = 'translateY(-5px) scale(1.02)';
        element.style.boxShadow = '0 20px 40px rgba(0, 242, 254, 0.3)';
        element.style.transition = 'all 0.3s ease';
        
        // Effet de ripple
        this.createRipple(e, element);
    }

    onHoverLeave(e) {
        const element = e.target;
        element.style.transform = 'translateY(0) scale(1)';
        element.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
    }

    createRipple(e, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
        ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(0, 242, 254, 0.3)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s ease-out';
        ripple.style.pointerEvents = 'none';
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    // ========================================
    // ANIMATIONS DE CHARGEMENT
    // ========================================
    
    setupLoadingAnimations() {
        this.createLoadingSpinner();
        this.setupProgressBars();
    }

    createLoadingSpinner() {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.innerHTML = `
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .loading-spinner {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 9999;
            }
            .spinner-ring {
                width: 40px;
                height: 40px;
                border: 4px solid transparent;
                border-top: 4px solid #00f2fe;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                position: absolute;
            }
            .spinner-ring:nth-child(2) {
                width: 30px;
                height: 30px;
                top: 5px;
                left: 5px;
                animation-delay: 0.2s;
            }
            .spinner-ring:nth-child(3) {
                width: 20px;
                height: 20px;
                top: 10px;
                left: 10px;
                animation-delay: 0.4s;
            }
        `;
        document.head.appendChild(style);
    }

    setupProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const progress = bar.dataset.progress || 0;
            this.animateProgressBar(bar, progress);
        });
    }

    animateProgressBar(bar, targetProgress) {
        let currentProgress = 0;
        const increment = targetProgress / 100;
        
        const interval = setInterval(() => {
            currentProgress += increment;
            bar.style.width = currentProgress + '%';
            
            if (currentProgress >= targetProgress) {
                clearInterval(interval);
                bar.classList.add('progress-complete');
            }
        }, 20);
    }

    // ========================================
    // VISUALISATION DE DONNÉES
    // ========================================
    
    setupDataVisualization() {
        this.animateCharts();
        this.setupCounters();
    }

    animateCharts() {
        const charts = document.querySelectorAll('.chart');
        charts.forEach(chart => {
            this.observer.observe(chart);
            chart.addEventListener('animationstart', () => {
                this.animateChartBars(chart);
            });
        });
    }

    animateChartBars(chart) {
        const bars = chart.querySelectorAll('.chart-bar');
        bars.forEach((bar, index) => {
            setTimeout(() => {
                const height = bar.dataset.height || '0%';
                bar.style.height = height;
                bar.classList.add('chart-bar-animated');
            }, index * 100);
        });
    }

    setupCounters() {
        const counters = document.querySelectorAll('.counter');
        counters.forEach(counter => {
            this.observer.observe(counter);
            counter.addEventListener('animationstart', () => {
                this.animateCounter(counter);
            });
        });
    }

    animateCounter(counter) {
        const target = parseInt(counter.dataset.target) || 0;
        const duration = parseInt(counter.dataset.duration) || 2000;
        const increment = target / (duration / 16);
        let current = 0;
        
        const interval = setInterval(() => {
            current += increment;
            counter.textContent = Math.floor(current);
            
            if (current >= target) {
                counter.textContent = target;
                clearInterval(interval);
            }
        }, 16);
    }

    // ========================================
    // ÉLÉMENTS INTERACTIFS
    // ========================================
    
    setupInteractiveElements() {
        this.setupButtonEffects();
        this.setupCardEffects();
        this.setupModalEffects();
    }

    setupButtonEffects() {
        const buttons = document.querySelectorAll('.btn, button');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.createClickEffect(e);
            });
        });
    }

    createClickEffect(e) {
        const button = e.target;
        const rect = button.getBoundingClientRect();
        
        const effect = document.createElement('div');
        effect.style.position = 'absolute';
        effect.style.left = (e.clientX - rect.left) + 'px';
        effect.style.top = (e.clientY - rect.top) + 'px';
        effect.style.width = '0';
        effect.style.height = '0';
        effect.style.background = 'rgba(0, 242, 254, 0.5)';
        effect.style.borderRadius = '50%';
        effect.style.transform = 'translate(-50%, -50%)';
        effect.style.animation = 'ripple 0.6s ease-out';
        effect.style.pointerEvents = 'none';
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(effect);
        
        setTimeout(() => effect.remove(), 600);
    }

    setupCardEffects() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) scale(1.02)';
                card.style.boxShadow = '0 20px 40px rgba(0, 242, 254, 0.2)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
                card.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            });
        });
    }

    setupModalEffects() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show', () => {
                modal.style.opacity = '0';
                modal.style.transform = 'scale(0.8)';
                modal.style.display = 'block';
                
                requestAnimationFrame(() => {
                    modal.style.transition = 'all 0.3s ease';
                    modal.style.opacity = '1';
                    modal.style.transform = 'scale(1)';
                });
            });
        });
    }

    // ========================================
    // MÉTHODES UTILITAIRES
    // ========================================
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
        });
        
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    createGlowEffect(element) {
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        
        const glow = document.createElement('div');
        glow.style.cssText = `
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 242, 254, 0.3), transparent);
            animation: shimmer 2s infinite;
            pointer-events: none;
        `;
        
        element.appendChild(glow);
    }

    // ========================================
    // INITIALISATION
    // ========================================
    
    static init() {
        document.addEventListener('DOMContentLoaded', () => {
            new AdvancedEffects();
        });
    }
}

// Initialiser les effets
AdvancedEffects.init();

// Exporter pour utilisation globale
window.AdvancedEffects = AdvancedEffects;
