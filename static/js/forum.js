function renderPosts(posts) {
  const list = document.getElementById("post-list");

  if (!posts.length) {
    list.innerHTML = '<p class="empty-state">No posts yet. Be the first to start a discussion.</p>';
    return;
  }

  list.innerHTML = posts
    .map(
      (p) => `
        <div class="card post-card" data-id="${p.id}">
          <h3>${escapeHtml(p.title)}</h3>
          <p class="muted">by ${escapeHtml(p.author)} &middot; ${formatDate(p.date)}</p>
          <p class="comment-count">${p.comment_count} comment${p.comment_count === 1 ? "" : "s"}</p>
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

async function loadPosts() {
  const list = document.getElementById("post-list");
  list.innerHTML = '<p class="loading">Loading posts…</p>';
  try {
    const posts = await api.getPosts();
    renderPosts(posts);
  } catch (err) {
    list.innerHTML = `<p class="error-text">${escapeHtml(err.message)}</p>`;
  }
}

const newPostBtn = document.getElementById("new-post-btn");
const postForm = document.getElementById("post-form");
const postMessage = document.getElementById("post-message");

newPostBtn.addEventListener("click", () => {
  postForm.classList.toggle("hidden");
});

postForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  postMessage.textContent = "";
  postMessage.className = "message";

  const payload = {
    title: document.getElementById("post-title").value.trim(),
    author: document.getElementById("post-author").value.trim(),
    body: document.getElementById("post-body").value.trim(),
  };

  try {
    await api.createPost(payload);
    postMessage.textContent = "Post published!";
    postMessage.className = "message success";
    postForm.reset();
    postForm.classList.add("hidden");
    loadPosts();
  } catch (err) {
    postMessage.textContent = err.message;
    postMessage.className = "message error";
  }
});

loadPosts();
