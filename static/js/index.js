const DOMAINS = ["Tech", "Finance", "Design", "Product", "Marketing"];
let currentDomain = "";

function makeFilterBtn(label, domain) {
  const btn = document.createElement("button");
  btn.className = "filter-btn" + (domain === currentDomain ? " active" : "");
  btn.textContent = label;
  btn.addEventListener("click", () => {
    currentDomain = domain;
    renderFilters();
    loadMentors();
  });
  return btn;
}

function renderFilters() {
  const bar = document.getElementById("domain-filters");
  bar.innerHTML = "";
  bar.appendChild(makeFilterBtn("All", ""));
  DOMAINS.forEach((d) => bar.appendChild(makeFilterBtn(d, d)));
}

function renderMentors(mentors) {
  const grid = document.getElementById("mentor-grid");

  if (!mentors.length) {
    grid.innerHTML = '<p class="empty-state">No mentors found for this domain.</p>';
    return;
  }

  grid.innerHTML = mentors
    .map((m) => {
      const preview = m.bio.length > 100 ? m.bio.slice(0, 100) + "…" : m.bio;
      return `
        <div class="card mentor-card" data-id="${m.id}">
          <div class="mentor-card-header">
            ${avatarHtml(m.name, "avatar-md")}
            <div>
              <div class="card-domain">${escapeHtml(m.domain)}</div>
              <h3>${escapeHtml(m.name)}</h3>
            </div>
          </div>
          <p class="muted">${escapeHtml(m.experience)}</p>
          <p class="bio-preview">${escapeHtml(preview)}</p>
          <button class="btn btn-outline view-profile" data-id="${m.id}">View Profile</button>
        </div>
      `;
    })
    .join("");

  grid.querySelectorAll(".mentor-card").forEach((card) => {
    card.addEventListener("click", () => {
      window.location.href = `/mentor/${card.dataset.id}`;
    });
  });
}

async function loadMentors() {
  const grid = document.getElementById("mentor-grid");
  grid.innerHTML = '<p class="loading">Loading mentors…</p>';
  try {
    const mentors = await api.getMentors(currentDomain);
    renderMentors(mentors);
  } catch (err) {
    grid.innerHTML = `<p class="error-text">${escapeHtml(err.message)}</p>`;
  }
}

function renderSiteStats(data) {
  const grid = document.getElementById("site-stats-grid");
  grid.innerHTML = `
    <div class="stat-card">
      <div class="stat-value">${data.mentor_count}</div>
      <div class="stat-label">Total Mentors</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${data.booking_count}</div>
      <div class="stat-label">Total Bookings</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${data.post_count}</div>
      <div class="stat-label">Total Posts</div>
    </div>
  `;
}

function renderSiteRecentPosts(posts) {
  const list = document.getElementById("site-recent-posts");

  if (!posts.length) {
    list.innerHTML = '<p class="empty-state">No forum activity yet.</p>';
    return;
  }

  list.innerHTML = posts
    .map(
      (p) => `
        <div class="card post-card" data-id="${p.id}">
          <h3>${escapeHtml(p.title)}</h3>
          <p class="muted">by ${escapeHtml(p.author)} &middot; ${formatDate(p.date)}</p>
        </div>
      `
    )
    .join("");

  list.querySelectorAll(".post-card").forEach((card) => {
    card.addEventListener("click", () => {
      window.location.href = `/post/${card.dataset.id}`;
    });
  });
}

async function loadSiteOverview() {
  try {
    const data = await api.getDashboard();
    renderSiteStats(data);
    renderSiteRecentPosts(data.recent_posts);
  } catch (err) {
    document.getElementById("site-stats-grid").innerHTML = `<p class="error-text">${escapeHtml(err.message)}</p>`;
  }
}

renderFilters();
loadMentors();
loadSiteOverview();
