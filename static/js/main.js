document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchResults = document.getElementById('searchResults');

    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const college = document.getElementById('college').value;
        const facultyName = document.getElementById('facultyName').value;
        const department = document.getElementById('department').value;

        if (!college || !facultyName || !department) {
            alert('Please select college and enter both faculty name and department');
            return;
        }

        searchResults.style.display = 'block';
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    college: college,
                    name: facultyName,
                    department: department
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                // Redirect to faculty-specific results page
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    // Fallback to faculty results page using faculty_id
                    window.location.href = `/faculty/${data.faculty_id}`;
                }
            } else {
                alert(`Error searching publications: ${data.message || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while searching');
        }
    });
});
