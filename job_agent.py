from playwright.sync_api import sync_playwright
import requests
import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_alert(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })


def check_jobs():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # open portal
        page.goto("https://tai.thetapacademy.com")

        # login
        page.locator("text=Login with Email").click()

        page.locator("input[type='email']").fill(EMAIL)
        page.locator("input[type='password']").fill(PASSWORD)

        page.locator("button:has-text('Continue')").click()

        page.wait_for_timeout(3000)

        # open jobs page
        page.goto("https://tai.thetapacademy.com/jobs")

        # wait until job cards appear
        page.wait_for_selector("text=TAP-JOB-ID")

        # select job cards
        jobs = page.locator("div:has-text('TAP-JOB-ID')")

        count = jobs.count()

        #print("Total job cards:", count)

        open_jobs = []

        for i in range(count):
            job = jobs.nth(i)
            text = job.inner_text()

            if "Open" in text and "Closed" not in text:

                lines = text.split("\n")

                # remove empty lines
                lines = [l.strip() for l in lines if l.strip()]

                job_id = lines[0]

                ends = next((l for l in lines if "Ends in" in l), "")
                role = next((l for l in lines if "Engineer" in l or "Developer" in l or "Analyst" in l), "")
                location = next((l for l in lines if "Bengaluru" in l or "Hyderabad" in l or "Chennai" in l), "")
                salary = next((l for l in lines if "LPA" in l), "")
                qualification = next((l for l in lines if "B.Tech" in l or "M.Tech" in l or "BCA" in l or "MCA" in l), "")

                message = f"""
🚨 NEW TAP ACADEMY JOB OPENING

🆔 Job ID: {job_id}
💼 Role: {role}
📍 Location: {location}
💰 Salary: {salary}
🎓 Qualification: {qualification}
⏳ {ends}
"""

                open_jobs.append(message)


        # send message only if open job exists
        if open_jobs:

            message = "🚨 Tap Academy Job Open\n\n"

            for job in open_jobs:
                send_alert(job)

            print("Telegram alert sent")

        else:

            send_alert("ℹ️ Tap Academy Update\n\nNo job openings available right now.")
            
            print("No open jobs")

        browser.close()

check_jobs()
