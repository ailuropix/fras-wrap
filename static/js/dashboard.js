// Initialize Chart.js
Plotly.setPlotConfig({
    responsive: true
});

// Fetch dashboard data
async function fetchDashboardData() {
    console.log('Fetching dashboard data...');
    try {
        const response = await fetch('/api/dashboard');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Dashboard data received:', data);
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Show error message to user
        document.getElementById('totalPublications').textContent = 'Error';
        document.getElementById('totalCitations').textContent = 'Error';
    }
}

// Update dashboard metrics
function updateDashboard(data) {
    console.log('Updating dashboard with data:', data);
    
    // Update metrics with explicit checks
    const totalPubsElement = document.getElementById('totalPublications');
    const totalCitesElement = document.getElementById('totalCitations');
    const lastUpdatedElement = document.getElementById('lastUpdated');
    const nextUpdateElement = document.getElementById('nextUpdate');
    
    if (totalPubsElement) {
        totalPubsElement.textContent = data.totalPublications || 0;
        console.log('Updated total publications to:', data.totalPublications);
    } else {
        console.error('totalPublications element not found');
    }
    
    if (totalCitesElement) {
        totalCitesElement.textContent = data.totalCitations || 0;
        console.log('Updated total citations to:', data.totalCitations);
    } else {
        console.error('totalCitations element not found');
    }
    
    if (lastUpdatedElement) {
        lastUpdatedElement.textContent = formatDate(data.lastUpdated);
    }
    
    if (nextUpdateElement) {
        nextUpdateElement.textContent = formatDate(data.nextUpdate);
    }

    // Update trend chart
    if (data.publicationTrends && data.publicationTrends.length > 0) {
        updateTrendChart(data.publicationTrends);
    } else {
        console.log('No publication trends data');
    }

    // Update top publications
    if (data.topPublications && data.topPublications.length > 0) {
        updateTopPublications(data.topPublications);
    } else {
        console.log('No top publications data');
    }
}

// Format date
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Update trend chart
function updateTrendChart(trends) {
    const years = trends.map(t => t.year);
    const counts = trends.map(t => t.count);
    const citations = trends.map(t => t.citations);

    const trace1 = {
        x: years,
        y: counts,
        name: 'Publications',
        type: 'bar'
    };

    const trace2 = {
        x: years,
        y: citations,
        name: 'Citations',
        type: 'scatter',
        yaxis: 'y2'
    };

    const layout = {
        title: 'Publications and Citations Over Time',
        yaxis: { title: 'Number of Publications' },
        yaxis2: {
            title: 'Number of Citations',
            overlaying: 'y',
            side: 'right'
        },
        margin: { l: 60, r: 60, t: 40, b: 40 },
        height: 400
    };

    Plotly.newPlot('trendChart', [trace1, trace2], layout);
}

// Update top publications
function updateTopPublications(publications) {
    const container = document.getElementById('topPublications');
    container.innerHTML = '';

    publications.forEach((pub, index) => {
        const publicationDiv = document.createElement('div');
        publicationDiv.className = 'publication-item';
        publicationDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="mb-0">${pub.title}</h5>
                    <small class="text-muted">${pub.journal} (${pub.year})</small>
                </div>
                <div>
                    <span class="badge bg-primary">${pub.citations} Citations</span>
                </div>
            </div>
        `;
        container.appendChild(publicationDiv);
    });
}

// Fetch data on page load and every 5 minutes
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, fetching dashboard data...');
    fetchDashboardData();
    setInterval(fetchDashboardData, 300000); // 5 minutes
});

// Also try to fetch data immediately when script loads
console.log('Dashboard script loaded');
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fetchDashboardData);
} else {
    // DOM is already loaded
    console.log('DOM already loaded, fetching data immediately');
    fetchDashboardData();
}
