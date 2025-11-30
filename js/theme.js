// Dark Mode Theme Toggle
(function() {
    const THEME_KEY = 'theme';
    const LIGHT = 'light';
    const DARK = 'dark';

    // Get the current theme from localStorage or default to light
    function getTheme() {
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme) {
            return savedTheme;
        }

        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return DARK;
        }

        return LIGHT;
    }

    // Set the theme
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);
    }

    // Toggle between light and dark
    function toggleTheme() {
        const currentTheme = getTheme();
        const newTheme = currentTheme === LIGHT ? DARK : LIGHT;
        setTheme(newTheme);
    }

    // Initialize theme immediately (before page renders)
    const initialTheme = getTheme();
    setTheme(initialTheme);

    // Set up toggle button when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        const toggleButton = document.querySelector('.theme-toggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', toggleTheme);
        }

        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                // Only auto-switch if user hasn't manually set a preference
                const savedTheme = localStorage.getItem(THEME_KEY);
                if (!savedTheme) {
                    setTheme(e.matches ? DARK : LIGHT);
                }
            });
        }
    });
})();
