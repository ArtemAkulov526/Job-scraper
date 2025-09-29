from extensions import db
from datetime import datetime, timezone

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.String(255))
    url = db.Column(db.String(500), unique=True, nullable=False)
    details = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "salary": self.salary,
            "url": self.url,
            "details": self.details,
            "description": self.description,
            "created_at": self.created_at.isoformat() 
        }