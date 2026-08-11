document.addEventListener("DOMContentLoaded", function() {
    const rootStyles = getComputedStyle(document.documentElement);
    const brandPrimary = rootStyles.getPropertyValue('--brand-primary').trim();
    const brandSecondary = rootStyles.getPropertyValue('--brand-secondary').trim();
    const brandAccent = rootStyles.getPropertyValue('--brand-accent').trim();
    const textMuted = rootStyles.getPropertyValue('--text-muted').trim();

    // Employee Status Chart
    const ctx1 = document.getElementById('employeeStatusChart')?.getContext('2d');
    if (ctx1 && window.employeeStatusData) {
        new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Inactive'],
                datasets: [{
                    data: window.employeeStatusData,
                    backgroundColor: [brandPrimary, textMuted],
                    borderWidth: 0
                }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    }

    // Hiring Trend Chart
    const ctx2 = document.getElementById('hiringTrendChart')?.getContext('2d');
    if (ctx2 && window.hiringTrendData) {
        new Chart(ctx2, {
            type: 'line',
            data: {
                labels: window.hiringTrendData.labels,
                datasets: [{
                    label: 'New Hires',
                    data: window.hiringTrendData.counts,
                    borderColor: brandSecondary,
                    backgroundColor: 'rgba(42, 210, 155, 0.2)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
    }

    // Employees per Department Chart
    const ctx3 = document.getElementById('employeesDeptChart')?.getContext('2d');
    if (ctx3 && window.employeesPerDeptData) {
        new Chart(ctx3, {
            type: 'bar',
            data: {
                labels: window.employeesPerDeptData.labels,
                datasets: [{
                    label: 'Employees',
                    data: window.employeesPerDeptData.counts,
                    backgroundColor: brandAccent
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
    }
});
