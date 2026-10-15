// PlacePilot Frontend JavaScript Utilities

document.addEventListener("DOMContentLoaded", function () {
  // 1. Mobile Sidebar Toggle
  const sidebarToggleBtn = document.getElementById("sidebarToggleBtn");
  const sidebar = document.querySelector(".sidebar");
  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });
  }

  // 2. Auto-dismiss Flash Alerts
  const alerts = document.querySelectorAll(".alert.alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {
        // Fallback if bootstrap is not yet loaded
        alert.style.display = "none";
      }
    }, 4500);
  });

  // 3. Confirm Dialog on Destructive Action
  document.querySelectorAll("[data-confirm]").forEach(function (element) {
    element.addEventListener("click", function (e) {
      const message = this.getAttribute("data-confirm") || "Are you sure you want to perform this action?";
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });
});
