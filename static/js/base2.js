document.getElementById("theme-toggle").addEventListener("click", function() {
    document.body.classList.toggle("dark-theme");
});

document.getElementById("notification-toggle").addEventListener("click", function() {
    alert("Notifications toggled!");
});

function navigate(page) {
    window.location.href = `/${page}/`;
}
