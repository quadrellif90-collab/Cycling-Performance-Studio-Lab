// Cycling Performance Studio Lab - Analytics JavaScript
// Integrates PCC math modules with Chart.js visualizations

window.CPSL = window.CPSL || {};

(function() {
    const charts = {
        powerCurve: null,
        fitness: null,
        cpwprime: null
    };

    function initCharts() {
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded');
            return;
        }

        const ctx1 = document.getElementById('power-canvas');
        const ctx2 = document.getElementById('fitness-canvas');
        const ctx3 = document.getElementById('cpwprime-canvas');

        if (ctx1) {
            charts.powerCurve = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: [5, 30, 60, 180, 600, 1200],
                    datasets: [{
                        label: 'Power Curve',
                        data: [320, 280, 250, 200, 180, 150],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 235, 0.1)',
                        tension: 0.2,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Power (W)' } },
                        x: { title: { display: true, text: 'Duration (s)' } }
                    }
                }
            });
        }

        if (ctx2) {
            charts.fitness = new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: ['FTP', 'LTP', 'HIE', 'Pmax'],
                    datasets: [{
                        label: 'Fitness Signature',
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#3498db', '#2ecc71', '#e67e22', '#e91e63']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { y: { title: { display: true, text: 'Value' } } }
                }
            });
        }

        if (ctx3) {
            charts.cpwprime = new Chart(ctx3, {
                type: 'bar',
                data: {
                    labels: ['Critical Power', "W'"],
                    datasets: [{
                        label: "CP/W' Analysis",
                        data: [0, 0],
                        backgroundColor: ['#3498db', '#e67e22']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { y: { title: { display: true, text: 'Power (W) / Energy (J)' } } }
                }
            });
        }
    }

    async function updateFitnessSig() {
        try {
            const efforts = window.CPSL.sampleEfforts || {300: 280, 600: 250, 1200: 220};
            const ftp = window.CPSL.sampleFTP || 209;
            const resp = await fetch('/api/fitness/signature', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ efforts: efforts, ftp: ftp })
            });
            if (resp.ok) {
                const data = await resp.json();
                if (data.success && charts.fitness) {
                    charts.fitness.data.datasets[0].data = [data.ftp, data.ltp, data.hie, data.peak_power];
                    charts.fitness.update();
                }
                window.CPSL.fitnessData = data;
            }
        } catch (err) {
            console.error('Failed to update fitness signature:', err);
        }
    }

    async function updateCpwprime() {
        try {
            const efforts = window.CPSL.sampleEfforts || {300: 280, 600: 250, 1200: 220};
            const resp = await fetch('/api/fitness/cp-wprime', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ efforts: efforts })
            });
            if (resp.ok) {
                const data = await resp.json();
                if (data.success && charts.cpwprime) {
                    charts.cpwprime.data.datasets[0].data = [data.cp, data.w_prime];
                    charts.cpwprime.update();
                }
                window.CPSL.cpwprimeData = data;
            }
        } catch (err) {
            console.error("Failed to update CP/W' analysis:", err);
        }
    }

    function refreshPowerCurve() {
        if (charts.powerCurve) {
            charts.powerCurve.data.datasets[0].data = [320, 280, 250, 200, 180, 150];
            charts.powerCurve.update();
        }
    }

    async function openInjuryManager() {
        try {
            const resp = await fetch('/api/injuries');
            if (resp.ok) {
                const data = await resp.json();
                alert(JSON.stringify(data.summary, null, 2));
            }
        } catch (err) {
            console.error('Failed to load injuries:', err);
        }
    }

    async function uploadBIA() {
        const input = document.getElementById('bia-upload');
        if (!input || !input.files[0]) {
            alert('Seleziona un file PDF');
            return;
        }
        const formData = new FormData();
        formData.append('file', input.files[0]);
        try {
            const resp = await fetch('/api/bia/analyze', { method: 'POST', body: formData });
            const data = await resp.json();
            const resultEl = document.getElementById('bia-result');
            const msgEl = document.getElementById('bia-msg');
            if (resultEl && msgEl) {
                resultEl.classList.remove('hidden');
                msgEl.textContent = JSON.stringify(data, null, 2);
            }
        } catch (err) {
            console.error('BIA upload failed:', err);
        }
    }

    window.CPSL.updateFitnessSig = updateFitnessSig;
    window.CPSL.updateCpwprime = updateCpwprime;
    window.CPSL.refreshPowerCurve = refreshPowerCurve;
    window.CPSL.openInjuryManager = openInjuryManager;
    window.CPSL.uploadBIA = uploadBIA;
    window.CPSL.sampleEfforts = {300: 280, 600: 250, 1200: 220};
    window.CPSL.sampleFTP = 209;

    document.addEventListener('DOMContentLoaded', function() {
        initCharts();
        updateFitnessSig();
        updateCpwprime();
    });
})();
