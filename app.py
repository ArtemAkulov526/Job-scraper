from flask import Flask, render_template
from extensions import db, migrate
from models import JobPosting

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

@app.route("/")
def index():
    jobs = JobPosting.query.order_by(JobPosting.id.desc()).all()
    return render_template("index.html", jobs=jobs)

if __name__ == "__main__":
    app.run(debug=True)