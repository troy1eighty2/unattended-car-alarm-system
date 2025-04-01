#!/usr/bin/env python3
import smtplib
from email.message import EmailMessage

def run_sms():
  msg = EmailMessage()

  msg.set_content("Lets get a bag")
  msg["From"] = "troytran000@gmail.com"
  msg["To"] = "6825606828@tmomail.net"
  msg["Subject"] = "Test"

  server = smtplib.SMTP("smtp.gmail.com", 587)
  server.starttls()
  server.login("troytran000@gmail.com", "waqc jhqo ybmv igcl")

  server.send_message(msg)
  server.quit()



run_sms()
