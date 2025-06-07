from PyQt5.QtCore import QObject, pyqtSignal
import requests
from bs4 import BeautifulSoup
import time
import json
from win10toast import ToastNotifier
from datetime import datetime

class JobBot(QObject):
    log_signal = pyqtSignal(str)
    
    def __init__(self, webhook_url, target_url, keywords, interval, log_output):
        super().__init__()
        self.webhook_url = webhook_url
        self.target_url = target_url
        self.keywords = keywords
        self.interval = interval
        self.log_output = log_output
        self.seen = set()
        self.running = True
        self.toast = ToastNotifier()
        self.log_signal.connect(self.log_output.append)

    def fetch_jobs(self):
        try:
            res = requests.get(self.target_url)
            soup = BeautifulSoup(res.text, 'html.parser')
            jobs = []
            dict = soup.find('div', attrs={'data':True})
            predict = json.loads(dict['data'])
            searchData = predict['searchResult']['job_offers']
            current_time = datetime.now().timestamp()
            for job in searchData:
                title = job['job_offer']['title']
                description = job['job_offer']['description_digest']
                posted_at = job['job_offer']['last_released_at']
                posted = datetime.fromisoformat(posted_at.replace('Z', '+00:00')).timestamp()
                avatar = 'https://crowdworks.jp/' + job['client']['user_picture_url']
                client = job['client']['username']
                link = 'https://crowdworks.jp/public/jobs/' + str(job['job_offer']['id'])
                # Skip if already seen and posted more than 2 hours ago
                if current_time - 7200 > posted:
                    continue
                if link in self.seen:
                    continue

                # Filter by keyword
                if self.keywords:
                    if not any(kw in title.lower() for kw in self.keywords):
                        continue

                self.seen.add(link)
                jobs.append((title, link, description, posted_at, avatar, client))
            return jobs
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {e}")
            return []

    def send_to_discord(self, jobs):
        for title, link, description, posted_at, avatar, client in jobs:
            payload = {
                "content": f"🌌 **{title}**\n🔗 {link}",
                "embeds": [
                    {
                        "title": title,
                        "url": link,
                        "description": description,
                        "author": {
                            "name": client,
                            "icon_url": avatar
                        },
                        "fields": [
                            {
                                "name": "Posted At",
                                "value": posted_at,
                                "inline": True
                            }
                        ]
                    }
                ]
            }
            requests.post(self.webhook_url, json=payload)
            self.log_signal.emit(f"✅ Sent to Data in Discord Channel: {title}")

    def run(self):
        while self.running:
            jobs = self.fetch_jobs()
            if jobs:
                self.send_to_discord(jobs)
            else:
                self.log_signal.emit("🔍 No new jobs found.")
            time.sleep(self.interval)
