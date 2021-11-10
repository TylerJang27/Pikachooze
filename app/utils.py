import smtplib
from smtplib import SMTPException

def send_new_pass(email, password):
    sender = 'tylerjang27@gmail.com'
    receivers = ['tylerjang27@gmail.com']

    message = """From: From Person <tylerjang27@gmail.com>
    To: To Person <tylerjang27@gmail.com>
    Subject: SMTP e-mail test

    This is a test e-mail message.
    """

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message)         
        print("Successfully sent email")
    except Exception:
        print("Error: unable to send email")
    return
    