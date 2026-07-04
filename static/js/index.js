const DOMAINS = ["Tech", "Finance", "Design", "Product", "Marketing"];
let currentDomain = "";
let allMentors = [];
let searchQuery = "";

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
    grid.innerHTML = '<p class="empty-state">No mentors match your search.</p>';
    return;
  }

  grid.innerHTML = mentors
    .map((m) => {
      const preview = m.bio.length > 100 ? m.bio.slice(0, 100) + "…" : m.bio;
      const dotColor = getAvatarColor(m.name);
      return `
        <div class="card mentor-card" data-id="${m.id}">
          <div class="card-domain-badge">${escapeHtml(m.domain)}</div>
          <div class="mentor-card-header">
            ${avatarHtml(m.name, "avatar-md")}
            <h3><span class="status-dot" style="background:${dotColor}"></span>${escapeHtml(m.name)}</h3>
          </div>
          <p class="muted">${escapeHtml(m.experience)}</p>
          <p class="bio-preview">${escapeHtml(preview)}</p>
          <button class="btn btn-outline view-profile" data-id="${m.id}">View Profile &rarr;</button>
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

function applySearchAndRender() {
  const q = searchQuery.trim().toLowerCase();
  const filtered = !q
    ? allMentors
    : allMentors.filter((m) =>
        [m.name, m.domain, m.bio].some((field) => field.toLowerCase().includes(q))
      );
  renderMentors(filtered);
}

async function loadMentors() {
  const grid = document.getElementById("mentor-grid");
  grid.innerHTML = '<p class="loading">Loading mentors…</p>';
  try {
    allMentors = await api.getMentors(currentDomain);
    applySearchAndRender();
  } catch (err) {
    grid.innerHTML = `<p class="error-text">${escapeHtml(err.message)}</p>`;
  }
}

function runSearch() {
  searchQuery = document.getElementById("mentor-search").value;
  applySearchAndRender();
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

document.getElementById("mentor-search").addEventListener("input", runSearch);
document.getElementById("mentor-search-btn").addEventListener("click", runSearch);
document.getElementById("mentor-search").addEventListener("keydown", (e) => {
  if (e.key === "Enter") runSearch();
});

renderFilters();
loadMentors();
loadSiteOverview();
