// Dark mode toggle functionality
const darkModeToggle = document.getElementById('darkModeToggle');
darkModeToggle?.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    // Optionally save preference to localStorage
    localStorage.setItem('darkMode', 
        document.documentElement.classList.contains('dark') ? 'dark' : 'light'
    );
});

// Initialize dark mode from saved preference
if (localStorage.getItem('darkMode') === 'dark' || 
    window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.classList.add('dark');
}