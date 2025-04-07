#!/usr/bin/env python3
import smtplib, ssl
import cv2
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def run_sms(picture, temperature, time):
  print("SENDING SMS")
  msg = MIMEMultipart("mixed")
  msg["Subject"] = "test"
  msg["From"] = "troytran000@gmail.com"
  msg["To"] = "6825606828@tmomms.net"

  txt = f"""\
  ⚠️⚠️⚠️⚠️⚠️ Subjects detected in your car ⚠️⚠️⚠️⚠️⚠️
  
  Did you forget to check your rear passenger seat?

  Time (CST): {time} 
  Car Temperature: {temperature} F

  """

  html = """\
  <html>
    <body>
      <p>
        test
      </p>
      <p>
        this is a test
      </p>
      <img src="https://i.pinimg.com/736x/c7/4a/82/c74a824818e364e84ca34a8ba39df661.jpg"/>
    </body>
  </html>"""

  part1 = MIMEText(txt, "plain")
  part2 = MIMEText(html, "html")

  _, buffer = cv2.imencode(".jpg", picture)
  image_data = buffer.tobytes()
  img = MIMEImage(image_data, name=time)

  msg.attach(part1)
  msg.attach(part2)
  msg.attach(img)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login("troytran000@gmail.com", "jsus lvxh nljk gtxv")
    server.sendmail(
      msg["From"], msg["To"], msg.as_string()
    )

