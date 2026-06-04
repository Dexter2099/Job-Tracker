from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models import (
    ApplicationStatus,
    ApplicationStatusHistory,
    Company,
    Contact,
    FollowUpReminder,
    JobApplication,
)


SEED_COMPANIES = [
    {
        "name": "Atlassian",
        "website": "https://www.atlassian.com",
        "notes": "Collaboration software company with backend platform roles.",
    },
    {
        "name": "Canva",
        "website": "https://www.canva.com",
        "notes": "Design platform with product engineering teams in Australia.",
    },
    {
        "name": "Gilmour Space",
        "website": "https://www.gspace.com",
        "notes": "Queensland aerospace company building launch vehicles.",
    },
    {
        "name": "Rheinmetall",
        "website": "https://www.rheinmetall.com",
        "notes": "Defence technology employer with software-adjacent roles.",
    },
    {
        "name": "Suncorp",
        "website": "https://www.suncorp.com.au",
        "notes": "Financial services company with cloud and platform teams.",
    },
    {
        "name": "TechnologyOne",
        "website": "https://www.technologyonecorp.com",
        "notes": "Enterprise SaaS company headquartered in Brisbane.",
    },
]


SEED_CONTACTS = [
    {
        "company": "Atlassian",
        "name": "Priya Shah",
        "email": "priya.shah@atlassian.example",
        "role_title": "Technical Recruiter",
        "notes": "Asked for backend project examples and API testing experience.",
    },
    {
        "company": "Canva",
        "name": "Morgan Lee",
        "email": "morgan.lee@canva.example",
        "role_title": "Engineering Recruiter",
        "notes": "Suggested highlighting FastAPI and PostgreSQL project work.",
    },
    {
        "company": "Gilmour Space",
        "name": "Alex Nguyen",
        "email": "alex.nguyen@gilmourspace.example",
        "role_title": "Talent Partner",
        "notes": "Interested in Python, testing, and operational reliability.",
    },
    {
        "company": "Rheinmetall",
        "name": "Sarah Walker",
        "email": "sarah.walker@rheinmetall.example",
        "role_title": "Recruitment Consultant",
        "notes": "Recommended applying for graduate software-adjacent roles.",
    },
    {
        "company": "Suncorp",
        "name": "Daniel Brown",
        "email": "daniel.brown@suncorp.example",
        "role_title": "Technology Recruiter",
        "notes": "Mentioned cloud platform and API integration teams.",
    },
    {
        "company": "TechnologyOne",
        "name": "Emily Carter",
        "email": "emily.carter@technologyone.example",
        "role_title": "Graduate Talent Lead",
        "notes": "Asked for a concise portfolio walkthrough.",
    },
]


SEED_APPLICATIONS = [
    {
        "company": "Atlassian",
        "contact_email": "priya.shah@atlassian.example",
        "role_title": "Junior Backend Engineer",
        "location": "Sydney",
        "job_url": "https://example.com/atlassian-junior-backend",
        "status": ApplicationStatus.interview,
        "source": "LinkedIn",
        "salary_range": "$85,000-$100,000",
        "notes": "Applied with API portfolio project and tailored backend resume.",
        "follow_up_date": date(2026, 6, 10),
        "applied_date": date(2026, 6, 1),
        "history": [
            ("applied", date(2026, 6, 1), "Submitted tailored application."),
            ("interview", date(2026, 6, 4), "Recruiter screen booked."),
        ],
        "reminders": [
            (
                date(2026, 6, 10),
                "Send a concise follow-up on backend role progress.",
                False,
            )
        ],
    },
    {
        "company": "Canva",
        "contact_email": "morgan.lee@canva.example",
        "role_title": "Graduate Software Engineer",
        "location": "Sydney",
        "job_url": "https://example.com/canva-graduate-software",
        "status": ApplicationStatus.technical_interview,
        "source": "Company careers page",
        "salary_range": "$90,000-$105,000",
        "notes": "Highlighted testing, migrations, and clean API contracts.",
        "follow_up_date": date(2026, 6, 12),
        "applied_date": date(2026, 6, 2),
        "history": [
            ("applied", date(2026, 6, 2), "Application submitted."),
            ("interview", date(2026, 6, 5), "Initial screen completed."),
            (
                "technical_interview",
                date(2026, 6, 9),
                "Technical interview scheduled.",
            ),
        ],
        "reminders": [
            (date(2026, 6, 12), "Review SQLAlchemy and pytest talking points.", False)
        ],
    },
    {
        "company": "Gilmour Space",
        "contact_email": "alex.nguyen@gilmourspace.example",
        "role_title": "Junior Python Developer",
        "location": "Gold Coast",
        "job_url": "https://example.com/gilmour-python-developer",
        "status": ApplicationStatus.applied,
        "source": "SEEK",
        "salary_range": "$75,000-$90,000",
        "notes": "Emphasized Python backend fundamentals and reliability mindset.",
        "follow_up_date": date(2026, 6, 14),
        "applied_date": date(2026, 6, 3),
        "history": [
            ("applied", date(2026, 6, 3), "Application submitted through SEEK.")
        ],
        "reminders": [
            (date(2026, 6, 14), "Follow up if no recruiter response.", False)
        ],
    },
    {
        "company": "Rheinmetall",
        "contact_email": "sarah.walker@rheinmetall.example",
        "role_title": "Graduate Software Analyst",
        "location": "Brisbane",
        "job_url": "https://example.com/rheinmetall-software-analyst",
        "status": ApplicationStatus.rejected,
        "source": "Referral",
        "salary_range": "$80,000-$95,000",
        "notes": "Good fit technically, but role required defence domain experience.",
        "follow_up_date": None,
        "applied_date": date(2026, 5, 28),
        "history": [
            ("applied", date(2026, 5, 28), "Applied after recruiter conversation."),
            ("rejected", date(2026, 6, 6), "Rejected after resume review."),
        ],
        "reminders": [],
    },
    {
        "company": "Suncorp",
        "contact_email": "daniel.brown@suncorp.example",
        "role_title": "API Integration Developer",
        "location": "Brisbane",
        "job_url": "https://example.com/suncorp-api-integration",
        "status": ApplicationStatus.offer,
        "source": "LinkedIn",
        "salary_range": "$88,000-$102,000",
        "notes": "Strong interview discussion around API contracts and migrations.",
        "follow_up_date": date(2026, 6, 16),
        "applied_date": date(2026, 5, 25),
        "history": [
            ("applied", date(2026, 5, 25), "Submitted application."),
            ("interview", date(2026, 5, 30), "Recruiter screen completed."),
            ("offer", date(2026, 6, 7), "Verbal offer received."),
        ],
        "reminders": [
            (date(2026, 6, 16), "Review offer details and prepare questions.", False)
        ],
    },
    {
        "company": "TechnologyOne",
        "contact_email": "emily.carter@technologyone.example",
        "role_title": "Graduate Backend Developer",
        "location": "Brisbane",
        "job_url": "https://example.com/technologyone-backend",
        "status": ApplicationStatus.applied,
        "source": "Company careers page",
        "salary_range": "$78,000-$92,000",
        "notes": "Used JobTracker API as the main portfolio example.",
        "follow_up_date": date(2026, 6, 18),
        "applied_date": date(2026, 6, 5),
        "history": [
            ("applied", date(2026, 6, 5), "Applied with portfolio link.")
        ],
        "reminders": [
            (date(2026, 6, 18), "Send portfolio follow-up email.", False)
        ],
    },
]


def changed_at(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, 9, 0, tzinfo=UTC)


def get_company(db: Session, name: str) -> Company | None:
    return db.execute(select(Company).where(Company.name == name)).scalar_one_or_none()


def get_contact(db: Session, email: str) -> Contact | None:
    return db.execute(select(Contact).where(Contact.email == email)).scalar_one_or_none()


def get_application(
    db: Session,
    company: str,
    role_title: str,
) -> JobApplication | None:
    return db.execute(
        select(JobApplication).where(
            JobApplication.company == company,
            JobApplication.role_title == role_title,
        )
    ).scalar_one_or_none()


def seed_companies(db: Session, summary: dict[str, int]) -> dict[str, Company]:
    companies = {}
    for item in SEED_COMPANIES:
        company = get_company(db, item["name"])
        if company is None:
            company = Company(**item)
            db.add(company)
            db.flush()
            summary["companies_created"] += 1
        else:
            summary["companies_skipped"] += 1
        companies[company.name] = company
    return companies


def seed_contacts(
    db: Session,
    companies: dict[str, Company],
    summary: dict[str, int],
) -> dict[str, Contact]:
    contacts = {}
    for item in SEED_CONTACTS:
        contact = get_contact(db, item["email"])
        if contact is None:
            contact_data = {key: value for key, value in item.items() if key != "company"}
            contact = Contact(company_id=companies[item["company"]].id, **contact_data)
            db.add(contact)
            db.flush()
            summary["contacts_created"] += 1
        else:
            summary["contacts_skipped"] += 1
        contacts[contact.email] = contact
    return contacts


def seed_status_history(
    db: Session,
    application: JobApplication,
    history_items: list[tuple[str, date, str]],
    summary: dict[str, int],
) -> None:
    existing_count = db.execute(
        select(ApplicationStatusHistory).where(
            ApplicationStatusHistory.application_id == application.id
        )
    ).scalars().all()
    if existing_count:
        summary["status_history_skipped"] += len(history_items)
        return

    previous_status = None
    for new_status, status_date, note in history_items:
        db.add(
            ApplicationStatusHistory(
                application_id=application.id,
                old_status=previous_status,
                new_status=new_status,
                changed_at=changed_at(status_date),
                note=note,
            )
        )
        previous_status = new_status
        summary["status_history_created"] += 1


def seed_reminders(
    db: Session,
    application: JobApplication,
    reminders: list[tuple[date, str, bool]],
    summary: dict[str, int],
) -> None:
    for reminder_date, note, completed in reminders:
        existing = db.execute(
            select(FollowUpReminder).where(
                FollowUpReminder.application_id == application.id,
                FollowUpReminder.reminder_date == reminder_date,
                FollowUpReminder.note == note,
            )
        ).scalar_one_or_none()
        if existing is not None:
            summary["reminders_skipped"] += 1
            continue

        db.add(
            FollowUpReminder(
                application_id=application.id,
                reminder_date=reminder_date,
                note=note,
                completed=completed,
            )
        )
        summary["reminders_created"] += 1


def seed_applications(
    db: Session,
    companies: dict[str, Company],
    contacts: dict[str, Contact],
    summary: dict[str, int],
) -> None:
    for item in SEED_APPLICATIONS:
        application = get_application(db, item["company"], item["role_title"])
        if application is None:
            contact = contacts[item["contact_email"]]
            application = JobApplication(
                company=item["company"],
                company_id=companies[item["company"]].id,
                contact_id=contact.id,
                contact_name=contact.name,
                contact_email=contact.email,
                role_title=item["role_title"],
                location=item["location"],
                job_url=item["job_url"],
                status=item["status"],
                source=item["source"],
                salary_range=item["salary_range"],
                notes=item["notes"],
                follow_up_date=item["follow_up_date"],
                applied_date=item["applied_date"],
            )
            db.add(application)
            db.flush()
            summary["applications_created"] += 1
        else:
            summary["applications_skipped"] += 1

        seed_status_history(db, application, item["history"], summary)
        seed_reminders(db, application, item["reminders"], summary)


def seed_database(db: Session) -> dict[str, int]:
    summary = {
        "companies_created": 0,
        "companies_skipped": 0,
        "contacts_created": 0,
        "contacts_skipped": 0,
        "applications_created": 0,
        "applications_skipped": 0,
        "status_history_created": 0,
        "status_history_skipped": 0,
        "reminders_created": 0,
        "reminders_skipped": 0,
    }
    companies = seed_companies(db, summary)
    contacts = seed_contacts(db, companies, summary)
    seed_applications(db, companies, contacts, summary)
    db.commit()
    return summary


def print_summary(summary: dict[str, int]) -> None:
    print("Seed data complete:")
    for key, value in summary.items():
        print(f"- {key}: {value}")


def main() -> None:
    db = SessionLocal()
    try:
        print_summary(seed_database(db))
    finally:
        db.close()


if __name__ == "__main__":
    main()
