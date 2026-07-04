const API_BASE = "/api";

async function apiRequest(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }

  if (!res.ok) {
    const message = (data && data.error) || `Request failed (${res.status})`;
    throw new Error(message);
  }

  return data;
}

const api = {
  getMentors: (domain) =>
    apiRequest(`/mentors${domain ? `?domain=${encodeURIComponent(domain)}` : ""}`),
  getMentor: (id) => apiRequest(`/mentors/${id}`),

  createBooking: (payload) =>
    apiRequest("/bookings", { method: "POST", body: JSON.stringify(payload) }),
  updateBookingStatus: (id, status) =>
    apiRequest(`/bookings/${id}`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    }),
  getBookingsForMentor: (mentorId) => apiRequest(`/bookings/mentor/${mentorId}`),
  getBookingsByEmail: (email) =>
    apiRequest(`/bookings/student?email=${encodeURIComponent(email)}`),

  getPosts: () => apiRequest("/posts"),
  getPost: (id) => apiRequest(`/posts/${id}`),
  createPost: (payload) =>
    apiRequest("/posts", { method: "POST", body: JSON.stringify(payload) }),
  addComment: (postId, payload) =>
    apiRequest(`/posts/${postId}/comments`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getDashboard: () => apiRequest("/dashboard"),
};

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatDate(value) {
  if (!value) return "";
  const d = new Date(value);
  if (isNaN(d)) return value;
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

const AVATAR_PALETTE = [
  "#e63946",
  "#457b9d",
  "#2a9d5c",
  "#d4a017",
  "#7209b7",
  "#f4845f",
  "#06a77d",
  "#3a86ff",
];

function getInitials(name) {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash);
}

function avatarHtml(name, sizeClass) {
  const initials = getInitials(name);
  const color = AVATAR_PALETTE[hashString(name) % AVATAR_PALETTE.length];
  return `<div class="avatar ${sizeClass}" style="background:${color}">${escapeHtml(initials)}</div>`;
}
