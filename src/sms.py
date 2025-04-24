#!/usr/bin/env python3
import smtplib, ssl
import cv2
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def run_sms(picture, temperature, time, detections):
  print("SENDING SMS")
  msg = MIMEMultipart("mixed")
  msg["Subject"] = "⚠️[GUARDIAN EYES] - ATTENTION⚠️ "
  msg["From"] = "troytran000@gmail.com"
  msg["To"] = "troytran000@gmail.com"

  html = """\
  <html>
    <body>
      <b>
        ⚠️⚠️⚠️⚠️⚠️ Subjects detected in your car ⚠️⚠️⚠️⚠️⚠️
      </b>
      <p>
        Did you forget to check your rear passenger seat for <b>{detections}</b>
      </p>
      <p>
        Time (CST): <b>{time} </b>
      </p>
      <p>
        Car Temperature: <b>{temperature} F </b>
      </p>

    </body>
  </html>"""
  filled = html.format(time=time, temperature=temperature, detections=detections)

  part2 = MIMEText(filled, "html")

  _, buffer = cv2.imencode(".jpg", picture)
  image_data = buffer.tobytes()
  img = MIMEImage(image_data, name=time)

  msg.attach(part2)
  msg.attach(img)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login("troytran000@gmail.com", "bjww cqkd uosg brbx")
    server.sendmail(
      msg["From"], msg["To"], msg.as_string()
    )

