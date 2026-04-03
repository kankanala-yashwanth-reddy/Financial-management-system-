/**
 * Finance Management System - Interactive Dashboard App (Dynamic Portfolio Edition)
 * Handles dynamic portfolio calculations, animations, and backend API integration
 */

class DashboardApp {
    constructor() {
        this.userId = null;
        this.currentChart = null;
        
        // Define risk profiles with dynamic asset allocations
        this.riskProfiles = {
            'Low': {
                colors: {
                    primary: '#10B981',
                    badge: '#10b981',
                    badgeBg: 'rgba(16, 185, 129, 0.1)'
                },
                assets: [
                    {
                        name: 'Government Bonds & Fixed Income',
                        percentage: 60,
                        description: 'Low-risk fixed income securities',
                        color: '#0F766E',
                        icon: '📋'
                    },
                    {
                        name: 'Blue-Chip Index Funds',
                        percentage: 30,
                        description: 'Established large-cap companies',
                        color: '#14B8A6',
                        icon: '📊'
                    },
                    {
                        name: 'Gold & Cash Equivalents',
                        percentage: 10,
                        description: 'Safe-haven assets and liquidity',
                        color: '#2DD4BF',
                        icon: '💰'
                    }
                ],
                strategy: 'Conservative approach focused on capital preservation with minimal volatility'
            },
            'Medium': {
                colors: {
                    primary: '#F59E0B',
                    badge: '#f59e0b',
                    badgeBg: 'rgba(245, 158, 11, 0.1)'
                },
                assets: [
                    {
                        name: 'Broad Market Equities',
                        percentage: 50,
                        description: 'Diversified stock portfolios',
                        color: '#3B82F6',
                        icon: '📈'
                    },
                    {
                        name: 'Corporate Bonds',
                        percentage: 30,
                        description: 'Mixed corporate debt securities',
                        color: '#7C3AED',
                        icon: '📑'
                    },
                    {
                        name: 'Real Estate (REITs)',
                        percentage: 10,
                        description: 'Real estate investment trusts',
                        color: '#EC4899',
                        icon: '🏢'
                    },
                    {
                        name: 'Digital Assets (Crypto)',
                        percentage: 10,
                        description: 'Cryptocurrencies and digital tokens',
                        color: '#F97316',
                        icon: '₿'
                    }
                ],
                strategy: 'Balanced portfolio with moderate growth potential and diversified risk exposure'
            },
            'High': {
                colors: {
                    primary: '#EF4444',
                    badge: '#ef4444',
                    badgeBg: 'rgba(239, 68, 68, 0.1)'
                },
                assets: [
                    {
                        name: 'Growth Stocks & Tech Equities',
                        percentage: 70,
                        description: 'High-growth and technology companies',
                        color: '#0EA5E9',
                        icon: '🚀'
                    },
                    {
                        name: 'Digital Assets & Web3 (Crypto)',
                        percentage: 20,
                        description: 'Emerging digital currencies and blockchain',
                        color: '#A855F7',
                        icon: '💻'
                    },
                    {
                        name: 'Venture / High-Yield Bonds',
                        percentage: 10,
                        description: 'High-yield and venture opportunities',
                        color: '#EF4444',
                        icon: '⚡'
                    }
                ],
                strategy: 'Aggressive growth strategy with higher risk tolerance for maximum returns'
            }
        };

        this.init();
    }

    init() {
        // Check authentication
        this.userId = fmsStorage.getUserId();
        if (!this.userId) {
            window.location.replace('login.html');
            return;
        }

        // Setup event listeners
        this.setupEventListeners();

        // Animate initial load
        this.animateInitialLoad();
    }

    setupEventListeners() {
        const calculateBtn = document.getElementById('calculateBtn');
        const savingsInput = document.getElementById('savingsInput');
        const logoutBtn = document.getElementById('logout-btn');

        calculateBtn.addEventListener('click', () => this.handleCalculate());
        savingsInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleCalculate();
        });
        logoutBtn.addEventListener('click', () => {
            fmsStorage.clear();
        });

        // Input validation
        savingsInput.addEventListener('input', (e) => {
            if (e.target.value < 0) e.target.value = 0;
        });
    }

    animateInitialLoad() {
        const elements = document.querySelectorAll('.fade-in-up');
        elements.forEach((el, index) => {
            const delay = index * 0.1;
            el.style.animationDelay = `${delay}s`;
        });
    }

    async handleCalculate() {
        const savingsAmount = parseFloat(document.getElementById('savingsInput').value);

        if (!savingsAmount || savingsAmount <= 0) {
            alert('Please enter a valid savings amount');
            return;
        }

        this.showLoadingState();

        try {
            const response = await fetch('http://127.0.0.1:8000/dashboard_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    savings_amount: savingsAmount
                })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();
            this.displayResults(data);

        } catch (error) {
            console.error('Error fetching portfolio data:', error);
            alert('Failed to calculate portfolio. Please try again.');
        } finally {
            this.hideLoadingState();
        }
    }

    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        const emptyState = document.getElementById('emptyState');

        emptyState.classList.add('hidden');
        resultsSection.classList.remove('hidden');

        // Get risk profile
        const riskLevel = data.risk_level;
        const profile = this.riskProfiles[riskLevel] || this.riskProfiles['Medium'];

        // Update risk badge
        this.updateRiskBadge(riskLevel, profile);

        // Generate dynamic assets grid
        this.generateAssetCards(data, profile);

        // Create donut chart
        this.createDonutChart(profile);

        // Update investment guide
        this.updateInvestmentGuide(profile);

        // Update summary
        this.updateSummary(data.savings_amount);

        setTimeout(() => {
            document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    }

    updateRiskBadge(riskLevel, profile) {
        const badge = document.getElementById('riskValue');
        badge.textContent = riskLevel;
        badge.style.background = profile.colors.badgeBg;
        badge.style.color = profile.colors.badge;
    }

    generateAssetCards(data, profile) {
        const assetsGrid = document.getElementById('assetsGrid');
        assetsGrid.innerHTML = '';

        // Set grid class based on number of assets
        const numAssets = profile.assets.length;
        assetsGrid.classList.remove('grid-3', 'grid-4');
        assetsGrid.classList.add(`grid-${numAssets}`);

        profile.assets.forEach((asset, index) => {
            const amount = (data.savings_amount * asset.percentage) / 100;
            const card = this.createAssetCard(asset, amount, index);
            assetsGrid.appendChild(card);
        });
    }

    createAssetCard(asset, amount, index) {
        const card = document.createElement('div');
        card.className = 'asset-card';
        card.style.animationDelay = `${index * 0.1}s`;

        const iconGradient = this.generateIconGradient(asset.color);

        card.innerHTML = `
            <div class="asset-header">
                <div class="asset-icon" style="background: ${iconGradient};">
                    <span style="font-size: 24px;">​${asset.icon}</span>
                </div>
                <h3 class="asset-name">${asset.name}</h3>
            </div>
            <div class="asset-body">
                <div class="asset-stat">
                    <span class="stat-label">Percentage</span>
                    <span class="stat-value" style="color: ${asset.color};">${asset.percentage}%</span>
                </div>
                <div class="asset-stat">
                    <span class="stat-label">Amount</span>
                    <span class="stat-amount">${this.formatCurrency(amount)}</span>
                </div>
            </div>
            <div class="asset-footer">
                <p class="asset-description">${asset.description}</p>
            </div>
        `;

        return card;
    }

    generateIconGradient(baseColor) {
        // Generate a lighter shade for gradient
        return `linear-gradient(135deg, ${baseColor}, ${this.lightenColor(baseColor, 20)})`;
    }

    lightenColor(color, percent) {
        const num = parseInt(color.replace("#",""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R<255?R<1?0:R:255)*0x10000 +
            (G<255?G<1?0:G:255)*0x100 +
            (B<255?B<1?0:B:255))
            .toString(16).slice(1);
    }

    createDonutChart(profile) {
        const ctx = document.getElementById('donutChart').getContext('2d');

        if (this.currentChart) {
            this.currentChart.destroy();
        }

        const labels = profile.assets.map(a => a.name);
        const data = profile.assets.map(a => a.percentage);
        const colors = profile.assets.map(a => a.color);

        this.currentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderColor: '#FFFFFF',
                    borderWidth: 3,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 13 },
                        displayColors: true,
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    updateInvestmentGuide(profile) {
        const guideContent = document.getElementById('guideContent');
        guideContent.innerHTML = '';

        let html = `<div class="guide-item">
            <div class="guide-item-title">Strategy</div>
            <div class="guide-item-text">${profile.strategy}</div>
        </div>`;

        profile.assets.forEach(asset => {
            html += `<div class="guide-item">
                <div class="guide-item-title">${asset.name}</div>
                <div class="guide-item-text">${asset.percentage}% - ${asset.description}</div>
            </div>`;
        });

        guideContent.innerHTML = html;

        const items = guideContent.querySelectorAll('.guide-item');
        items.forEach((item, index) => {
            item.style.animation = `slideUpFadeIn 0.5s ease-out ${0.3 + index * 0.1}s forwards`;
            item.style.opacity = '0';
        });
    }

    updateSummary(amount) {
        const summaryAmount = document.getElementById('summaryAmount');
        this.animateMoneyTicker(summaryAmount, amount);
    }

    animateMoneyTicker(element, endValue) {
        const duration = 1500;
        const startValue = 0;
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = startValue + (endValue - startValue) * easeOut;
            element.textContent = this.formatCurrency(currentValue);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    formatCurrency(amount) {
        return '₹' + amount.toLocaleString('en-IN', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    }

    showLoadingState() {
        const btn = document.getElementById('calculateBtn');
        const btnText = btn.querySelector('.btn-text');
        const btnSpinner = btn.querySelector('.btn-spinner');
        const input = document.getElementById('savingsInput');

        btn.disabled = true;
        input.disabled = true;
        btnText.style.display = 'none';
        btnSpinner.classList.remove('hidden');
    }

    hideLoadingState() {
        const btn = document.getElementById('calculateBtn');
        const btnText = btn.querySelector('.btn-text');
        const btnSpinner = btn.querySelector('.btn-spinner');
        const input = document.getElementById('savingsInput');

        btn.disabled = false;
        input.disabled = false;
        btnText.style.display = 'inline-block';
        btnSpinner.classList.add('hidden');
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new DashboardApp();
});
