from models import Mentor, db

MENTORS = [
    {
        "name": "Ananya Sharma",
        "domain": "Tech",
        "experience": "8 years",
        "bio": "Senior Software Engineer at Google, specializes in distributed systems and backend architecture.",
        "availability": "Weekends, 4-6 PM",
    },
    {
        "name": "Rohit Malhotra",
        "domain": "Finance",
        "experience": "12 years",
        "bio": "Investment Banking VP at Goldman Sachs, expert in equity research and financial modeling.",
        "availability": "Weekday evenings",
    },
    {
        "name": "Priya Nair",
        "domain": "Design",
        "experience": "6 years",
        "bio": "Lead Product Designer at Swiggy, passionate about UX research and design systems.",
        "availability": "Tue/Thu, 7-9 PM",
    },
    {
        "name": "Karan Mehta",
        "domain": "Product",
        "experience": "10 years",
        "bio": "Senior Product Manager at Microsoft, focused on B2B SaaS and growth strategy.",
        "availability": "Weekends, mornings",
    },
    {
        "name": "Sneha Kapoor",
        "domain": "Marketing",
        "experience": "7 years",
        "bio": "Head of Growth Marketing at a fintech startup, expert in performance marketing and brand strategy.",
        "availability": "Weekday afternoons",
    },
    {
        "name": "Vikram Singh",
        "domain": "Tech",
        "experience": "5 years",
        "bio": "Full-stack developer at Amazon, enjoys mentoring on system design interviews and coding practices.",
        "availability": "Weekends, all day",
    },
    {
        "name": "Ishita Verma",
        "domain": "Finance",
        "experience": "9 years",
        "bio": "Financial Analyst turned Consultant at Deloitte, specializes in corporate finance and valuations.",
        "availability": "Mon/Wed, 6-8 PM",
    },
    {
        "name": "Aditya Rao",
        "domain": "Design",
        "experience": "4 years",
        "bio": "UI/UX Designer at Zomato, loves helping students build strong design portfolios.",
        "availability": "Weekday evenings",
    },
    {
        "name": "Meera Iyer",
        "domain": "Product",
        "experience": "6 years",
        "bio": "Product Manager at Flipkart, experienced in e-commerce and marketplace products.",
        "availability": "Weekends, 2-5 PM",
    },
    {
        "name": "Arjun Khanna",
        "domain": "Marketing",
        "experience": "11 years",
        "bio": "CMO at a D2C brand, specializes in digital marketing strategy and brand building.",
        "availability": "Flexible, by appointment",
    },
]


def seed_mentors():
    """Insert the demo mentors if the table is empty. Must run inside an app context.

    Idempotent and safe to call on every app startup — this is what keeps the demo
    populated on Render's free tier, where the SQLite file is wiped on every redeploy.
    """
    if Mentor.query.count() > 0:
        return False

    for data in MENTORS:
        db.session.add(Mentor(**data))
    db.session.commit()
    print(f"Seeded {len(MENTORS)} mentors.")
    return True


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        if not seed_mentors():
            print(f"Skipping seed: {Mentor.query.count()} mentor(s) already exist.")
