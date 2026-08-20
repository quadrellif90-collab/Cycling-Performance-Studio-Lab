// Cycling Performance Studio Lab - Complete Frontend Application
// Vanilla JS, no frameworks. Integrates all API endpoints.

window.CPSL = window.CPSL || {};
(function() {
    const state = {
        activeProfile: null,
        profiles: [],
        athlete: {},
        workouts: [],
        filteredWorkouts: [],
        currentFilter: 'all',
        injuries: []
    };

    // ─── API Helpers ──────────────────────────────────────────
    async function api(url, opts) {
        try {
            const r = await fetch(url, opts);
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return await r.json();
        } catch(e) { console.error('API error:', url, e); return null; }
    }
    async function apiPost(url, data) { return api(url, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)}); }

    // ─── Toast ────────────────────────────────────────────────
    function toast(msg, type='success') {
        const el = document.createElement('div');
        el.className = `toast ${type}`;
        el.textContent = msg;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 3000);
    }

    // ─── Modal ────────────────────────────────────────────────
    function openModal(id) { document.getElementById(id)?.classList.add('open'); }
    function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

    // ─── Profile Management ───────────────────────────────────
    async function loadProfiles() {
        const data = await api('/api/profiles');
        if (data) {
            state.profiles = data.profiles || [];
            state.activeProfile = data.active || null;
            renderProfileList();
            updateSidebar();
        }
    }

    function renderProfileList() {
        const grid = document.getElementById('profiles-grid');
        const list = document.getElementById('profile-list');
        const items = state.profiles.map(pid => `
            <div class="profile-card ${pid === state.activeProfile ? 'active' : ''}" onclick="CPSL.switchProfile('${pid}')">
                <div class="profile-avatar" style="background:${getColor(pid)}">${pid[0].toUpperCase()}</div>
                <div class="profile-info">
                    <div class="profile-name">${pid.replace(/-/g,' ').replace(/\b\w/g,l=>l.toUpperCase())}</div>
                    <div class="profile-sub">${pid === state.activeProfile ? 'Active' : ''}</div>
                </div>
            </div>
        `).join('');
        if (grid) grid.innerHTML = items || '<div class="empty-state"><p>No profiles yet</p></div>';
        if (list) list.innerHTML = state.profiles.length ? items : '<div class="empty-state"><p>No profiles</p></div>';
    }

    function updateSidebar() {
        const name = document.getElementById('sidebar-profile-name');
        const sub = document.getElementById('sidebar-profile-sub');
        const avatar = document.getElementById('sidebar-avatar');
        if (name) name.textContent = state.activeProfile ? state.activeProfile.replace(/-/g,' ').replace(/\b\w/g,l=>l.toUpperCase()) : 'No Profile';
        if (sub) sub.textContent = state.athlete.ftp ? `FTP: ${state.athlete.ftp}W` : 'FTP: --';
        if (avatar) avatar.textContent = state.activeProfile ? state.activeProfile[0].toUpperCase() : '?';
    }

    function getColor(pid) {
        const c = ['#3498db','#2ecc71','#e67e22','#9b59b6','#e74c3c','#f1c40f','#1abc9c','#e91e63'];
        let h = 0; for (let i=0; i<pid.length; i++) h = ((h<<5)-h)+pid.charCodeAt(i);
        return c[Math.abs(h) % c.length];
    }

    async function switchProfile(pid) {
        await apiPost('/api/profiles/switch', {profile_id: pid});
        state.activeProfile = pid;
        await loadProfiles();
        await loadAthlete();
        toast('Profile switched to ' + pid.replace(/-/g,' '));
        closeModal('profile-modal');
        location.reload();
    }

    async function createProfile() {
        const name = prompt('Profile name:');
        if (!name) return;
        const slug = name.toLowerCase().replace(/\s+/g,'-').replace(/[^a-z0-9-]/g,'');
        await apiPost('/api/profiles/create', {profile_id: slug});
        await switchProfile(slug);
    }

    function openProfilePicker() { loadProfiles(); openModal('profile-modal'); }

    // ─── Athlete ──────────────────────────────────────────────
    async function loadAthlete() {
        if (!state.activeProfile) return;
        const data = await api(`/api/profiles/${state.activeProfile}/athlete`);
        if (data) { state.athlete = data; updateSidebar(); }
    }

    async function saveAthlete() {
        const data = {
            ftp: parseInt(document.getElementById('athlete-ftp').value) || 0,
            weight_kg: parseFloat(document.getElementById('athlete-weight').value) || 0,
            lthr: parseInt(document.getElementById('athlete-lthr').value) || 0,
            max_hr: parseInt(document.getElementById('athlete-maxhr').value) || 0,
            wprime_j: (parseFloat(document.getElementById('athlete-wprime').value) || 0) * 1000,
            pmax: parseInt(document.getElementById('athlete-pmax').value) || 0
        };
        const r = await apiPost(`/api/profiles/${state.activeProfile}/athlete`, data);
        if (r && r.success !== false) { toast('Athlete data saved'); state.athlete = {...state.athlete, ...data}; updateSidebar(); }
        else toast('Error saving athlete', 'error');
    }

    // ─── Dashboard ────────────────────────────────────────────
    async function loadDashboard() {
        await loadProfiles();
        await loadAthlete();
        loadInjuries();
        computeFitness();
    }

    // ─── Fitness Signature ────────────────────────────────────
    async function computeFitness() {
        if (!state.athlete.ftp) return;
        const efforts = state.athlete.efforts || {300: state.athlete.ftp * 1.12, 600: state.athlete.ftp * 1.02, 1200: state.athlete.ftp * 0.95, 3600: state.athlete.ftp};
        const data = await apiPost('/api/fitness/signature', {efforts, ftp: state.athlete.ftp});
        if (data && data.success) {
            setBar('fs-ftp', data.ftp, 400);
            setBar('fs-ltp', data.ltp, 400);
            setBar('fs-hie', data.hie, 30);
            setBar('fs-pmax', data.peak_power, 1500);
        }
    }
    function setBar(prefix, val, max) {
        const bar = document.getElementById(prefix+'-bar');
        const v = document.getElementById(prefix+'-val');
        if (bar) bar.style.width = Math.min(100, (val/max)*100) + '%';
        if (v) v.textContent = Math.round(val);
    }

    // ─── Power Curve ──────────────────────────────────────────
    let powerChart = null;
    function refreshPowerCurve() {
        const ctx = document.getElementById('power-canvas');
        if (!ctx || typeof Chart === 'undefined') return;
        if (powerChart) powerChart.destroy();
        const ftp = state.athlete.ftp || 200;
        powerChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['5s','15s','30s','1m','2m','5m','10m','20m','60m'],
                datasets: [{
                    label: 'Best Power',
                    data: [ftp*1.8, ftp*1.5, ftp*1.35, ftp*1.2, ftp*1.12, ftp*1.05, ftp*1.0, ftp*0.97, ftp*0.92],
                    borderColor: '#4f9cf7',
                    backgroundColor: 'rgba(79,156,247,0.1)',
                    tension: 0.3, fill: true, pointRadius: 4, pointBackgroundColor: '#4f9cf7'
                },{
                    label: 'FTP',
                    data: Array(9).fill(ftp),
                    borderColor: '#ef4444', borderDash: [5,5], pointRadius: 0, borderWidth: 1
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#b8c8d8', font: {size:11} } } },
                scales: {
                    y: { grid: {color:'#2d3f52'}, ticks:{color:'#8a9bb0'}, title:{display:true,text:'Power (W)',color:'#8a9bb0'} },
                    x: { grid: {color:'#2d3f52'}, ticks:{color:'#8a9bb0'}, title:{display:true,text:'Duration',color:'#8a9bb0'} }
                }
            }
        });
    }

    // ─── Profile Page ─────────────────────────────────────────
    function loadProfile() {
        loadProfiles();
        loadAthlete().then(() => {
            loadInjuries();
            loadZones();
        });
    }

    function loadZones() {
        const ftp = state.athlete.ftp;
        const lthr = state.athlete.lthr;
        if (ftp) {
            const pzones = [
                {z:'Z1', name:'Active Recovery', pct:'<55%', range:`< ${Math.round(ftp*0.55)}W`},
                {z:'Z2', name:'Endurance', pct:'56-75%', range:`${Math.round(ftp*0.56)}-${Math.round(ftp*0.75)}W`},
                {z:'Z3', name:'Tempo', pct:'76-90%', range:`${Math.round(ftp*0.76)}-${Math.round(ftp*0.90)}W`},
                {z:'Z4', name:'Threshold', pct:'91-105%', range:`${Math.round(ftp*0.91)}-${Math.round(ftp*1.05)}W`},
                {z:'Z5', name:'VO2max', pct:'106-120%', range:`${Math.round(ftp*1.06)}-${Math.round(ftp*1.20)}W`},
                {z:'Z6', name:'Anaerobic', pct:'121-150%', range:`${Math.round(ftp*1.21)}-${Math.round(ftp*1.50)}W`},
                {z:'Z7', name:'Neuromuscular', pct:'>150%', range:`> ${Math.round(ftp*1.50)}W`}
            ];
            document.getElementById('power-zones-body').innerHTML = pzones.map(z =>
                `<tr><td><span class="badge b-${z.z==='Z4'?'good':z.z==='Z5'?'med':z.z==='Z6'?'low':'gold'}">${z.z}</span></td><td>${z.name}</td><td>${z.range}</td><td>${z.pct}</td></tr>`
            ).join('');
        }
        if (lthr) {
            const hzones = [
                {z:'Z1', name:'Active Recovery', pct:'<65%', range:`< ${Math.round(lthr*0.65)} bpm`},
                {z:'Z2', name:'Endurance', pct:'65-75%', range:`${Math.round(lthr*0.65)}-${Math.round(lthr*0.75)} bpm`},
                {z:'Z3', name:'Tempo', pct:'76-85%', range:`${Math.round(lthr*0.76)}-${Math.round(lthr*0.85)} bpm`},
                {z:'Z4', name:'Threshold', pct:'86-92%', range:`${Math.round(lthr*0.86)}-${Math.round(lthr*0.92)} bpm`},
                {z:'Z5', name:'VO2max', pct:'93-100%', range:`${Math.round(lthr*0.93)}-${lthr} bpm`},
                {z:'Z6', name:'Anaerobic', pct:'>100%', range:`> ${lthr} bpm`}
            ];
            document.getElementById('hr-zones-body').innerHTML = hzones.map(z =>
                `<tr><td><span class="badge b-${z.z==='Z4'?'good':z.z==='Z5'?'med':'gold'}">${z.z}</span></td><td>${z.name}</td><td>${z.range}</td><td>${z.pct}</td></tr>`
            ).join('');
        }
    }

    // ─── Workouts ─────────────────────────────────────────────
    async function loadWorkouts() {
        const data = await api('/api/workouts');
        if (data && data.workouts) {
            state.workouts = data.workouts;
            state.filteredWorkouts = data.workouts;
            renderWorkouts();
        } else {
            document.getElementById('workout-list').innerHTML = '<div class="empty-state"><p>No workouts available</p><p style="font-size:12px;color:var(--text3)">Add ZWO files to the workouts/ directory</p></div>';
        }
    }

    function renderWorkouts() {
        const list = document.getElementById('workout-list');
        const w = state.filteredWorkouts;
        document.getElementById('wl-total').textContent = w.length;
        document.getElementById('wl-count').textContent = `${w.length} workouts`;
        if (!w.length) { list.innerHTML = '<div class="empty-state"><p>No matching workouts</p></div>'; return; }
        list.innerHTML = w.map((wk, i) => {
            const cat = wk.category || 'endurance';
            const icon = {threshold:'⚡',vo2:'🔥',sweet_spot:'💚',endurance:'🚴',sprint:'💨',recovery:'🌿',tempo:'⏱️'}[cat] || '🚴';
            return `<div class="workout-item" onclick="CPSL.showWorkout(${i})">
                <div class="workout-icon wi-${cat}">${icon}</div>
                <div class="workout-info">
                    <div class="workout-title">${wk.name || wk.filename || 'Workout'}</div>
                    <div class="workout-meta">${wk.duration_min || '--'} min ${wk.avg_power ? '· '+wk.avg_power+'W' : ''}</div>
                    <div class="workout-tags">${wk.tags ? wk.tags.split(',').map(t=>'<span class="badge b-cat4">'+t.trim()+'</span>').join('') : ''}</div>
                </div>
            </div>`;
        }).join('');
    }

    function filterWorkouts(q) {
        q = q.toLowerCase();
        state.filteredWorkouts = state.workouts.filter(w => {
            const matchSearch = !q || (w.name||'').toLowerCase().includes(q) || (w.tags||'').toLowerCase().includes(q);
            const matchFilter = state.currentFilter === 'all' || (w.category||'') === state.currentFilter;
            return matchSearch && matchFilter;
        });
        renderWorkouts();
    }

    function setFilter(f) {
        state.currentFilter = f;
        document.querySelectorAll('#workout-filters .tab').forEach(t => t.classList.toggle('active', t.dataset.filter === f));
        filterWorkouts(document.getElementById('workout-search')?.value || '');
    }

    function showWorkout(i) {
        const w = state.filteredWorkouts[i];
        if (!w) return;
        document.getElementById('wm-title').textContent = w.name || w.filename || 'Workout';
        document.getElementById('wm-content').innerHTML = `
            <div style="font-size:13px; color:var(--text2); margin-bottom:12px">
                <p><strong>Duration:</strong> ${w.duration_min || '--'} min</p>
                <p><strong>Category:</strong> ${w.category || 'General'}</p>
                ${w.description ? '<p style="margin-top:8px">'+w.description+'</p>' : ''}
            </div>`;
        openModal('workout-modal');
    }

    // ─── Analytics ────────────────────────────────────────────
    async function loadAnalytics() {
        await loadAthlete();
        const a = state.athlete;
        if (a.ftp) document.getElementById('rp-ftp').textContent = a.ftp;
        if (a.ftp && a.weight_kg) document.getElementById('rp-wkg').textContent = (a.ftp/a.weight_kg).toFixed(2);
        if (a.pmax) document.getElementById('rp-pmax').textContent = a.pmax;

        // Load fitness signature
        const sig = await apiPost('/api/fitness/signature', {efforts:{300:a.ftp*1.12||280,600:a.ftp*1.02||250,1200:a.ftp*0.95||220}, ftp:a.ftp||209});
        if (sig && sig.success) {
            document.getElementById('rp-ltp').textContent = Math.round(sig.ltp);
            document.getElementById('rp-hie').textContent = (sig.hie/1000).toFixed(1);
            if (!a.pmax) document.getElementById('rp-pmax').textContent = Math.round(sig.peak_power);
        }

        // Load CP/W'
        const cp = await apiPost('/api/fitness/cp-wprime', {efforts:{300:a.ftp*1.12||280,600:a.ftp*1.02||250,1200:a.ftp*0.95||220}});
        if (cp && cp.success) {
            document.getElementById('rp-cp').textContent = Math.round(cp.cp);
            document.getElementById('rp-wprime').textContent = (cp.w_prime/1000).toFixed(1);
        }
        refreshPowerCurve();
        initAnalyticsCharts(sig, cp);
    }

    let fitnessChart = null, cpChart = null;
    function initAnalyticsCharts(sig, cp) {
        if (typeof Chart === 'undefined') return;
        const fctx = document.getElementById('fitness-canvas');
        if (fctx && sig && sig.success) {
            if (fitnessChart) fitnessChart.destroy();
            fitnessChart = new Chart(fctx, {
                type: 'bar',
                data: {
                    labels: ['FTP', 'LTP', 'HIE (kJ)', 'Pmax'],
                    datasets: [{data:[Math.round(sig.ftp), Math.round(sig.ltp), +(sig.hie/1000).toFixed(1), Math.round(sig.peak_power)],
                        backgroundColor:['#4f9cf7','#22c55e','#f97316','#ef4444'], borderRadius:6}]
                },
                options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}},
                    scales:{y:{grid:{color:'#2d3f52'},ticks:{color:'#8a9bb0'}},x:{grid:{display:false},ticks:{color:'#8a9bb0'}}} }
            });
        }
        const cctx = document.getElementById('cpwprime-canvas');
        if (cctx && cp && cp.success) {
            if (cpChart) cpChart.destroy();
            cpChart = new Chart(cctx, {
                type: 'bar',
                data: {
                    labels: ['Critical Power (W)', "W' (kJ)"],
                    datasets: [{data:[Math.round(cp.cp), +(cp.w_prime/1000).toFixed(1)],
                        backgroundColor:['#4f9cf7','#eab308'], borderRadius:6}]
                },
                options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}},
                    scales:{y:{grid:{color:'#2d3f52'},ticks:{color:'#8a9bb0'}},x:{grid:{display:false},ticks:{color:'#8a9bb0'}}} }
            });
            document.getElementById('cpwprime-details').innerHTML = `CP: <strong>${Math.round(cp.cp)}W</strong> · W': <strong>${(cp.w_prime/1000).toFixed(1)}kJ</strong>`;
        }
    }

    // ─── Injuries ─────────────────────────────────────────────
    async function loadInjuries() {
        const data = await api('/api/injuries');
        if (data) {
            state.injuries = data.active_injuries || [];
            renderInjuries('injury-list');
            renderInjuries('injuries-list');
        }
    }

    function renderInjuries(containerId) {
        const el = document.getElementById(containerId);
        if (!el) return;
        if (!state.injuries.length) { el.innerHTML = '<div class="empty-state" style="padding:16px"><p>No active injuries</p></div>'; return; }
        el.innerHTML = state.injuries.map(inj => `
            <div class="injury-item">
                <div class="injury-severity sev-${inj.severity}"></div>
                <div style="flex:1">
                    <div style="font-size:13px; font-weight:500">${inj.name}</div>
                    <div style="font-size:11px; color:var(--text3)">${inj.date_start} · ${inj.severity}</div>
                </div>
                <button class="btn btn-sm" onclick="CPSL.resolveInjury('${inj.injury_id}')">Resolve</button>
            </div>
        `).join('');
    }

    function showInjuryForm() { openModal('injury-modal'); }

    async function saveInjury() {
        const data = {
            name: document.getElementById('injury-name').value,
            date_start: document.getElementById('injury-date-start').value,
            severity: document.getElementById('injury-severity').value,
            notes: document.getElementById('injury-notes').value
        };
        const r = await apiPost('/api/injuries', data);
        if (r && r.success) { toast('Injury registered'); closeModal('injury-modal'); loadInjuries(); }
        else toast('Error registering injury', 'error');
    }

    async function resolveInjury(id) {
        await api(`/api/injuries/${id}/resolve`, {method:'POST'});
        toast('Injury resolved');
        loadInjuries();
    }

    // ─── BIA ──────────────────────────────────────────────────
    async function uploadBIA() {
        const input = document.getElementById('bia-upload');
        if (!input?.files[0]) { toast('Select a PDF file', 'error'); return; }
        const fd = new FormData();
        fd.append('file', input.files[0]);
        try {
            const r = await fetch('/api/bia/analyze', {method:'POST', body:fd});
            const data = await r.json();
            const el = document.getElementById('bia-result');
            el.style.display = 'block';
            el.textContent = JSON.stringify(data, null, 2);
        } catch(e) { toast('BIA analysis failed', 'error'); }
    }

    // ─── Settings ─────────────────────────────────────────────
    async function loadSettings() {
        loadProfiles();
    }

    async function testICU() {
        const id = document.getElementById('icu-athlete-id').value;
        const key = document.getElementById('icu-api-key').value;
        if (!id || !key) { toast('Enter Athlete ID and API Key', 'error'); return; }
        const r = await apiPost('/api/icu/test', {athlete_id: id, api_key: key});
        if (r && r.ok) { document.getElementById('icu-badge').className='badge b-gold'; document.getElementById('icu-badge').textContent='Connected'; document.getElementById('icu-info').textContent=r.name||''; toast('Connected!'); }
        else toast(r?.error || 'Connection failed', 'error');
    }

    async function saveICU() {
        const id = document.getElementById('icu-athlete-id').value;
        const key = document.getElementById('icu-api-key').value;
        await apiPost('/api/icu/save', {athlete_id: id, api_key: key});
        toast('ICU credentials saved');
    }

    async function syncICU() { toast('Syncing with Intervals.icu...'); await api('/api/icu/sync', {method:'POST'}); toast('Sync complete'); }
    async function exportBackup() { window.open('/api/export/backup'); }
    async function exportZIP() { window.open('/api/export/zip'); }
    async function exportMetrics() { window.open('/api/export/metrics'); }

    async function uploadGPX() {
        const input = document.getElementById('gpx-upload');
        if (!input?.files[0]) { toast('Select a GPX file', 'error'); return; }
        const fd = new FormData();
        fd.append('file', input.files[0]);
        try {
            const r = await fetch('/api/gpx/parse', {method:'POST', body:fd});
            const data = await r.json();
            const el = document.getElementById('gpx-result');
            el.style.display = 'block';
            el.innerHTML = `<strong>${data.filename||'GPX'}</strong><br>Distance: ${data.total_distance_km?.toFixed(1)||'--'} km<br>Elevation: ${data.total_elevation_gain_m?.toFixed(0)||'--'} m<br>Duration: ${data.duration_seconds ? Math.round(data.duration_seconds/60)+' min' : '--'}`;
        } catch(e) { toast('GPX parse failed', 'error'); }
    }

    // ─── Init ─────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function() {
        loadProfiles().then(() => loadAthlete());
    initAiCoachTab();        initAiCoachTab();
    });

    // ─── Public API ───────────────────────────────────────────────
    Object.assign(window.CPSL, {
        toast, openModal, closeModal,
        loadDashboard, loadProfile, loadAnalytics, loadWorkouts, loadSettings,
        loadProfiles, switchProfile, createProfile, openProfilePicker,
        saveAthlete, computeFitness, refreshPowerCurve, computeCpWprime: computeFitness,
        filterWorkouts, setFilter, showWorkout,
        showInjuryForm, saveInjury, resolveInjury,
        uploadBIA, testICU, saveICU, syncICU,
        exportBackup, exportZIP, exportMetrics, uploadGPX,
        toggleAiCoachChat, sendAiCoachMessage

    // AI Coach Tab ─────────────────────────────────────────────────
    async function initAiCoachTab() {
        const statusEl = document.getElementById('ai_coach_status');
        const chatEl = document.getElementById('ai_coach_chat');
        const formEl = document.getElementById('ai_coach_form');
        const loadingEl = document.getElementById('ai_coach_loading');
        
        if (!statusEl || !chatEl || !formEl || !loadingEl) return;
        
        try {
            const r = await api('/api/ai/status');
            if (r && r.ai_coach_enabled) {
                statusEl.textContent = 'AI Coach attivo';
                statusEl.style.color = 'var(--green)';
                chatEl.style.display = 'block';
                formEl.style.display = 'block';
            } else {
                statusEl.textContent = 'AI Coach disabilitato (flag OFF)';
                statusEl.style.color = 'var(--red)';
            }
        } catch(e) {
            statusEl.textContent = 'Errore stato AI Coach';
            statusEl.style.color = 'var(--red)';
        }
    }

    async function toggleAiCoachChat(show) {
        const chatEl = document.getElementById('ai_coach_chat');
        const formEl = document.getElementById('ai_coach_form');
        const loadingEl = document.getElementById('ai_coach_loading');
        const inputEl = document.getElementById('ai_coach_input');
        
        if (!chatEl || !formEl || !loadingEl || !inputEl) return;
        
        if (show) {
            chatEl.style.display = 'block';
            formEl.style.display = 'block';
            loadingEl.style.display = 'none';
            inputEl.disabled = false;
            inputEl.focus();
        } else {
            chatEl.style.display = 'none';
            formEl.style.display = 'none';
            loadingEl.style.display = 'none';
            inputEl.disabled = true;
            inputEl.value = '';
        }
    }

    async function sendAiCoachMessage() {
        const inputEl = document.getElementById('ai_coach_input');
        const chatEl = document.getElementById('ai_coach_chat');
        const statusEl = document.getElementById('ai_coach_status');
        const loadingEl = document.getElementById('ai_coach_loading');
        const formEl = document.getElementById('ai_coach_form');
        
        if (!inputEl || !chatEl || !statusEl || !loadingEl || !formEl) return;
        
        const message = inputEl.value.trim();
        if (!message) return;
        
        # Show loading state
        loadingEl.style.display = 'block';
        chatEl.style.display = 'none';
        formEl.style.display = 'none';
        
        try:
            const r = await apiPost('/api/ai/weekly-analysis', {rides: [], profile_data: {}});
            if (r && r.ok && r.analysis) {
                # Display analysis result
                let html = '<div class="activity">';
                html += `<div class="act-name"><strong>Analisi Settimanale</strong></div>`;
                html += `<div class="act-meta">${r.analysis.llm_analysis || 'Nessuna analisi disponibile'}</div>`;
                html += '</div>';
                chatEl.innerHTML += html;
            } else:
                toast(r?.error || 'Errore analysis', 'error');
        # catch(e):
            toast('Errore comunicazione AI', 'error');
        # finally:
            # Reset state
            loadingEl.style.display = 'none';
            chatEl.style.display = 'block';
            formEl.style.display = 'block';
            inputEl.value = '';
        }
    
    };
})();
