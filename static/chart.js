const labels = dataFromFlask.map(d => d.skill_name);
const values = dataFromFlask.map(d => d.total_minutes);

const ctx = document.getElementById('skillChart').getContext('2d');
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'เวลาที่ใช้ (นาที)',
            data: values,
            backgroundColor: '#2d89ef'
        }]
    },
    options: {
        scales: { y: { beginAtZero: true } }
    }
});
