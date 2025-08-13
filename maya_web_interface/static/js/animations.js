// Initialize GSAP animations
class MayaAnimations {
    constructor() {
        // Set default GSAP settings
        gsap.config({
            force3D: true,
            autoSleep: 60,
            nullTargetWarn: false
        });
        
        // Initialize animations
        this.initPageLoad();
        this.initHoverEffects();
    }
    
    // Page load animations
    initPageLoad() {
        // Initial page load animation
        gsap.from('body', { 
            duration: 0.5, 
            autoAlpha: 0,
            ease: 'power2.out'
        });
        
        // Animate sidebar
        gsap.from('.sidebar', {
            duration: 0.8,
            x: -50,
            autoAlpha: 0,
            ease: 'power3.out',
            delay: 0.2
        });
        
        // Animate main content
        gsap.from('.content-section', {
            duration: 0.8,
            y: 20,
            autoAlpha: 0,
            ease: 'power3.out',
            delay: 0.4,
            stagger: 0.1
        });
    }
    
    // Hover and interaction effects
    initHoverEffects() {
        // Button hover effects
        gsap.utils.toArray('.btn, button, [role="button"]').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                gsap.to(btn, { 
                    scale: 1.05, 
                    duration: 0.2,
                    ease: 'power2.out'
                });
            });
            
            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, { 
                    scale: 1, 
                    duration: 0.2,
                    ease: 'power2.out'
                });
            });
            
            btn.addEventListener('mousedown', () => {
                gsap.to(btn, { 
                    scale: 0.98, 
                    duration: 0.1,
                    ease: 'power2.out'
                });
            });
            
            btn.addEventListener('mouseup', () => {
                gsap.to(btn, { 
                    scale: 1, 
                    duration: 0.1,
                    ease: 'power2.out'
                });
            });
        });
    }
    
    // Todo item animations
    animateTodoIn(element, onComplete) {
        return gsap.fromTo(element,
            { y: 20, opacity: 0 },
            { 
                y: 0, 
                opacity: 1, 
                duration: 0.3,
                ease: 'back.out(1.2)',
                onComplete
            }
        );
    }
    
    animateTodoOut(element, onComplete) {
        return gsap.to(element, {
            height: 0,
            opacity: 0,
            marginBottom: 0,
            paddingTop: 0,
            paddingBottom: 0,
            duration: 0.3,
            ease: 'power2.in',
            onComplete: () => {
                if (onComplete) onComplete();
                element.remove();
            }
        });
    }
    
    // Chat message animations
    animateMessageIn(element, isUser = false) {
        return gsap.fromTo(element,
            { 
                x: isUser ? 50 : -50,
                opacity: 0 
            },
            { 
                x: 0, 
                opacity: 1, 
                duration: 0.3,
                ease: 'power2.out'
            }
        );
    }
    
    // Modal animations
    animateModalIn(modal) {
        gsap.set(modal, { display: 'flex' });
        return gsap.fromTo(modal.querySelector('.modal-content'),
            { y: 50, opacity: 0 },
            { 
                y: 0, 
                opacity: 1, 
                duration: 0.3,
                ease: 'back.out(1.2)'
            }
        );
    }
    
    animateModalOut(modal) {
        return gsap.to(modal.querySelector('.modal-content'), {
            y: 50,
            opacity: 0,
            duration: 0.2,
            ease: 'power2.in',
            onComplete: () => {
                gsap.set(modal, { display: 'none' });
            }
        });
    }
    
    // Section transitions
    switchSection(currentSection, newSection) {
        const tl = gsap.timeline();
        
        tl.to(currentSection, {
            opacity: 0,
            y: 20,
            duration: 0.2,
            ease: 'power2.in',
            onComplete: () => {
                currentSection.style.display = 'none';
                newSection.style.display = 'block';
            }
        })
        .fromTo(newSection,
            { opacity: 0, y: -20 },
            { 
                opacity: 1, 
                y: 0, 
                duration: 0.3,
                ease: 'power2.out'
            },
            '-=0.1'
        );
        
        return tl;
    }
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mayaAnimations = new MayaAnimations();
});
