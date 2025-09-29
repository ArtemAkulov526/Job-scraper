import asyncio 
import aiohttp 
import time
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
from models import db, JobPosting
from playwright.async_api import async_playwright
from app import app  

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
HEADERS = {'User-Agent': "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0)"}
DJINNI_URL = "https://djinni.co/jobs/?primary_keyword=Python&exp_level=no_exp"
WORK_UA_URL = "https://www.work.ua/jobs-remote-junior+python+developer/"
ROBOTA_URL = "https://robota.ua/zapros/python/ukraine/params;scheduleIds=3;experienceType=true"

async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()

def save_jobs_to_db(jobs):
    with app.app_context():
        for job_data in jobs:
            print(f"Checking job: {job_data['url']}")
            if not JobPosting.query.filter_by(url=job_data["url"]).first():
                job = JobPosting(**job_data)
                db.session.add(job)
                logging.info("Added job: %s", job_data["title"])
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error("Database error: %s", e)

async def get_jobs_djinni(session: aiohttp.ClientSession)-> List[Dict[str, str]]:
    html = await fetch(session, DJINNI_URL, headers=HEADERS)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html5lib')
    job = soup.find('main', attrs={'id': 'jobs_main'})
    if not job:
        print("Djinni main block not found")
        return []
    
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
    logging.info("Scraped %d jobs from Djinni", len(jobs))
    return jobs

async def get_jobs_work_ua(session: aiohttp.ClientSession)-> List[Dict[str, str]]:
    html = await fetch(session, WORK_UA_URL, headers=HEADERS)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html5lib')
    job = soup.find('div', attrs={'id': 'pjax-jobs-list'})
    if not job:
        return []
    
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
    logging.info("Scraped %d jobs from Work.ua", len(jobs))
    return jobs


async def get_jobs_robota_ua()-> List[Dict[str, str]]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_extra_http_headers(HEADERS)
        await page.goto(ROBOTA_URL)

        previous_height = 0
        for _ in range(5):
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(1000)
            current_height = await page.evaluate("() => document.body.scrollHeight")
            if current_height == previous_height:
                break
            previous_height = current_height

        await page.wait_for_selector("div.santa--mb-20", timeout=10000)
        content = await page.content()
        await browser.close()

    soup = BeautifulSoup(content, "html.parser")
    job_blocks = soup.select("div.santa--mb-20.ng-star-inserted")

    jobs = []
    for block in job_blocks:
        title = block.select_one("h2.santa-typo-h3")
        salary = block.select_one("span.ng-star-inserted")
        url_tag = block.select_one("a.card")

        jobs.append({
            "title": title.text.strip() if title else "No title",
            "salary": salary.text.strip() if salary else "No salary",
            "url": "https://robota.ua" + url_tag["href"] if url_tag and url_tag.has_attr("href") else "No URL",
            "details": ", ".join(span.text.strip() for span in block.select("span.ng-star-inserted")[1:]) or "No details",
        })

    logging.info("Scraped %d jobs from Robota.ua", len(jobs))
    return jobs

async def main():
    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        djinni_jobs, work_ua_jobs, robota_jobs = await asyncio.gather(
        get_jobs_djinni(session),
        get_jobs_work_ua(session),
        get_jobs_robota_ua()
    )
            
    for job_list in [djinni_jobs, work_ua_jobs, robota_jobs]:
        save_jobs_to_db(job_list)
    
    end = time.perf_counter()
    logging.info("Async scraping completed in %.2f seconds", end - start)

if __name__ == "__main__":
    asyncio.run(main())
