// Search form initialization
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('.search-form form');
    const keywordInput = searchForm?.querySelector('input[name="keyword"]');
    const locationInput = searchForm?.querySelector('input[name="location"]');
    const jobsList = document.querySelector('.jobs-list');
    const searchButton = searchForm?.querySelector('button[type="submit"]');
    let keywordTimeoutId;
    let locationTimeoutId;

    // Set initial button state
    const originalButtonText = searchButton?.innerHTML || '<span class="material-symbols-outlined">search</span>';

    // Initialize input values from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    if (keywordInput && urlParams.has('keyword')) {
        keywordInput.value = urlParams.get('keyword');
    }
    if (locationInput && urlParams.has('location')) {
        locationInput.value = urlParams.get('location');
    }

    // Handle real-time search for keyword input
    if (keywordInput) {
        keywordInput.addEventListener('input', (e) => {
            clearTimeout(keywordTimeoutId);
            keywordTimeoutId = setTimeout(() => handleRealTimeSearch(), 300);
        });
    }

    // Handle real-time search for location input
    if (locationInput) {
        locationInput.addEventListener('input', (e) => {
            clearTimeout(locationTimeoutId);
            locationTimeoutId = setTimeout(() => handleRealTimeSearch(), 300);
        });
    }

    // Handle form submission
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleRealTimeSearch(true);
        });
    }

    function handleRealTimeSearch(isFormSubmit = false) {
        const keyword = keywordInput?.value || '';
        const location = locationInput?.value || '';

        // Only search if we have at least 2 characters in either field
        if (!isFormSubmit && keyword.length < 2 && location.length < 2) {
            return;
        }

        // Update button state
        if (searchButton) {
            searchButton.disabled = true;
            searchButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
        }

        // Build search URL
        const searchParams = new URLSearchParams();
        if (keyword) searchParams.set('keyword', keyword);
        if (location) searchParams.set('location', location);
        
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        
        // Perform search
        fetch(`/search/?${searchParams.toString()}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (jobsList && data.html) {
                    jobsList.innerHTML = data.html;

                    // Update URL without page reload if this was a form submission
                    if (isFormSubmit) {
                        const newUrl = `${window.location.pathname}?${searchParams.toString()}`;
                        window.history.pushState({ path: newUrl }, '', newUrl);
                    }
                }
            })
            .catch(error => {
                console.error('Search error:', error);
                // Show error message to user
                if (jobsList) {
                    jobsList.innerHTML = `
                        <div class="no-results">
                            <h3>Search Error</h3>
                            <p>Sorry, something went wrong with the search. Please try again.</p>
                        </div>
                    `;
                }
            })
            .finally(() => {
                // Reset button state
                if (searchButton) {
                    searchButton.disabled = false;
                    searchButton.innerHTML = originalButtonText;
                }
            });
    }

    // Add clear search functionality
    const clearSearch = document.querySelector('.clear-search');
    if (clearSearch) {
        clearSearch.addEventListener('click', (e) => {
            e.preventDefault();
            if (keywordInput) keywordInput.value = '';
            if (locationInput) locationInput.value = '';
            window.location.href = window.location.pathname;
        });
    }
    
    // Helper function to get cookie by name (for CSRF token)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
