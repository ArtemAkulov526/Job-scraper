import requests
from bs4 import BeautifulSoup

def get_jobs_djinni():
    URL = "https://djinni.co/jobs/?primary_keyword=Python&exp_level=no_exp"
    OUTPUT_FILE = "jobs_junior.txt"
    headers = {'User-Agent':"Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36"}


    r=requests.get(url=URL, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    arr = []
    job = soup.find('main', attrs={'id':'jobs_main'})

    for row in job.find_all('li', attrs={'class':'mb-4'}):

        jobs = {}
        jobs['title'] = row.find("a", class_="job-item__title-link").text.strip() if row.find("a", class_="job-item__title-link") else "No Title"
        jobs['salary'] = row.find("span", class_="text-success text-nowrap").text.strip() if row.find("span", class_="text-success text-nowrap") else "No salary expectations provided"
        jobs['url'] = row.h2.find("a")["href"]
        jobs['details'] = ", ".join([span.text.strip() for span in row.find_all("span", class_="text-nowrap")]) if row.find("span", class_="text-nowrap") else "No details"
        jobs['description'] = row.find("span", class_="js-truncated-text").text.strip() if row.find("span", class_="js-truncated-text") else "No description"
        arr.append(jobs)


    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for job in arr:
            file.write(f"Title: {job['title']}\n")
            file.write(f"Salary: {job['salary']}\n")
            file.write(f"URL: https://djinni.co{job['url']}\n")
            file.write(f"Details: {job['details']}\n")
            file.write(f"Description: {job['description']}\n")
            file.write("-" * 40 + "\n")  

    print(f"Saved {len(arr)} job listings from Djinni to {OUTPUT_FILE}")

def get_jobs_work_ua():
    URL = "https://www.work.ua/jobs-remote-junior+python+developer/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    r = requests.get(url=URL, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    job = soup.find('div', attrs={'id': 'pjax-jobs-list'})
    
    jobs = []
    for row in job.find_all('div', attrs={'class': 'job-link'}):
        job_data = {
            "title": row.find("h2", class_="my-0").text.strip() if row.find("h2", class_="my-0") else "No Title",
            "salary": row.find("span", class_="strong-600").text.strip() if row.find("span", class_="strong-600") else "No salary provided",
            "url": "https://work.ua" + row.find("h2").find("a")["href"] if row.find("h2") and row.find("h2").find("a") else "No URL",
            "details": ", ".join([span.text.strip() for span in row.find_all("span", class_="mt-xs")]) if row.find("span", class_="mt-xs") else "No details",
            "description": row.find("p", class_="ellipsis ellipsis-line ellipsis-line-3 text-default-7 mb-0").text.strip() if row.find("p", class_="ellipsis ellipsis-line ellipsis-line-3 text-default-7 mb-0") else "No description"
        }
        
        jobs.append(job_data)

    OUTPUT_FILE = 'jobs.txt'
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for job in jobs:
            f.write(f"Title: {job['title']}\n")
            f.write(f"Salary: {job['salary']}\n")
            f.write(f"URL: {job['url']}\n")
            f.write(f"Details: {job['details']}\n")
            f.write(f"Description: {job['description']}\n")
            f.write("-" * 40 + "\n")
    
    print(f"Saved {len(jobs)} job listings from work.ua to {OUTPUT_FILE}")



if __name__ == "__main__":
    get_jobs_djinni()
    get_jobs_work_ua()




