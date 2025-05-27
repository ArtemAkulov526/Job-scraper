import asyncio
import aiohttp
from bs4 import BeautifulSoup
from models import db, JobPosting
from app import app  

async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def get_jobs_djinni():
    URL = "https://djinni.co/jobs/?primary_keyword=Python&exp_level=no_exp"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0)"
    }

    async with aiohttp.ClientSession() as session:
        html = await fetch(session, URL, headers)
    
    soup = BeautifulSoup(html.content, 'html5lib')
    job = soup.find('main', attrs={'class': 'list-unstyled list-jobs mb-4'})
    
    jobs = []
    for row in job.find_all('li', attrs={'class': 'mb-4'}):
        baseURL = 'https://djinni.co'
        job_data = {
            "title": row.find("a", class_="job-item__title-link").text.strip() if row.find("a", class_="job-item__title-link") else "No Title",
            "salary": row.find("span", class_="text-success text-nowrap").text.strip() if row.find("span", class_="text-success text-nowrap") else "No salary provided",
            "url": baseURL + row.find("h2").find("a")["href"] if row.find("h2") and row.find("h2").find("a") else "No URL",
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

async def get_jobs_work_ua():
    URL = "https://www.work.ua/jobs-remote-junior+python+developer/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    async with aiohttp.ClientSession() as session:
        html = await fetch(session, URL, headers)
    
    soup = BeautifulSoup(html.content, 'html5lib')
    job = soup.find('div', attrs={'id': 'pjax-jobs-list'})
    
    jobs = []
    for row in job.find_all('div', attrs={'class': 'job-link'}):
        job_data = {
            "title": row.find("h2", class_="my-0").text.strip() if row.find("h2", class_="my-0") else "No Title",
            "salary": row.find("span", class_="strong-600").text.strip() if row.find("span", class_="strong-600") else "No salary provided",
            "url": "https://work.ua"+ row.find("h2").find("a")["href"] if row.find("h2") and row.find("h2").find("a") else "No URL",
            "details": ", ".join([span.text.strip() for span in row.find_all("span", class_="mt-xs")]) if row.find("span", class_="mt-xs") else "No details",
            "description": row.find("p", class_="ellipsis ellipsis-line ellipsis-line-3 text-default-7 mb-0").text.strip() if row.find("p", class_="ellipsis ellipsis-line ellipsis-line-3 text-default-7 mb-0") else "No description"
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


async def main():
    await asyncio.gather(
        get_jobs_djinni,
        get_jobs_work_ua
        )


    if __name__ == "__main__":
        asyncio.run(main())
