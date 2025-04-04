#!/usr/bin/env python3
import smtplib, ssl
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def run_sms():
  msg = MIMEMultipart("alternative")
  msg["Subject"] = "test"
  msg["From"] = "troytran000@gmail.com"
  msg["To"] = "troytran000@gmail.com"

  txt = f"""\
  ⚠️⚠️⚠️⚠️⚠️ Subjects detected in your car ⚠️⚠️⚠️⚠️⚠️
  
  Did you forget to check your rear passenger seat?



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
  with open("", "rb") as f:
    img = MIMEImage(f.read())
    img.add_header("Content-Disposition", "attachment", filename="")
    msg.attach(img)

  msg.attach(part1)
  msg.attach(part2)
  msg.attach(img)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login("troytran000@gmail.com", "uxps mtjy yeoj ylml")
    server.sendmail(
      "troytran000@gmail.com", "troytran000@gmail.com", msg.as_string()
    )




run_sms()
