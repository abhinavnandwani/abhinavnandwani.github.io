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
     * - If the user has toggled before, use their saved light/dark.
     * - Otherwise follow prefers-color-scheme (nothing persisted until they click).
     */
    function effectiveTheme() {
        var s = getStored();
        if (s === 'light' || s === 'dark') {
            return s;
        }
        if (typeof window.matchMedia === 'function' &&
            window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
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

        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
                if (getStored() !== 'light' && getStored() !== 'dark') {
                    applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    });
})();
