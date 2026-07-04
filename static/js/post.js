function renderPost(post) {
  const detail = document.getElementById("post-detail");
  detail.innerHTML = `
    <h1>${escapeHtml(post.title)}</h1>
    <p class="muted">by ${escapeHtml(post.author)} &middot; ${formatDate(post.date)}</p>
    <p class="post-body">${escapeHtml(post.body)}</p>
  `;
}

function renderComments(comments) {
  const list = document.getElementById("comment-list");

  if (!comments.length) {
    list.innerHTML = '<p class="empty-state">No comments yet.</p>';
    return;
  }

  list.innerHTML = comments
    .map(
      (c) => `
        <div class="comment card">
          <p class="comment-author">${escapeHtml(c.author)} <span class="muted">&middot; ${formatDate(c.date)}</span></p>
          <p>${escapeHtml(c.comment)}</p>
        </div>
      `
    )
    .join("");
}

async function loadPost() {
  const detail = document.getElementById("post-detail");
  try {
    const post = await api.getPost(POST_ID);
    renderPost(post);
    renderComments(post.comments);
  } catch (err) {
    detail.innerHTML = `<p class="error-text">${escapeHtml(err.message)}</p>`;
  }
}

const commentForm = document.getElementById("comment-form");
const commentMessage = document.getElementById("comment-message");

commentForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  commentMessage.textContent = "";
  commentMessage.className = "message";

  const payload = {
    author: document.getElementById("comment-author").value.trim(),
    comment: document.getElementById("comment-body").value.trim(),
  };

  try {
    await api.addComment(POST_ID, payload);
    commentForm.reset();
    const post = await api.getPost(POST_ID);
    renderComments(post.comments);
  } catch (err) {
    commentMessage.textContent = err.message;
    commentMessage.className = "message error";
  }
});

loadPost();
