// === User Roles Distribution ===
const rolesCtx = document.getElementById('rolesChart').getContext('2d');
const rolesChart = new Chart(rolesCtx, {
    type: 'doughnut',
    data: {
        labels: userRolesLabels,
        datasets: [{
            label: 'User Roles',
            data: userRolesData,
            backgroundColor: ['#16a085','#2980b9','#8e44ad','#c0392b','#f39c12','#2c3e50'],
            borderColor: '#fff',
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } }
    }
});

// === User Activity Chart ===
const activityCtx = document.getElementById('activityChart').getContext('2d');
const activityChart = new Chart(activityCtx, {
    type: 'line',
    data: {
        labels: activityDates,
        datasets: [{
            label: 'Active Users',
            data: activityCounts,
            backgroundColor: 'rgba(52, 152, 219, 0.2)',
            borderColor: '#2980b9',
            fill: true,
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { display: true, position: 'top' } },
        scales: { y: { beginAtZero: true } }
    }
});
