function togglePassword(id, password, button) {
    const passwordField = document.getElementById("password-" + id);
    if (!passwordField) return;

    const isHidden = passwordField.innerText === "********";
    passwordField.classList.add('fade-text');

    setTimeout(() => {
        passwordField.innerText = isHidden ? password : "********";
        passwordField.classList.remove('fade-text');
    }, 100);

    if (button) {
        button.dataset.revealed = isHidden ? 'true' : 'false';
        const icon = button.querySelector('.show-icon');
        const label = button.querySelector('.show-label');
        if (icon) icon.textContent = isHidden ? '🙈' : '👁';
        if (label) label.textContent = isHidden ? 'Hide' : 'Show';
    }
}

async function copyPassword(id) {
    const passwordField = document.getElementById("password-" + id);
    if (!passwordField) return;
    const password = passwordField.getAttribute('data-password');

    if (!password) {
        showNotification('Unable to copy password.', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(password);
        showNotification('Password copied to clipboard.', 'success');
    } catch (error) {
        showNotification('Clipboard copy failed. Please try manually.', 'error');
    }
}

function applyTheme(theme) {
    const body = document.body;
    const toggle = document.getElementById('theme-toggle');
    body.classList.toggle('light-mode', theme === 'light');
    if (toggle) {
        toggle.textContent = theme === 'light' ? 'Dark mode' : 'Light mode';
    }
}

function toggleTheme() {
    const current = document.body.classList.contains('light-mode') ? 'light' : 'dark';
    const next = current === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', next);
    applyTheme(next);
}

function showNotification(message, type = 'info') {
    const wrapper = document.querySelector('.notification-wrapper');
    if (!wrapper) return;
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `<span>${message}</span><button type="button" class="notification-close" aria-label="Dismiss message">×</button>`;
    wrapper.appendChild(notification);
    initNotifications();
}

function closeNotification(button) {
    const notification = button.closest('.notification');
    if (!notification) return;
    notification.classList.add('notification-hidden');
    setTimeout(() => notification.remove(), 260);
}

function initNotifications() {
    document.querySelectorAll('.notification-close').forEach(button => {
        if (!button.dataset.bound) {
            button.addEventListener('click', () => closeNotification(button));
            button.dataset.bound = 'true';
        }
    });

    document.querySelectorAll('.notification').forEach(notification => {
        if (!notification.dataset.timeout) {
            notification.dataset.timeout = 'true';
            setTimeout(() => {
                notification.classList.add('notification-hidden');
                setTimeout(() => notification.remove(), 260);
            }, 5600);
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const savedTheme = localStorage.getItem('theme');
    const preferredTheme = savedTheme || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    applyTheme(preferredTheme);
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
        toggle.addEventListener('click', toggleTheme);
    }

    // Generator tabs
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchGeneratorTab(tabName);
        });
    });

    const lengthSlider = document.getElementById('password-length');
    const lengthValue = document.getElementById('length-value');
    const passwordField = document.getElementById('account_password');
    if (lengthSlider && lengthValue) {
        lengthSlider.addEventListener('input', event => lengthValue.textContent = event.target.value);
    }
    if (passwordField) {
        passwordField.addEventListener('input', event => analyzePassword(event.target.value));
        if (passwordField.value) analyzePassword(passwordField.value);
    }

    // Search and Filter functionality
    const searchInput = document.getElementById('password-search');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const passwordTable = document.getElementById('password-table');
    const resultCount = document.getElementById('result-count');

    if (searchInput && passwordTable) {
        // Real-time search
        searchInput.addEventListener('input', () => {
            filterTable();
        });

        // Filter buttons
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                filterTable();
            });
        });
    }

    initNotifications();
});

function switchGeneratorTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update content
    document.querySelectorAll('.generator-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-generator`);
    });
}

function generatePassword() {
    const length = parseInt(document.getElementById('password-length').value, 10);
    const upper = document.getElementById('generate-upper').checked;
    const lower = document.getElementById('generate-lower').checked;
    const numbers = document.getElementById('generate-numbers').checked;
    const symbols = document.getElementById('generate-symbols').checked;
    let characters = '';

    if (upper) characters += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (lower) characters += 'abcdefghijklmnopqrstuvwxyz';
    if (numbers) characters += '0123456789';
    if (symbols) characters += '!@#$%^&*()-_=+[]{}|;:,.<>?';

    if (!characters) {
        showNotification('Please select at least one character set to generate a password.', 'warning');
        return;
    }

    let password = '';
    const array = new Uint32Array(length);
    window.crypto.getRandomValues(array);
    for (let i = 0; i < length; i++) {
        password += characters[array[i] % characters.length];
    }

    const passwordField = document.getElementById('account_password');
    if (passwordField) {
        passwordField.type = 'text';
        passwordField.value = password;
        passwordField.focus();
        passwordField.setSelectionRange(0, password.length);
        analyzePassword(password);
        setTimeout(() => passwordField.type = 'password', 5000);
        showNotification('Secure password generated and filled in.', 'success');
    }
}

function generateSmartPassword() {
    const category = document.getElementById('website-category').value;
    const memorable = document.getElementById('smart-memorable').checked;
    const includeNumbers = document.getElementById('smart-numbers').checked;
    const includeSymbols = document.getElementById('smart-symbols').checked;
    const mixedCase = document.getElementById('smart-uppercase').checked;

    if (!category) {
        showNotification('Please select a website category first.', 'warning');
        return;
    }

    let password = '';

    if (memorable) {
        password = generateMemorablePassword(category, includeNumbers, includeSymbols, mixedCase);
    } else {
        password = generateSecurePassword(category, includeNumbers, includeSymbols, mixedCase);
    }

    const passwordField = document.getElementById('account_password');
    if (passwordField) {
        passwordField.type = 'text';
        passwordField.value = password;
        passwordField.focus();
        passwordField.setSelectionRange(0, password.length);
        analyzePassword(password);
        setTimeout(() => passwordField.type = 'password', 5000);
        showNotification('Smart password generated and filled in.', 'success');
    }
}

function generateMemorablePassword(category, includeNumbers, includeSymbols, mixedCase) {
    const categoryWords = {
        'banking': ['Bank', 'Money', 'Safe', 'Vault', 'Secure', 'Trust', 'Finance', 'Capital'],
        'social': ['Social', 'Friend', 'Connect', 'Share', 'Like', 'Post', 'Chat', 'Network'],
        'email': ['Mail', 'Inbox', 'Send', 'Letter', 'Message', 'Contact', 'Compose', 'Reply'],
        'shopping': ['Shop', 'Buy', 'Cart', 'Deal', 'Price', 'Store', 'Purchase', 'Order'],
        'work': ['Work', 'Office', 'Team', 'Project', 'Meet', 'Task', 'Report', 'Business'],
        'entertainment': ['Game', 'Play', 'Watch', 'Movie', 'Music', 'Fun', 'Stream', 'Enjoy'],
        'education': ['Learn', 'Study', 'Book', 'Class', 'School', 'Teach', 'Course', 'Grade'],
        'health': ['Health', 'Care', 'Well', 'Fit', 'Doctor', 'Medicine', 'Body', 'Life'],
        'government': ['Gov', 'Public', 'Service', 'State', 'Official', 'Admin', 'Record', 'Legal'],
        'other': ['Secure', 'Safe', 'Lock', 'Key', 'Access', 'Login', 'Account', 'User']
    };

    const words = categoryWords[category] || categoryWords['other'];
    const word1 = words[Math.floor(Math.random() * words.length)];
    const word2 = words[Math.floor(Math.random() * words.length)];

    let password = word1 + word2;

    // Add numbers
    if (includeNumbers) {
        const year = new Date().getFullYear();
        const numbers = ['2024', '2025', '2026', year.toString(), Math.floor(Math.random() * 9000 + 1000).toString()];
        password += numbers[Math.floor(Math.random() * numbers.length)];
    }

    // Add symbols
    if (includeSymbols) {
        const symbols = ['!', '@', '#', '$', '%', '&', '*'];
        password += symbols[Math.floor(Math.random() * symbols.length)];
    }

    // Apply mixed case
    if (mixedCase) {
        password = password.split('').map((char, index) => {
            return index % 2 === 0 ? char.toUpperCase() : char.toLowerCase();
        }).join('');
    }

    return password;
}

function generateSecurePassword(category, includeNumbers, includeSymbols, mixedCase) {
    const categoryThemes = {
        'banking': 'BANK',
        'social': 'SOCIAL',
        'email': 'MAIL',
        'shopping': 'SHOP',
        'work': 'WORK',
        'entertainment': 'FUN',
        'education': 'LEARN',
        'health': 'HEALTH',
        'government': 'GOV',
        'other': 'SECURE'
    };

    const theme = categoryThemes[category] || 'SECURE';
    let password = theme;

    // Add random characters
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    const numbers = '0123456789';
    const symbols = '!@#$%^&*';

    for (let i = 0; i < 8; i++) {
        let charSet = chars;
        if (includeNumbers && Math.random() < 0.3) charSet = numbers;
        if (includeSymbols && Math.random() < 0.2) charSet = symbols;
        password += charSet[Math.floor(Math.random() * charSet.length)];
    }

    // Apply mixed case if requested
    if (mixedCase) {
        password = password.split('').map(char => {
            return Math.random() < 0.5 ? char.toUpperCase() : char.toLowerCase();
        }).join('');
    }

    return password;
}

function estimateEntropy(password) {
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSymbol = /[^A-Za-z0-9]/.test(password);
    let alphabetSize = 0;
    if (hasUpper) alphabetSize += 26;
    if (hasLower) alphabetSize += 26;
    if (hasNumber) alphabetSize += 10;
    if (hasSymbol) alphabetSize += 32;
    if (password.includes(' ')) alphabetSize += 1;
    return password.length > 0 ? Math.round(password.length * Math.log2(alphabetSize || 1)) : 0;
}

function getAttackEstimate(entropy) {
    if (entropy < 28) return 'Instant';
    if (entropy < 36) return 'Seconds';
    if (entropy < 60) return 'Hours';
    if (entropy < 80) return 'Years';
    if (entropy < 100) return 'Decades';
    return 'Centuries';
}

function getStrengthGrade(score) {
    if (score < 25) return { label: 'Very weak', className: 'strength-weak' };
    if (score < 45) return { label: 'Weak', className: 'strength-fair' };
    if (score < 70) return { label: 'Fair', className: 'strength-fair' };
    if (score < 90) return { label: 'Strong', className: 'strength-strong' };
    return { label: 'Excellent', className: 'strength-excellent' };
}

function analyzePassword(password) {
    const length = password.length;
    const entropy = estimateEntropy(password);
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSymbol = /[^A-Za-z0-9]/.test(password);
    const variety = [hasUpper, hasLower, hasNumber, hasSymbol].filter(Boolean).length;

    let score = Math.round(entropy * 1.1);
    if (length >= 12) score += 8;
    if (length >= 16) score += 6;
    if (variety >= 3) score += 6;
    if (variety === 4) score += 8;
    if (length < 8) score -= 18;
    if (entropy < 20) score -= 12;
    score = Math.max(0, Math.min(score, 100));

    const attack = getAttackEstimate(entropy);
    const grade = getStrengthGrade(score);
    const recommendations = [];
    if (length < 12) recommendations.push('Use at least 12 characters.');
    if (!hasUpper) recommendations.push('Add uppercase letters.');
    if (!hasLower) recommendations.push('Add lowercase letters.');
    if (!hasNumber) recommendations.push('Add numbers.');
    if (!hasSymbol) recommendations.push('Add special characters.');
    if (recommendations.length === 0) recommendations.push('Your password is strong. Use a unique password for each account.');

    updateStrengthUI({ score, entropy, attack, grade, recommendations });
}

function updateStrengthUI({ score, entropy, attack, grade, recommendations }) {
    const strengthBar = document.getElementById('strength-bar');
    const strengthGrade = document.getElementById('strength-grade');
    const entropyValue = document.getElementById('entropy-value');
    const attackValue = document.getElementById('attack-value');
    const recommendationsNode = document.getElementById('recommendations');
    if (strengthBar) {
        strengthBar.style.width = `${score}%`;
        if (score < 35) {
            strengthBar.style.background = '#ff6b6b';
        } else if (score < 55) {
            strengthBar.style.background = '#ffb703';
        } else if (score < 75) {
            strengthBar.style.background = '#64b5ff';
        } else {
            strengthBar.style.background = '#20c997';
        }
    }
    if (strengthGrade) {
        strengthGrade.textContent = grade.label;
        strengthGrade.className = `strength-pill ${grade.className}`;
    }
    if (entropyValue) entropyValue.textContent = `${entropy} bits`;
    if (attackValue) attackValue.textContent = attack;
    if (recommendationsNode) recommendationsNode.textContent = recommendations.join(' ');
}

function filterTable() {
    const searchInput = document.getElementById('password-search');
    const passwordTable = document.getElementById('password-table');
    const resultCount = document.getElementById('result-count');
    const tableScroll = document.querySelector('.table-scroll');

    if (!searchInput || !passwordTable) return;

    const searchTerm = searchInput.value.toLowerCase().trim();
    const activeFilter = document.querySelector('.filter-btn.active').dataset.filter;
    const rows = passwordTable.querySelectorAll('tbody tr');
    let visibleCount = 0;

    // Remove existing no-results message
    const existingNoResults = tableScroll.querySelector('.no-results');
    if (existingNoResults) {
        existingNoResults.remove();
    }

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length < 7) return; // Skip if not enough cells

        const website = cells[0].textContent.toLowerCase();
        const category = cells[1].textContent.toLowerCase();
        const username = cells[2].textContent.toLowerCase();
        const riskBadge = cells[4].querySelector('.risk-badge');
        const breachBadge = cells[5].querySelector('.badge');

        // Get risk level from badge class
        let riskLevel = 'excellent'; // default
        if (riskBadge) {
            const classes = riskBadge.className.split(' ');
            const riskClass = classes.find(cls => cls.startsWith('risk-'));
            if (riskClass) {
                riskLevel = riskClass.replace('risk-', '');
            }
        }

        // Get breach status
        let isBreached = false;
        if (breachBadge) {
            isBreached = breachBadge.classList.contains('badge-breach');
        }

        // Check search term match
        const matchesSearch = !searchTerm ||
            website.includes(searchTerm) ||
            category.includes(searchTerm) ||
            username.includes(searchTerm);

        // Check filter match
        let matchesFilter = true;
        switch (activeFilter) {
            case 'critical':
                matchesFilter = riskLevel === 'critical';
                break;
            case 'high':
                matchesFilter = riskLevel === 'high';
                break;
            case 'medium':
                matchesFilter = riskLevel === 'medium';
                break;
            case 'low':
                matchesFilter = riskLevel === 'low';
                break;
            case 'breached':
                matchesFilter = isBreached;
                break;
            case 'all':
            default:
                matchesFilter = true;
                break;
        }

        // Show/hide row
        if (matchesSearch && matchesFilter) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });

    // Update result count
    if (resultCount) {
        if (searchTerm || activeFilter !== 'all') {
            resultCount.textContent = `Showing ${visibleCount} of ${rows.length} entries`;
        } else {
            resultCount.textContent = `Showing all ${rows.length} entries`;
        }
    }

    // Show no results message if needed
    if (visibleCount === 0) {
        const noResults = document.createElement('div');
        noResults.className = 'no-results';
        noResults.innerHTML = `
            <h3>No matching entries found</h3>
            <p>Try adjusting your search terms or filter criteria.</p>
        `;
        tableScroll.appendChild(noResults);
        passwordTable.classList.add('table-hidden');
    } else {
        passwordTable.classList.remove('table-hidden');
    }
}

// Export functionality
document.addEventListener('DOMContentLoaded', function() {
    const exportButtons = document.querySelectorAll('.export-btn');
    const exportPasswordInput = document.getElementById('export-password');

    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const format = this.getAttribute('data-format');
            const password = exportPasswordInput.value.trim();

            if (!password) {
                alert('Please enter an export password to protect your data.');
                exportPasswordInput.focus();
                return;
            }

            if (password.length < 8) {
                alert('Export password must be at least 8 characters long.');
                exportPasswordInput.focus();
                return;
            }

            // Create a form to submit the export request
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/export/${format}`;

            // Add the password field
            const passwordField = document.createElement('input');
            passwordField.type = 'hidden';
            passwordField.name = 'export_password';
            passwordField.value = password;
            form.appendChild(passwordField);

            // Submit the form
            document.body.appendChild(form);
            form.submit();
            document.body.removeChild(form);

            // Clear the password field for security
            exportPasswordInput.value = '';
        });
    });
});
