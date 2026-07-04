async function loadMentor() {
  const detail = document.getElementById("mentor-detail");
  try {
    const m = await api.getMentor(MENTOR_ID);
    detail.innerHTML = `
      <div class="mentor-detail-header">
        ${avatarHtml(m.name, "avatar-lg")}
        <div>
          <div class="card-domain">${escapeHtml(m.domain)}</div>
          <h1>${escapeHtml(m.name)}</h1>
          <p class="muted">${escapeHtml(m.experience)} &middot; ${escapeHtml(m.availability)}</p>
        </div>
      </div>
      <p class="bio-full">${escapeHtml(m.bio)}</p>
    `;
  } catch (err) {
    detail.innerHTML = `<p class="error-text">${escapeHtml(err.message)}</p>`;
  }
}

const bookingForm = document.getElementById("booking-form");
const bookingMessage = document.getElementById("booking-message");

bookingForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  bookingMessage.textContent = "";
  bookingMessage.className = "message";

  const payload = {
    mentor_id: MENTOR_ID,
    student_name: document.getElementById("student_name").value.trim(),
    email: document.getElementById("email").value.trim(),
    reason: document.getElementById("reason").value.trim(),
    date: document.getElementById("date").value,
  };

  try {
    await api.createBooking(payload);
    bookingMessage.textContent = "Booking request sent! The mentor will review it soon.";
    bookingMessage.className = "message success";
    bookingForm.reset();
  } catch (err) {
    bookingMessage.textContent = err.message;
    bookingMessage.className = "message error";
  }
});

loadMentor();
