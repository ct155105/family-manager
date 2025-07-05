import base64
from email.message import EmailMessage
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose"
]


def get_gmail_creds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def gmail_create_draft(to: str, subject: str, body: str, html: str = None) -> dict:
    """
    Create and insert a draft email. Print the returned draft's message and id.
    Args:
        to (str): Recipient email address.
        subject (str): Email subject.
        body (str): Email body text (plain text).
        html (str, optional): HTML content for the email. If provided, sends a multipart email.
    Returns:
        dict: Draft object, including draft id and message meta data, or None if error.
    """
    creds = get_gmail_creds()
    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()
        message["To"] = to
        message["From"] = "christeuschler@gmail.com"
        message["Subject"] = subject
        message.set_content(body)
        if html:
            message.add_alternative(html, subtype="html")
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"message": {"raw": encoded_message}}
        draft = (
            service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )
        print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
        return draft
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def gmail_send_message(to: str, subject: str, body: str, html: str = None) -> dict:
    """
    Sends an email using the Gmail API.
    Args:
        to (str): Recipient email address.
        subject (str): Email subject.
        body (str): Email body text (plain text).
        html (str, optional): HTML content for the email. If provided, sends a multipart email.
    Returns:
        dict: Sent message metadata or None if error.
    """
    creds = get_gmail_creds()
    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()
        message["To"] = to
        message["From"] = "christeuschler@gmail.com"
        message["Subject"] = subject
        message.set_content(body)
        if html:
            message.add_alternative(html, subtype="html")
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}
        sent_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Sent message id: {sent_message["id"]}')
        return sent_message
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def test_client():
    """Shows basic usage of the Gmail API. Lists the user's Gmail labels."""
    creds = get_gmail_creds()
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        if not labels:
            print("No labels found.")
            return
        print("Labels:")
        for label in labels:
            print(label["name"])
    except HttpError as error:
        print(f"An error occurred: {error}")


# test_client()
# # draft = gmail_create_draft()
# # print(draft)
# gmail_send_message(
#     to="christeuschler@gmail.com",
#     subject="Test HTML Email",
#     body="This is the plain text version of the email.",
#     html="""
#     <html>
#       <body>
#         <h1>This is an HTML Email</h1>
#         <p>You can use <b>HTML markup</b> here!</p>
#       </body>
#     </html>
#     """
# )
# print("Email sent successfully.")