from app.models import (
    ApplicationStatusHistory,
    Company,
    Contact,
    FollowUpReminder,
    JobApplication,
)
from scripts.seed_data import seed_database


def test_seed_data_creates_demo_records(db_session):
    summary = seed_database(db_session)

    assert summary["companies_created"] == 6
    assert summary["contacts_created"] == 6
    assert summary["applications_created"] == 6
    assert db_session.query(Company).count() == 6
    assert db_session.query(Contact).count() == 6
    assert db_session.query(JobApplication).count() == 6
    assert db_session.query(ApplicationStatusHistory).count() >= 5
    assert db_session.query(FollowUpReminder).count() >= 4


def test_seed_data_is_repeatable_without_uncontrolled_duplicates(db_session):
    first_summary = seed_database(db_session)
    second_summary = seed_database(db_session)

    assert first_summary["applications_created"] == 6
    assert second_summary["applications_created"] == 0
    assert second_summary["applications_skipped"] == 6
    assert db_session.query(Company).count() == 6
    assert db_session.query(Contact).count() == 6
    assert db_session.query(JobApplication).count() == 6


def test_seeded_contacts_link_to_companies(db_session):
    seed_database(db_session)

    canva_contact = (
        db_session.query(Contact)
        .join(Company)
        .filter(Company.name == "Canva")
        .one()
    )

    assert canva_contact.company.name == "Canva"
    assert canva_contact.email == "morgan.lee@canva.example"


def test_seeded_reminders_link_to_applications(db_session):
    seed_database(db_session)

    reminder = (
        db_session.query(FollowUpReminder)
        .join(JobApplication)
        .filter(JobApplication.company == "Atlassian")
        .one()
    )

    assert reminder.application.company == "Atlassian"
    assert reminder.note == "Send a concise follow-up on backend role progress."
