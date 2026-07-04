import json

import requests

BASE = "http://127.0.0.1:5000"
passed = 0
failed = 0


def check(label, resp, expected_status):
    global passed, failed
    ok = resp.status_code == expected_status
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    try:
        body = resp.json()
    except ValueError:
        body = resp.text
    print(f"[{status}] {label} -> {resp.status_code} (expected {expected_status})")
    print(f"       {json.dumps(body)[:300]}")
    return body


print("=" * 70)
print("MENTOR ROUTES")
print("=" * 70)

body = check("GET /api/mentors", requests.get(f"{BASE}/api/mentors"), 200)

body = check(
    "GET /api/mentors?domain=Tech",
    requests.get(f"{BASE}/api/mentors", params={"domain": "Tech"}),
    200,
)

body = check("GET /api/mentors/1", requests.get(f"{BASE}/api/mentors/1"), 200)

check("GET /api/mentors/9999 (not found)", requests.get(f"{BASE}/api/mentors/9999"), 404)

new_mentor = {
    "name": "Test Mentor",
    "domain": "Tech",
    "experience": "3 years",
    "bio": "Test bio",
    "availability": "Anytime",
}
body = check(
    "POST /api/mentors",
    requests.post(f"{BASE}/api/mentors", json=new_mentor),
    201,
)
created_mentor_id = body["id"]

check(
    "POST /api/mentors (missing fields)",
    requests.post(f"{BASE}/api/mentors", json={"name": "Incomplete"}),
    400,
)

body = check(
    f"PUT /api/mentors/{created_mentor_id}",
    requests.put(
        f"{BASE}/api/mentors/{created_mentor_id}",
        json={"bio": "Updated bio"},
    ),
    200,
)

print("=" * 70)
print("BOOKING ROUTES")
print("=" * 70)

new_booking = {
    "mentor_id": 1,
    "student_name": "Test Student",
    "email": "student@test.com",
    "reason": "Career advice",
    "date": "2026-07-10",
}
body = check(
    "POST /api/bookings",
    requests.post(f"{BASE}/api/bookings", json=new_booking),
    201,
)
booking_id = body["id"]
assert body["status"] == "pending", "status should default to pending"
assert body["mentor_name"] == "Ananya Sharma", "mentor_name should be joined"

check(
    "POST /api/bookings (bad mentor_id)",
    requests.post(f"{BASE}/api/bookings", json={**new_booking, "mentor_id": 9999}),
    400,
)

check(
    "POST /api/bookings (missing fields)",
    requests.post(f"{BASE}/api/bookings", json={"mentor_id": 1}),
    400,
)

body = check("GET /api/bookings", requests.get(f"{BASE}/api/bookings"), 200)

body = check(
    "GET /api/bookings/mentor/1",
    requests.get(f"{BASE}/api/bookings/mentor/1"),
    200,
)

check(
    "GET /api/bookings/mentor/9999 (not found)",
    requests.get(f"{BASE}/api/bookings/mentor/9999"),
    404,
)

body = check(
    f"PUT /api/bookings/{booking_id} (accept)",
    requests.put(f"{BASE}/api/bookings/{booking_id}", json={"status": "accepted"}),
    200,
)
assert body["status"] == "accepted"

check(
    f"PUT /api/bookings/{booking_id} (invalid status)",
    requests.put(f"{BASE}/api/bookings/{booking_id}", json={"status": "maybe"}),
    400,
)

body = check(
    "GET /api/bookings/student?email=student@test.com",
    requests.get(f"{BASE}/api/bookings/student", params={"email": "student@test.com"}),
    200,
)
assert len(body) == 1 and body[0]["id"] == booking_id, "should find the booking by email"

body = check(
    "GET /api/bookings/student?email=nobody@test.com",
    requests.get(f"{BASE}/api/bookings/student", params={"email": "nobody@test.com"}),
    200,
)
assert body == [], "unknown email should return an empty list, not 404"

check(
    "GET /api/bookings/student (missing email)",
    requests.get(f"{BASE}/api/bookings/student"),
    400,
)

print("=" * 70)
print("FORUM ROUTES")
print("=" * 70)

new_post = {
    "title": "Test Post",
    "body": "This is a test post body.",
    "author": "Test Author",
}
body = check("POST /api/posts", requests.post(f"{BASE}/api/posts", json=new_post), 201)
post_id = body["id"]

check(
    "POST /api/posts (missing fields)",
    requests.post(f"{BASE}/api/posts", json={"title": "No body/author"}),
    400,
)

body = check("GET /api/posts", requests.get(f"{BASE}/api/posts"), 200)
assert "comment_count" in body[0], "list should include comment_count"

new_comment = {"author": "Commenter", "comment": "Nice post!"}
body = check(
    f"POST /api/posts/{post_id}/comments",
    requests.post(f"{BASE}/api/posts/{post_id}/comments", json=new_comment),
    201,
)
comment_id = body["id"]

check(
    f"POST /api/posts/9999/comments (post not found)",
    requests.post(f"{BASE}/api/posts/9999/comments", json=new_comment),
    404,
)

body = check(f"GET /api/posts/{post_id}", requests.get(f"{BASE}/api/posts/{post_id}"), 200)
assert len(body["comments"]) == 1, "post should include its comments"

check("GET /api/posts/9999 (not found)", requests.get(f"{BASE}/api/posts/9999"), 404)

print("=" * 70)
print("DASHBOARD ROUTE")
print("=" * 70)

body = check("GET /api/dashboard", requests.get(f"{BASE}/api/dashboard"), 200)
for key in [
    "mentor_count",
    "booking_count",
    "pending_bookings",
    "post_count",
    "recent_bookings",
    "recent_posts",
]:
    assert key in body, f"dashboard missing key: {key}"

print("=" * 70)
print("CLEANUP (delete routes)")
print("=" * 70)

check(f"DELETE /api/comments/{comment_id}", requests.delete(f"{BASE}/api/comments/{comment_id}"), 200)
check("DELETE /api/comments/9999 (not found)", requests.delete(f"{BASE}/api/comments/9999"), 404)

check(f"DELETE /api/posts/{post_id}", requests.delete(f"{BASE}/api/posts/{post_id}"), 200)
check("DELETE /api/posts/9999 (not found)", requests.delete(f"{BASE}/api/posts/9999"), 404)

check(f"DELETE /api/bookings/{booking_id}", requests.delete(f"{BASE}/api/bookings/{booking_id}"), 200)
check("DELETE /api/bookings/9999 (not found)", requests.delete(f"{BASE}/api/bookings/9999"), 404)

check(
    f"DELETE /api/mentors/{created_mentor_id}",
    requests.delete(f"{BASE}/api/mentors/{created_mentor_id}"),
    200,
)
check("DELETE /api/mentors/9999 (not found)", requests.delete(f"{BASE}/api/mentors/9999"), 404)

print("=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 70)
