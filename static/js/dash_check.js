// dash_check.js - Ensures dashbase-root exists, otherwise reloads page
(function() {
    // Mobile browser special handling (entire code block)
    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {

        // Check if dashbase-root element exists
        const dashbaseRoot = document.getElementById('dashbase-root');

        // If element doesn't exist OR is still hidden after 1 second (safety check) || (window.getComputedStyle(dashbaseRoot).display === 'none')
        if (!dashbaseRoot) {
            console.warn('Dashbase root missing or hidden on mobile - forcing reload');

            // Try standard reload first
            try {
                window.location.reload(true);
            } catch(e) {
                // Fallback for browsers that block location.reload()
                window.location.href = window.location.href + '?forceReload=' + Date.now();
            }

            // Additional protection for stubborn cases
            setTimeout(() => {
                if (!document.getElementById('dashbase-root')) {
                    window.location.assign(window.location.href);
                }
            }, 500);
        }

        document.addEventListener('visibilitychange', function() {
            if (!document.hidden && !document.getElementById('dashbase-root')) {
                window.location.replace(window.location.href);
            }
        });
    }
})();