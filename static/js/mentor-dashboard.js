const mentorSelect = document.getElementById("mentor-select");
const contentEl = document.getElementById("mentor-dashboard-content");
const emptyStateEl = document.getElementById("mentor-empty-state");
const statsGrid = document.getElementById("mentor-stats-grid");
const tbody = document.querySelector("#mentor-bookings-table tbody");

let currentMentorId = null;

async function loadMentorOptions() {
  try {
    const mentors = await api.getMentors();
    mentorSelect.innerHTML =
      '<option value="">-- Choose mentor --</option>' +
      mentors
        .map(
          (m) =>
            `<option value="${m.id}">${escapeHtml(m.name)} (${escapeHtml(m.domain)})</option>`
        )
        .join("");
  } catch (err) {
    mentorSelect.innerHTML = `<option value="">Failed to load mentors</option>`;
  }
}

function renderStats(bookings) {
  const total = bookings.length;
  const pending = bookings.filter((b) => b.status === "pending").length;
  const accepted = bookings.filter((b) => b.status === "accepted").length;
  const rejected = bookings.filter((b) => b.status === "rejected").length;

  statsGrid.innerHTML = `
    <div class="stat-card">
      <div class="stat-value">${total}</div>
      <div class="stat-label">Total Requests</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${pending}</div>
      <div class="stat-label">Pending</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${accepted}</div>
      <div class="stat-label">Accepted</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${rejected}</div>
      <div class="stat-label">Rejected</div>
    </div>
  `;
}

function statusBadge(status) {
  return `<span class="status-badge status-${escapeHtml(status)}">${escapeHtml(status)}</span>`;
}

function renderBookings(bookings) {
  if (!bookings.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No booking requests yet.</td></tr>';
    return;
  }

  tbody.innerHTML = bookings
    .map(
      (b) => `
        <tr>
          <td>${escapeHtml(b.student_name)}</td>
          <td>${escapeHtml(b.email)}</td>
          <td>${escapeHtml(b.reason)}</td>
          <td>${escapeHtml(b.date)}</td>
          <td>${statusBadge(b.status)}</td>
          <td class="actions-cell">
            ${
              b.status === "pending"
                ? `<button class="btn btn-small btn-accept" data-id="${b.id}">Accept</button>
                   <button class="btn btn-small btn-reject" data-id="${b.id}">Reject</button>`
                : ""
            }
          </td>
        </tr>
      `
    )
    .join("");

  tbody.querySelectorAll(".btn-accept").forEach((btn) => {
    btn.addEventListener("click", () => updateStatus(btn.dataset.id, "accepted"));
  });
  tbody.querySelectorAll(".btn-reject").forEach((btn) => {
    btn.addEventListener("click", () => updateStatus(btn.dataset.id, "rejected"));
  });
}

async function loadBookingsForMentor(mentorId) {
  try {
    const bookings = await api.getBookingsForMentor(mentorId);
    renderStats(bookings);
    renderBookings(bookings);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="error-text">${escapeHtml(err.message)}</td></tr>`;
  }
}

async function updateStatus(id, status) {
  try {
    await api.updateBookingStatus(id, status);
    if (currentMentorId) await loadBookingsForMentor(currentMentorId);
  } catch (err) {
    alert(err.message);
  }
}

mentorSelect.addEventListener("change", () => {
  const id = mentorSelect.value;
  if (!id) {
    contentEl.classList.add("hidden");
    emptyStateEl.classList.remove("hidden");
    currentMentorId = null;
    return;
  }
  currentMentorId = id;
  contentEl.classList.remove("hidden");
  emptyStateEl.classList.add("hidden");
  loadBookingsForMentor(id);
});

loadMentorOptions();
