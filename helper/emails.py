import ssl
import smtplib
from datetime import datetime
from email.utils import formataddr
from email.message import EmailMessage
from django.template.loader import render_to_string
from moneyball.settings import SMTP_SENDER_EMAIL, SMTP_SENDER_LOGIN, SMTP_SENDER_NAME, SMTP_SENDER_PASSWORD


def email_send(subject, template, recipient, context, cc_email=None, bcc_email=None, file_name=None, payload=None):
    try:
        global SMTP_SENDER_EMAIL, SMTP_SENDER_LOGIN, SMTP_SENDER_NAME, SMTP_SENDER_PASSWORD
        msg_html = render_to_string(template, context)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = formataddr((SMTP_SENDER_NAME, SMTP_SENDER_EMAIL))
        msg['To'] = recipient
        if cc_email is not None and len(cc_email) > 0:
            msg ['CC'] = cc_email
        if bcc_email is not None and len(bcc_email) > 0:
            msg ['BCC'] = bcc_email
            
        args ={
            "from_email": SMTP_SENDER_EMAIL,
            "email_sent_time": str(datetime.now()),
            "subject": subject
        }

        if payload is not None: 
            for p_key, p_value in payload. items ():
                args [p_key] = p_value
        
        msg['custom_args'] = str(args)
        msg.set_content(msg_html, subtype='html')
        context = ssl.create_default_context()
        with smtplib.SMTP('smtp-relay.brevo.com', 587) as smtp:
            smtp.ehlo() # Can be omitted, called implicitly by the method if required
            smtp.starttls(context=context)
            smtp.ehlo() # Can be omitted, called implicitly by the method if required
            smtp.login(SMTP_SENDER_LOGIN, SMTP_SENDER_PASSWORD) 
            smtp.send_message(msg)
            smtp.quit()
            status = True
    except Exception as e:
        print(f"SMTP send email Error: {subject} : {str(e)}")
        print(f"SMTP: Additional Details: TO_EMAIL: {recipient} : FROM_EMAIL: {SMTP_SENDER_NAME}")
        status = False
    return status