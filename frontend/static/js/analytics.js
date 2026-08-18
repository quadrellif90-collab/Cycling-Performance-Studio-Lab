// Cycling Performance Studio Lab - Analytics JavaScript
// Integrates PCC math modules with Chart.js visualizations

document.addEventListener('DOMContentLoaded', function() {

    // Chart instances
    const charts = {
        powerCurve: null,
        fitness: null,
        cpwprime: null
    };

    // Initialize charts
    function initCharts() {
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
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: true }
                    },
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
                        data: [0, 0, 0, 0], // Will be filled by API
                        backgroundColor: [
                            '#3498db',
                            '#2ecc71',
                            '#e67e22',
                            '#e91e63'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { title: { display: true, text: 'Value' } }
                    }
                }
            });
        }

        if (ctx3) {
            charts.cpwprime = new Chart(ctx3, {
                type: 'bar',
                data: {
                    labels: ['Critical Power', 'W\''],
                    datasets: [{
                        label: 'CP/W\' Analysis',
                        data: [0, 0], // Will be filled by API
                        backgroundColor: ['#3498db', '#e67e22']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { title: { display: true, text: 'Power (W) / Energy (J)' } }
                    }
                }
            });
        }
    }

    // Fetch fitness signature from API and update chart
    async function updateFitnessSignature() {
        try {
            const pm = window.CPSL_STATE?.activeProfile;
            if (!pm) return;

            const resp = await fetch('/api/fitness/signature', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    efforts: window.sampleEfforts || {300: 280, 600: 250, 1200: 220},
                    ftp: window.sampleFTP
                })
            });

            if (resp.ok) {
                const data = await resp.json();
                if (charts.fitness) {
                    charts.fitness.data.datasets[0].data = [
                        data.ftp,
                        data.ltp,
                        data.hie,
                        data.peak_power
                    ];
                    charts.fitness.update();
                }
            }
        } catch (err) {
            console.error('Failed to update fitness signature:', err);
        }
    }

    // Update CP/W' chart from API
    async function updateCpWprime() {
        try {
            const resp = await fetch('/api/fitness/cp-wprime', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    efforts: {300: 280, 600: 250, 1200: 220}
                })
            });

            if (resp.ok) {
                const data = await resp.json();
                if (charts.cpwprime) {
                    charts.cpwprime.data.datasets[0].data = [data.cp, data.w_prime];
                    charts.cpwprime.update();
                }
            }
        } catch (err) {
            console.error('Failed to update CP/W\' analysis:', err);
        }
    }

    // Initialize on DOM load
    initCharts();

    // Periodic refresh (every 30 seconds)
    setInterval(() => {
        if (window.location.pathname.includes('/analytics')) {
            updateFitnessSignature();
            updateCpWprime();
        }
    }, 30000);

    // Manual refresh buttons handled via inline onclick in HTML
});