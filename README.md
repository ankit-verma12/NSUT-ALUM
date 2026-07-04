# NALUM Mentorship

A lightweight mentorship platform connecting NSUT alumni (mentors) with students. Students
browse mentors by domain, request booking sessions, and discuss in an open forum. Mentors
(via a shared dashboard) accept or reject booking requests. No login system — anyone can
book a session or post/comment by just typing their name.

Built as a portfolio/demo project: API-first Flask backend, zero-build-step frontend,
deployed on Render.

## Who it's for

- **Students** — browse mentors filtered by domain (Tech, Finance, Design, Product,
  Marketing), view a mentor's profile, and submit a booking request.
- **Mentors / admins** — use the dashboard to see pending bookings and accept/reject them.
- **Anyone** — post in the discussion forum and comment on existing posts.

There's intentionally no authentication in this version — see [Known Limitations](#known-limitations).

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Flask | Minimal, unopinionated — fits a small API-first app without the overhead of a full framework like Django. |
| Database | SQLite via Flask-SQLAlchemy | Zero-config, file-based, no separate DB server to provision. Fine for a demo; see limitations for why it's not ideal on Render's free tier. |
| Frontend | Plain HTML/CSS/JS (Jinja templates) | No build step, no npm toolchain — Flask serves the pages directly and JS just calls the JSON API with `fetch`. Keeps the whole stack in one language (Python) plus vanilla JS. |
| Production server | gunicorn | Flask's built-in dev server (`app.run()`) isn't meant for production — no concurrency, no process management. gunicorn is the standard WSGI server Render expects. |
| Deployment | Render (free web service) | Simple git-push-to-deploy for a Python app, no Dockerfile required. |

## Database schema

Four tables, no `User` table — bookings and posts store the submitter's name directly
instead of referencing an account.

```
Mentor                          Booking
--------------------------      --------------------------
id            PK                id            PK
name                            mentor_id     FK -> Mentor.id
domain                          student_name
experience                      email
bio                             reason
availability                    date
                                 status  (pending | accepted | rejected, default "pending")

Posts                           Comments
--------------------------      --------------------------
id            PK                id            PK
title                           post_id       FK -> Posts.id
body                            author
author                          comment
date                             date
```

Relationships:
- `Booking.mentor_id` → `Mentor.id`. Deleting a mentor cascades to delete their bookings
  (no orphaned bookings pointing at a mentor that no longer exists).
- `Comments.post_id` → `Posts.id`. Deleting a post cascades to delete its comments.

See [models.py](models.py) for the SQLAlchemy definitions.

## API routes

All routes accept/return JSON (except the five page routes, which render HTML).

**Pages**

| Method | Route | Description |
|---|---|---|
| GET | `/` | Home — mentor listing with domain filter |
| GET | `/mentor/<id>` | Mentor profile + booking form |
| GET | `/forum` | Forum post list |
| GET | `/post/<id>` | Post detail + comments |
| GET | `/dashboard` | Stats, recent bookings, recent posts |

**Mentors**

| Method | Route | Description |
|---|---|---|
| GET | `/api/mentors` | List all mentors. Supports `?domain=<value>` filter (case-insensitive exact match) |
| GET | `/api/mentors/<id>` | Get one mentor. 404 if not found |
| POST | `/api/mentors` | Create a mentor. Body: `name, domain, experience, bio, availability` |
| PUT | `/api/mentors/<id>` | Update any subset of mentor fields |
| DELETE | `/api/mentors/<id>` | Delete a mentor (cascades to delete their bookings) |

**Bookings**

| Method | Route | Description |
|---|---|---|
| GET | `/api/bookings` | List all bookings, newest first, with `mentor_name` joined in |
| GET | `/api/bookings/mentor/<mentor_id>` | Bookings for one mentor |
| POST | `/api/bookings` | Create a booking. Body: `mentor_id, student_name, email, reason, date`. Status always starts `"pending"` |
| PUT | `/api/bookings/<id>` | Update status only. Body: `status` — must be `pending`/`accepted`/`rejected` |
| DELETE | `/api/bookings/<id>` | Delete a booking |

**Forum**

| Method | Route | Description |
|---|---|---|
| GET | `/api/posts` | List all posts, newest first, each with a `comment_count` |
| GET | `/api/posts/<id>` | One post with its full list of comments |
| POST | `/api/posts` | Create a post. Body: `title, body, author` |
| DELETE | `/api/posts/<id>` | Delete a post (cascades to delete its comments) |
| POST | `/api/posts/<id>/comments` | Add a comment. Body: `author, comment` |
| DELETE | `/api/comments/<id>` | Delete a comment |

**Dashboard**

| Method | Route | Description |
|---|---|---|
| GET | `/api/dashboard` | `{ mentor_count, booking_count, pending_bookings, post_count, recent_bookings, recent_posts }` |

All error responses are `{"error": "..."}` with an appropriate status code (`400` for
validation errors, `404` for missing resources).

## Running locally

Requires Python 3.11+.

```bash
git clone <your-repo-url>
cd nalum-mentorship

python -m venv venv
source venv/Scripts/activate      # Windows Git Bash
# venv\Scripts\activate.bat       # Windows cmd
# source venv/bin/activate        # macOS/Linux

pip install -r requirements.txt

python seed.py        # optional — app.py auto-seeds on first run anyway
python app.py
```

Visit `http://127.0.0.1:5000`. The SQLite file (`nalum.db`) is created automatically on
first run, and 10 demo mentors are seeded automatically if the `Mentor` table is empty
(see [Known Limitations](#known-limitations) for why this auto-seed matters on Render).

To run with Flask's debugger/auto-reload locally: `FLASK_DEBUG=1 python app.py`.

## Folder structure

```
nalum-mentorship/
  app.py               Flask app: page routes + all /api/* routes
  models.py             SQLAlchemy models — Mentor, Booking, Posts, Comments
  seed.py               Demo mentor data + seed_mentors(), called both standalone and by app.py on startup
  requirements.txt       Pinned dependencies
  render.yaml            Render Blueprint (build/start commands, env vars)
  templates/             Jinja templates (base.html + one per page), just HTML shells — no server-rendered data
    base.html            Shared nav + <head>, extended by every page
    index.html            /
    mentor.html            /mentor/<id>
    forum.html            /forum
    post.html            /post/<id>
    dashboard.html        /dashboard
  static/
    css/style.css        Single stylesheet, black-red theme, used by every page
    js/
      api.js             Shared fetch wrapper + helpers (escapeHtml, formatDate, avatar generation)
      index.js, mentor.js, forum.js, post.js, dashboard.js   One script per page, each calls `api.*` and renders into the DOM
    images/nsut-logo.png  Navbar logo
```

The frontend has no build step: templates render a static shell, and each page's JS file
fetches from `/api/*` and fills in the DOM. This is why `templates/` and `static/js/`
are split one-to-one per page.

## Deploying to Render

### 1. Push to GitHub

Render deploys from a git repo. If you haven't already:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

(`.gitignore` already excludes `venv/`, `nalum.db`, and `__pycache__/`.)

### 2. Create the Render service

Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Web Service**.

- Connect your GitHub repo.
- Render should detect `render.yaml` and offer to use it as a **Blueprint** — accept
  that and it fills in the settings below automatically. If it doesn't pick it up,
  configure manually:

| Setting | Value |
|---|---|
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance Type | Free |

### 3. Environment variables

Set these under the service's **Environment** tab (already in `render.yaml` if using
the Blueprint):

| Key | Value | Why |
|---|---|---|
| `PYTHON_VERSION` | `3.12.7` | Pins the Python version Render builds with |
| `FLASK_DEBUG` | `0` | Not strictly required — gunicorn never triggers `app.run()`'s debug flag — but set explicitly so nothing accidentally runs in debug mode |

No database URL or secret key is needed — there's no auth and the DB is a local SQLite
file.

### 4. Deploy

Click **Create Web Service**. Render will run the build command, then start the app
with gunicorn. First boot will auto-create the SQLite file and auto-seed the 10 demo
mentors (via `seed_mentors()` running inside `create_app()`).

Your app will be live at `https://<your-service-name>.onrender.com`.

### 5. Verify

```bash
curl https://<your-service-name>.onrender.com/api/health
curl https://<your-service-name>.onrender.com/api/mentors
```

You should see `{"status": "ok"}` and a list of 10 mentors.

## Known limitations

- **SQLite resets on Render's free tier.** Render's free web services use an ephemeral
  filesystem — anything written to disk (including `nalum.db`) is wiped on every
  redeploy, and can also reset when the service spins down after inactivity and spins
  back up. This means **any bookings, posts, or comments created by users will
  disappear on the next deploy or cold start.** The 10 demo mentors will always come
  back (thanks to the auto-seed in `create_app()`), but user-submitted data won't
  persist long-term. For real persistence, you'd need Render's paid persistent disk
  add-on, or swap SQLite for a managed Postgres instance (Render offers a free Postgres
  tier — migrating would mean changing `SQLALCHEMY_DATABASE_URI` and swapping any
  SQLite-specific behavior, of which there currently is none).
- **No authentication.** Anyone can create, and there's no ownership check on
  delete/update — e.g. any visitor can delete any booking or comment via the API. This
  is by design for this version (explicitly scoped out), but is the first thing to add
  before this could be a real production tool: sessions or JWT, a `User` table, and
  ownership checks on the mutating routes.
- **No pagination.** `/api/mentors`, `/api/bookings`, and `/api/posts` return every row.
  Fine at demo scale (10 mentors, a handful of bookings/posts); would need `?page=`/
  `?limit=` params before this scaled to hundreds of rows.
- **No file uploads.** Mentor "photos" on the frontend are generated initials avatars
  (colored circle + initials, computed client-side from the mentor's name) — there's no
  `photo_url` field or image upload, by design, to keep the schema to exactly the 6
  Mentor fields.
- **No input sanitization beyond required-field checks.** Free-text fields (bio, post
  body, comments) aren't length-capped or profanity-filtered — acceptable for a demo,
  not for a public-facing production app.
- **Single instance only.** Because the DB is a local SQLite file, this can't be
  horizontally scaled to multiple Render instances (they'd each see a different copy of
  the file). Fine for Render's free tier (always 1 instance), but worth knowing if this
  ever moves to a paid multi-instance plan — would require Postgres first.
