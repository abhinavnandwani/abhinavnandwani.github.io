(function () {
    var STORAGE_KEY = 'theme';

    function getStored() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            return null;
        }
    }

    /**
     * Resolved theme for this page view. Does not write storage.
     * Defaults to light until the visitor uses the theme control (then we persist).
     */
    function effectiveTheme() {
        var s = getStored();
        if (s === 'light' || s === 'dark') {
            return s;
        }
        return 'light';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    }

    function persistTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {}
    }

    applyTheme(effectiveTheme());

    function toggleTheme() {
        var next = effectiveTheme() === 'light' ? 'dark' : 'light';
        applyTheme(next);
        persistTheme(next);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var btn = document.querySelector('.theme-toggle');
        if (btn) {
            btn.addEventListener('click', toggleTheme);
        }
    });
})();
