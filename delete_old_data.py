import logging
from datetime import datetime, timedelta, timezone
from app import app, db
from models import JobPosting

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


def delete_old_jobs(weeks: int = 2):
    """
    Delete all JobPosting records older than 2 weeks.
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=weeks)
    with app.app_context():
        try:
            num_deleted = (
                db.session.query(JobPosting)
                .filter(JobPosting.created_at < cutoff_date) 
                .delete(synchronize_session=False)
            )
            db.session.commit()
            logging.info("Deleted %d JobPosting records older than %d weeks", num_deleted, weeks)
        except Exception as e:
            db.session.rollback()
            logging.error("Error deleting old JobPosting records: %s", e)
        finally:
            db.session.close()


if __name__ == "__main__":
    delete_old_jobs()
