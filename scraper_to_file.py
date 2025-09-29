import requests
import asyncio 
import time
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
OUTPUT_FILE = "jobs_junior.txt"
HEADERS = {'User-Agent': "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0)"}
DJINNI_URL = "https://djinni.co/jobs/?primary_keyword=Python&exp_level=no_exp"
WORK_UA_URL = "https://www.work.ua/jobs-remote-junior+python+developer/"
ROBOTA_URL = "https://robota.ua/zapros/python/ukraine/params;scheduleIds=3;experienceType=true"

def save_jobs(jobs: list, source: str, mode: str = "a"):
    with open(OUTPUT_FILE, mode, encoding="utf-8") as f:
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        f.write(f"Jobs scraped at: {now}\n")
        for job in jobs:
            f.write(f"Title: {job.get('title')}\n")
            f.write(f"Salary: {job.get('salary')}\n")
            f.write(f"URL: {job.get('url')}\n")
            if job.get('details'):
                f.write(f"Details: {job.get('details')}\n")
            if job.get('description'):
                f.write(f"Description: {job.get('description')}\n")
            f.write(f"Found on: {source}\n")
            f.write("-" * 40 + "\n")
    logging.info("Saved %d jobs from %s", len(jobs), source)

def scrape_djinni() -> List[Dict[str, str]]:
    r = requests.get(DJINNI_URL, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html5lib')

    jobs = []
    for row in soup.select("main#jobs_main li.mb-4"):
        jobs.append({
            "title": row.select_one("a.job-item__title-link").text.strip() if row.select_one("a.job-item__title-link") else "No Title",
            "salary": row.select_one("span.text-success.text-nowrap").text.strip() if row.select_one("span.text-success.text-nowrap") else "No salary",
            "url": "https://djinni.co" + row.h2.find("a")["href"],
            "details": ", ".join(span.text.strip() for span in row.select("span.text-nowrap")) or "No details",
            "description": row.select_one("span.js-truncated-text").text.strip() if row.select_one("span.js-truncated-text") else "No description"
        })

    logging.info("Scraped %d jobs from Djinni", len(jobs))
    return jobs


def scrape_work_ua() -> List[Dict[str, str]]:
    r = requests.get(WORK_UA_URL, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html5lib')

    job_blocks = soup.select("div#pjax-jobs-list div.job-link")

    jobs = []
    for block in job_blocks:
        jobs.append({
            "title": block.select_one("h2.my-0").text.strip() if block.select_one("h2.my-0") else "No Title",
            "salary": block.select_one("span.strong-600").text.strip() if block.select_one("span.strong-600") else "No salary",
            "url": "https://work.ua" + block.find("a")["href"],
            "details": ", ".join(span.text.strip() for span in block.select("span.mt-xs")) or "No details",
            "description": block.select_one("p.ellipsis-line-3").text.strip() if block.select_one("p.ellipsis-line-3") else "No description"
        })

    logging.info("Scraped %d jobs from work.ua", len(jobs))
    return jobs


async def scrape_robota_ua() -> List[Dict[str, str]]:
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

    logging.info("Scraped %d jobs from robota.ua", len(jobs))
    return jobs


def main():
    start = time.perf_counter()

    djinni_jobs = scrape_djinni()
    work_ua_jobs = scrape_work_ua()
    robota_jobs = asyncio.run(scrape_robota_ua())

    save_jobs(djinni_jobs, source="Djinni", mode="w")
    save_jobs(work_ua_jobs, source="Work.ua")
    save_jobs(robota_jobs, source="Robota.ua")

    end = time.perf_counter()
    logging.info("Scraping completed in %.2f seconds", end - start)


if __name__ == "__main__":
    main()
