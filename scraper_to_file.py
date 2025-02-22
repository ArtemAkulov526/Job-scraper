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


if __name__ == "__main__":
    get_jobs_djinni()




