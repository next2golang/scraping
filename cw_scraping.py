import requests
from bs4 import BeautifulSoup
import time

WEBHOOK_URL = 'https://discord.com/api/webhooks/1380639610220187699/v35fb8y1WA9Woxn55x2PgaXxh-4beew3t4VqorFvTAfCYVgHKn2HlT0Oqp__sZ4VqSLt'
CHECK_INTERVAL = 60  # seconds

seen_jobs = set()

def get_latest_jobs():
    url = 'https://crowdworks.jp/public/jobs/group/development'  # Replace with correct category or search URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    jobs = []
    for job in soup.select('.job_data'):
        title = job.select_one('.job_title').get_text(strip=True)
        link = 'https://crowdworks.jp' + job.select_one('a')['href']
        if link not in seen_jobs:
            seen_jobs.add(link)
            jobs.append((title, link))
    return jobs

def notify_discord(jobs):
    for title, link in jobs:
        data = {
            "content": f"🆕 新しい案件: **{title}**\n🔗 {link}"
        }
        requests.post(WEBHOOK_URL, json=data)

while True:
    try:
        if new_jobs := get_latest_jobs():
            notify_discord(new_jobs)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(CHECK_INTERVAL)
