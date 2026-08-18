// Cycling Performance Studio Lab - Main JavaScript Application
// Vanilla JS, no frameworks - matching domestique style

document.addEventListener('DOMContentLoaded', function() {

    // State management
    const state = {
        activeProfile: null,
        profiles: [],
        italianFormat: false
    };

    // Initialize from DOM
    function initState() {
        // Read Italian format preference
        state.italianFormat = document.getElementById('format-italian')?.checked || false;

        // Read active profile from data attribute
        const header = document.querySelector('header');
        if (header) {
            const active = header.dataset.activeProfile;
            if (active) state.activeProfile = active;
        }
    }

    // Profile management
    async function loadProfiles() {
        try {
            const resp = await fetch('/api/profiles');
            if (resp.ok) {
                const data = await resp.json();
                state.profiles = data.profiles || [];
                renderProfiles();
                updateActiveProfileDisplay();
            }
        } catch (err) {
            console.error('Failed to load profiles:', err);
        }
    }

    function renderProfiles() {
        const list = document.querySelector('.profiles-list');
        if (!list) return;

        if (state.profiles.length === 0) {
            list.innerHTML = '<li class="empty-state">Nessun profilo creato</li>';
            return;
        }

        list.innerHTML = state.profiles.map(pid => `
            <li class="profile-item" data-profile-id="${pid}">
                <span class="profile-color" style="background: ${getColor(pid)}"></span>
                <span class="profile-name">${pid.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
                ${pid === state.activeProfile ? '<span class="status-badge">Attivo</span>' : ''}
            </li>
        `).join('');
    }

    function getColor(pid) {
        const colors = ['#3498db', '#2ecc71', '#e67e22', '#9b59b6', '#e74c3c',
                       '#f1c40f', '#1abc9c', '#pink'];
        return colors[parseInt(pid.split('-').reduce((a, b) => a + b.charCodeAt(0), 0)) % 8];
    }

    function updateActiveProfileDisplay() {
        const el = document.getElementById('active-profile-name');
        if (el) {
            el.textContent = state.activeProfile ? state.activeProfile.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : 'Nessun profilo attivo';
        }
    }

    // Athlete form
    function initAthleteForm() {
        const form = document.getElementById('athlete-form');
        if (!form) return;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const data = {
                ftp: parseInt(document.getElementById('athlete-ftp').value) || 200,
                weight_kg: parseFloat(document.getElementById('athlete-weight').value) || 70,
                lthr: parseInt(document.getElementById('athlete-lthr').value) || 180,
                max_hr: parseInt(document.getElementById('athlete-max-hr').value) || 190
            };

            try {
                const resp = await fetch('/api/profiles/' + state.activeProfile + '/athlete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (resp.ok) {
                    showToast('Atleta salvato con successo');
                } else {
                    showToast('Errore salvataggio', 'error');
                }
            } catch (err) {
                console.error('Error:', err);
                showToast('Errore di rete', 'error');
            }
        });
    }

    // Toast notification
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%);
            background: var(--primary); color: white; padding: 0.75rem 1.25rem;
            border-radius: var(--radius); box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000; min-width: 200px;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    // Initialize
    initState();
    loadProfiles();
    initAthleteForm();
});