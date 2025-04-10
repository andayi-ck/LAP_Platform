import os
import smtplib
import ssl
from email.message import EmailMessage

email_sender = 'magero833@gmail.com'
email_password = "gdtd gmuk bddl retb"
email_receiver = 'andayi.ck@gmail.com'



subject = 'Account Creation Successfull!'
body = """
Click the Link below and sign up to receive daily Notifications: https://www.google.com
"""

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, em.as_string())
print("Email sent successfully!")

