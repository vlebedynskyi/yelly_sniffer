#! /usr/bin/python

import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

SMTP_SERVER = "smtp.gmail.com"


def send(sender, sender_pass, recipient, title, content, image):
    # me == my email address
    # you == recipient's email address

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = recipient

    # Create the body of the message (a plain-text and an HTML version).
    # text = "Привет. Это русское сообщение.. Я думаю все будет окей"
    # html = """\
    # <html>
    #   <head></head>
    #   <body>
    #     <p>Hi!<br>
    #        How are you?<br>
    #        Here is the <a href="http://www.python.org">link</a> you wanted.
    #     </p>
    #   </body>
    # </html>
    # """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(title, 'plain')
    part2 = MIMEText(content, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    if image is not None:
        with open(image, 'rb') as file:
            img_data = file.read()
            msg.attach(MIMEImage(img_data, name=os.path.basename(image)))


    # AUTH TO REMOTE SERVER
    server = smtplib.SMTP(SMTP_SERVER, 587)
    server.starttls()
    server.login(sender, sender_pass)

    # Send the message via local SMTP server.
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    server.sendmail(sender, recipient, msg.as_string())
    server.quit()
