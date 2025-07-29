// ===== Global Variables =====
let queryCount = 0;
let totalResponseTime = 0;
let isTyping = false;

// ===== DOM Content Loaded =====
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeSmoothScrolling();
    initializeDemo();
    initializeAnimations();
    initializeTheme();
    updateStats();
});

// ===== Navigation Functions =====
function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    const navToggle = document.querySelector('.navbar-toggle');
    const navMenu = document.querySelector('.navbar-menu');
    
    // Mobile menu toggle
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', toggleMenu);
    }
    
    // Navbar scroll effect
    if (navbar) {
        window.addEventListener('scroll', handleNavbarScroll);
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (navMenu && navMenu.classList.contains('active') && 
            !navMenu.contains(e.target) && !navToggle.contains(e.target)) {
            toggleMenu();
        }
    });
    
    // Close mobile menu when clicking on menu items
    const navItems = document.querySelectorAll('.navbar-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            if (navMenu.classList.contains('active')) {
                toggleMenu();
            }
        });
    });
}

function toggleMenu() {
    const navToggle = document.querySelector('.navbar-toggle');
    const navMenu = document.querySelector('.navbar-menu');
    
    if (navToggle && navMenu) {
        navToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
    }
}

function handleNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    const scrolled = window.scrollY > 50;
    
    if (navbar) {
        navbar.style.background = scrolled 
            ? 'rgba(255, 255, 255, 0.98)' 
            : 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = scrolled 
            ? '0 4px 20px rgba(0, 0, 0, 0.1)' 
            : 'none';
    }
}

// ===== Smooth Scrolling =====
function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ===== Demo Functions =====
function initializeDemo() {
    const demoInput = document.getElementById('demoQuery');
    const sendBtn = document.querySelector('.send-btn');
    
    // Enter key support
    if (demoInput) {
        demoInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !isTyping) {
                sendDemoQuery();
            }
        });
    }
    
    // Send button click
    if (sendBtn) {
        sendBtn.addEventListener('click', sendDemoQuery);
    }
    
    // Initialize typing animation
    startHeroTypingAnimation();
}

function setDemoQuery(query) {
    const demoInput = document.getElementById('demoQuery');
    if (demoInput) {
        demoInput.value = query;
        demoInput.focus();
    }
}

function sendDemoQuery() {
    const demoInput = document.getElementById('demoQuery');
    const chatHistory = document.getElementById('chatHistory');
    
    if (!demoInput || !chatHistory || isTyping) return;
    
    const query = demoInput.value.trim();
    if (!query) return;
    
    isTyping = true;
    
    // Add user message
    addChatMessage(query, 'user');
    
    // Clear input
    demoInput.value = '';
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    // Simulate API call
    setTimeout(() => {
        removeChatMessage(typingId);
        
        const response = generateDemoResponse(query);
        addChatMessage(response.answer, 'assistant');
        
        // Update stats
        queryCount++;
        totalResponseTime += response.responseTime;
        updateStats();
        
        isTyping = false;
    }, Math.random() * 2000 + 1000); // 1-3 seconds
}

function addChatMessage(content, type) {
    const chatHistory = document.getElementById('chatHistory');
    if (!chatHistory) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(messageContent);
    chatHistory.appendChild(messageDiv);
    
    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    // Add entrance animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px)';
    
    requestAnimationFrame(() => {
        messageDiv.style.transition = 'all 0.3s ease-out';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    });
    
    return messageDiv;
}

function addTypingIndicator() {
    const chatHistory = document.getElementById('chatHistory');
    if (!chatHistory) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message assistant typing';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    
    messageContent.appendChild(typingIndicator);
    typingDiv.appendChild(messageContent);
    chatHistory.appendChild(typingDiv);
    
    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    return typingDiv;
}

function removeChatMessage(messageElement) {
    if (messageElement && messageElement.parentNode) {
        messageElement.style.transition = 'all 0.3s ease-out';
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            messageElement.remove();
        }, 300);
    }
}

function generateDemoResponse(query) {
    const responses = {
        'nephio': {
            answer: 'Nephio 是一個基於 Kubernetes 的網路自動化平台，專為管理和自動化 5G 網路功能而設計。它提供了一個統一的框架來部署、配置和管理網路功能，支援多雲環境和邊緣計算場景。',
            responseTime: 1200
        },
        'o-ran': {
            answer: 'O-RAN (Open Radio Access Network) 是一個開放的無線接取網路架構，採用標準化介面和虛擬化技術。其核心架構包括 O-CU (Central Unit)、O-DU (Distributed Unit) 和 O-RU (Radio Unit)，支援多廠商互通和智能化控制。',
            responseTime: 1500
        },
        'deploy': {
            answer: '部署 Nephio 叢集需要以下步驟：1) 準備 Kubernetes 環境，2) 安裝 Nephio 管理平面，3) 配置網路拓撲，4) 部署網路功能包，5) 驗證部署狀態。建議使用 Helm Chart 或 Operator 進行自動化部署。',
            responseTime: 1800
        },
        'cu-du': {
            answer: 'O-RAN CU (Central Unit) 負責上層協議處理和控制功能，包括 RRC 和 PDCP 層處理。O-RAN DU (Distributed Unit) 負責下層協議處理，包括 RLC、MAC 和 PHY 上層功能。CU 可進一步分為 CU-CP (控制平面) 和 CU-UP (使用者平面)。',
            responseTime: 1400
        }
    };
    
    // Simple keyword matching
    const queryLower = query.toLowerCase();
    
    for (const [key, response] of Object.entries(responses)) {
        if (queryLower.includes(key) || queryLower.includes(key.replace('-', ' '))) {
            return response;
        }
    }
    
    // Default response
    return {
        answer: '感謝您的提問！這是一個關於 O-RAN 和 Nephio 技術的智能問答系統。我可以回答關於網路架構、部署方式、技術規格等各種問題。請嘗試更具體的問題，例如詢問 Nephio 的核心功能或 O-RAN 的架構特點。',
        responseTime: 1000
    };
}

function updateStats() {
    const queryCountElement = document.getElementById('queryCount');
    const avgTimeElement = document.getElementById('avgTime');
    
    if (queryCountElement) {
        queryCountElement.textContent = queryCount;
    }
    
    if (avgTimeElement) {
        const avgTime = queryCount > 0 ? Math.round(totalResponseTime / queryCount) : 0;
        avgTimeElement.textContent = avgTime + 'ms';
    }
}

// ===== Hero Typing Animation =====
function startHeroTypingAnimation() {
    const typingElements = document.querySelectorAll('.typing-indicator span');
    
    if (typingElements.length === 0) return;
    
    // Start typing animation after a delay
    setTimeout(() => {
        // Remove typing indicator and show response
        const assistantMessage = document.querySelector('.chat-message.assistant');
        if (assistantMessage) {
            const messageContent = assistantMessage.querySelector('.message-content');
            if (messageContent) {
                const response = 'Nephio 是一個基於 Kubernetes 的網路自動化平台，專為電信業者設計。它提供統一的管理介面來部署和管理 5G 網路功能，支援多雲環境和邊緣計算，讓網路營運更加智能化和自動化。';
                
                // Replace typing indicator with actual response
                messageContent.innerHTML = `<p>${response}</p>`;
            }
        }
    }, 3000);
}

// ===== Animations =====
function initializeAnimations() {
    // Intersection Observer for scroll animations
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
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.feature-card, .community-card, .step, .arch-layer');
    animateElements.forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });
    
    // Counter animation
    animateCounters();
    
    // Parallax effect for hero section
    initializeParallax();
}

function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = counter.textContent;
        const isNumeric = /^\d+/.test(target);
        
        if (!isNumeric) return;
        
        const finalValue = parseInt(target);
        let currentValue = 0;
        const increment = finalValue / 50;
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                counter.textContent = target; // Restore original format
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(currentValue).toString();
            }
        }, 40);
    });
}

function initializeParallax() {
    const hero = document.querySelector('.hero');
    if (!hero) return;
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallax = scrolled * 0.5;
        
        hero.style.transform = `translateY(${parallax}px)`;
    });
}

// ===== Theme Functions =====
function initializeTheme() {
    // Auto dark mode based on system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // Enable dark mode if system prefers it
        // document.body.classList.add('dark-mode');
    }
    
    // Listen for theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (e.matches) {
            // document.body.classList.add('dark-mode');
        } else {
            // document.body.classList.remove('dark-mode');
        }
    });
}

// ===== Utility Functions =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

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

// ===== Performance Optimizations =====
// Debounced scroll handler
const debouncedScrollHandler = debounce(() => {
    // Additional scroll handling if needed
}, 100);

window.addEventListener('scroll', debouncedScrollHandler);

// ===== Error Handling =====
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // You could send this to an analytics service
});

// ===== CSS Animation Classes =====
// Add CSS for scroll animations
const style = document.createElement('style');
style.textContent = `
    .animate-on-scroll {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease-out;
    }
    
    .animate-on-scroll.animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    .feature-card.animate-on-scroll {
        transition-delay: 0.2s;
    }
    
    .feature-card:nth-child(2).animate-on-scroll {
        transition-delay: 0.4s;
    }
    
    .feature-card:nth-child(3).animate-on-scroll {
        transition-delay: 0.6s;
    }
    
    .community-card.animate-on-scroll {
        transition-delay: 0.1s;
    }
    
    .community-card:nth-child(2).animate-on-scroll {
        transition-delay: 0.3s;
    }
    
    .community-card:nth-child(3).animate-on-scroll {
        transition-delay: 0.5s;
    }
    
    .community-card:nth-child(4).animate-on-scroll {
        transition-delay: 0.7s;
    }
    
    .step.animate-on-scroll {
        transition-delay: 0.2s;
    }
    
    .step:nth-child(2).animate-on-scroll {
        transition-delay: 0.4s;
    }
    
    .step:nth-child(3).animate-on-scroll {
        transition-delay: 0.6s;
    }
    
    @media (prefers-reduced-motion: reduce) {
        .animate-on-scroll {
            transition: none;
        }
    }
`;
document.head.appendChild(style);

// ===== SEO and Analytics Functions =====
function trackEvent(category, action, label) {
    // Google Analytics 4 event tracking
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            event_category: category,
            event_label: label
        });
    }
}

// Track demo interactions
function trackDemoUsage(query) {
    trackEvent('Demo', 'Query', query.substring(0, 50));
}

// Track navigation clicks
document.querySelectorAll('.navbar-item, .btn').forEach(link => {
    link.addEventListener('click', function() {
        const text = this.textContent.trim();
        trackEvent('Navigation', 'Click', text);
    });
});

// ===== Service Worker Registration =====
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// ===== Copy to Clipboard Function =====
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('已複製到剪貼簿');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('已複製到剪貼簿');
    }
}

// Add copy buttons to code blocks
document.querySelectorAll('.code-block').forEach(codeBlock => {
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.innerHTML = '📋 複製';
    copyBtn.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 4px;
        padding: 5px 10px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s;
    `;
    
    const pre = codeBlock.querySelector('pre');
    if (pre) {
        codeBlock.style.position = 'relative';
        codeBlock.appendChild(copyBtn);
        
        copyBtn.addEventListener('click', () => {
            copyToClipboard(pre.textContent);
            copyBtn.innerHTML = '✅ 已複製';
            setTimeout(() => {
                copyBtn.innerHTML = '📋 複製';
            }, 2000);
        });
        
        copyBtn.addEventListener('mouseenter', () => {
            copyBtn.style.background = 'rgba(255,255,255,0.2)';
        });
        
        copyBtn.addEventListener('mouseleave', () => {
            copyBtn.style.background = 'rgba(255,255,255,0.1)';
        });
    }
});

// ===== Toast Notification Function =====
function showToast(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });
    
    // Remove after duration
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ===== Keyboard Navigation =====
document.addEventListener('keydown', function(e) {
    // ESC to close mobile menu
    if (e.key === 'Escape') {
        const navMenu = document.querySelector('.navbar-menu');
        if (navMenu && navMenu.classList.contains('active')) {
            toggleMenu();
        }
    }
    
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const demoInput = document.getElementById('demoQuery');
        if (demoInput) {
            demoInput.focus();
        }
    }
});

// ===== Initialize Everything =====
console.log('🚀 O-RAN × Nephio RAG Website Loaded Successfully!');