import base64
import requests

from django.template.loader import render_to_string

from sendgrid import SendGridAPIClient, FileContent, FileType, FileName, Disposition, ContentId
from sendgrid.helpers.mail import Mail, Attachment, MimeType, From

from moneyball.settings import SENDGRID_API_KEY, FROM_EMAIL


def email_send(subject, template, recipient, context, file_name=None):
    msg_html = render_to_string(template, context)
    message = Mail(
        from_email=From(FROM_EMAIL, "AutoXP"),
        to_emails=recipient,
        subject=subject,
        html_content=msg_html)
    if file_name:
        file_path = requests.get(file_name).content
        encoded = base64.b64encode(file_path).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        # attachment.file_type = FileType('application/pdf')
        extension = file_name.split('.')[-1]
        attachment.file_name = FileName('AutoXP_Attachment.' + extension)
        attachment.disposition = Disposition('attachment')
        attachment.content_id = ContentId('Example Content ID')
        message.attachment = attachment
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        pass
