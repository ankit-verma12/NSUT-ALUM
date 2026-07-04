const emailForm = document.getElementById("email-form");
const wrapEl = document.getElementById("student-bookings-wrap");
const tbody = document.querySelector("#student-bookings-table tbody");
const emptyEl = document.getElementById("student-empty-state");

function statusBadge(status) {
  return `<span class="status-badge status-${escapeHtml(status)}">${escapeHtml(status)}</span>`;
}

function renderBookings(bookings) {
  if (!bookings.length) {
    wrapEl.classList.add("hidden");
    emptyEl.textContent = "No requests yet.";
    emptyEl.classList.remove("hidden");
    return;
  }

  emptyEl.classList.add("hidden");
  wrapEl.classList.remove("hidden");
  tbody.innerHTML = bookings
    .map(
      (b) => `
        <tr>
          <td>${escapeHtml(b.mentor_name)}</td>
          <td>${escapeHtml(b.reason)}</td>
          <td>${escapeHtml(b.date)}</td>
          <td>${statusBadge(b.status)}</td>
        </tr>
      `
    )
    .join("");
}

emailForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("student-email").value.trim();

  wrapEl.classList.add("hidden");
  emptyEl.classList.add("hidden");

  try {
    const bookings = await api.getBookingsByEmail(email);
    renderBookings(bookings);
  } catch (err) {
    emptyEl.textContent = err.message;
    emptyEl.classList.remove("hidden");
  }
});
