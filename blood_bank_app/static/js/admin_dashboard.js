
document.addEventListener('DOMContentLoaded', function() {
    const mainContent = document.getElementById('main-content');
    const params = new URLSearchParams(window.location.search);
    const section = params.get('section');
    const message = params.get('msg');

    // ✅ Show success message if exists
    if (message) {
        const alertBox = document.createElement('div');
        alertBox.classList.add('alert-success');
        alertBox.textContent = decodeURIComponent(message);
        document.body.prepend(alertBox);
        setTimeout(() => alertBox.remove(), 3000);
    }

    // ✅ Decide which section to show first
    let defaultPageUrl = "{% url 'admin_dashboard_content' %}";
    if (section === 'manage_bloodstock') {
        defaultPageUrl = "{% url 'manage_bloodstock' %}";
        setActiveOption('option3');
    } else if (section === 'manage_users') {
        defaultPageUrl = "{% url 'manage_users' %}";
        setActiveOption('option2');
    } else if (section === 'manage_requests') {
        defaultPageUrl = "{% url 'manage_requests' %}";
        setActiveOption('option4');
    } else if (section === 'view_reports') {
        defaultPageUrl = "{% url 'view_reports' %}";
        setActiveOption('option5');
    } else {
        setActiveOption('option1');
    }

    // ✅ Load the correct section
    fetch(defaultPageUrl)
        .then(response => response.text())
        .then(html => mainContent.innerHTML = html)
        .catch(err => console.error('Error loading content:', err));

    // ✅ Sidebar click handling
    document.querySelectorAll('.nav-option').forEach(item => {
        item.addEventListener('click', function(e) {
            // Don't block logout link
            if (this.classList.contains('option4')) return;

            e.preventDefault();
            const pageUrl = this.getAttribute('data-page');
            if (!pageUrl) return;

            document.querySelectorAll('.nav-option').forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');

            fetch(pageUrl)
                .then(response => response.text())
                .then(html => mainContent.innerHTML = html)
                .catch(err => console.error('Error loading page:', err));
        });
    });

    // Helper for active state
    function setActiveOption(className) {
        document.querySelectorAll('.nav-option').forEach(opt => opt.classList.remove('active'));
        const target = document.querySelector('.' + className);
        if (target) target.classList.add('active');
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const dateElement = document.getElementById("current-date");
    const now = new Date();
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    dateElement.textContent = now.toLocaleDateString('en-US', options);
});


