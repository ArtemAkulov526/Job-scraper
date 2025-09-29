import asyncio
import json
from flask import Flask, request, render_template
from extensions import db, migrate
from models import JobPosting
from scraper_to_file import scrape_djinni, scrape_work_ua, scrape_robota_ua, save_jobs

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

@app.route("/")
def index():
    jobs = JobPosting.query.order_by(JobPosting.id.desc()).all()
    return render_template("index.html", jobs=jobs)

@app.route("/scrape", methods=["POST"])
def scrape():
    keyword = request.form.get("position")

    djinni_url = f"https://djinni.co/jobs/?primary_keyword={keyword}&exp_level=no_exp"
    work_ua_url = f"https://www.work.ua/jobs-remote-junior+{keyword}/?experience=1"
    robota_url = f"https://robota.ua/zapros/junior-{keyword}/ukraine/params;scheduleIds=3;experienceType=true"

    djinni_jobs=scrape_djinni(djinni_url)
    work_ua_jobs=scrape_work_ua(work_ua_url)
    robota_jobs=asyncio.run(scrape_robota_ua(robota_url))

    save_jobs(djinni_jobs, source="Djinni", mode="w")
    save_jobs(work_ua_jobs, source="Work.ua")
    save_jobs(robota_jobs, source="Robota.ua")
    
    try:
        with open("jobs_junior.json", "r", encoding="utf-8") as f:
            jobs_data = json.load(f)
    except FileNotFoundError:
        jobs_data = []

    return render_template("jobs.html", jobs=jobs_data)

if __name__ == "__main__":
    app.run(debug=True)