import requests
from bs4 import BeautifulSoup
from models import db, JobPosting
from app import app  

def get_jobs_djinni():
    URL = "https://djinni.co/jobs/?primary_keyword=Python&exp_level=no_exp"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36"
    }

    r = requests.get(url=URL, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    job = soup.find('main', attrs={'id': 'jobs_main'})
    
    jobs = []
    for row in job.find_all('li', attrs={'class': 'mb-4'}):
        job_data = {
            "title": row.find("a", class_="job-item__title-link").text.strip() if row.find("a", class_="job-item__title-link") else "No Title",
            "salary": row.find("span", class_="text-success text-nowrap").text.strip() if row.find("span", class_="text-success text-nowrap") else "No salary provided",
            "url": row.find("h2").find("a")["href"] if row.find("h2") and row.find("h2").find("a") else "No URL",
            "details": ", ".join([span.text.strip() for span in row.find_all("span", class_="text-nowrap")]) if row.find("span", class_="text-nowrap") else "No details",
            "description": row.find("span", class_="js-truncated-text").text.strip() if row.find("span", class_="js-truncated-text") else "No description"
        }
        jobs.append(job_data)

    
    with app.app_context():
        for job_data in jobs:
            existing_job = JobPosting.query.filter_by(url=job_data["url"]).first()
            if not existing_job:
                job = JobPosting(**job_data)
                db.session.add(job)
                print(f"Added job: {job.title}")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f" Database error: {e}")

if __name__ == "__main__":
    get_jobs_djinni()  
