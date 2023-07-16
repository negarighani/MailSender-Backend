from celery import Celery
from email.message import EmailMessage
import ssl
import smtplib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Letter
from datetime import datetime, timedelta

celery = Celery("tasks", broker="redis://localhost:6379/0")

engine = create_engine("")
Session = sessionmaker(bind=engine)
email_sender = ''
email_password = ''

@celery.task
def send_letter_task(serialized_letter, recipients):
    letter_id = serialized_letter["id"]
    letter_subject = serialized_letter["subject"]
    letter_content = serialized_letter["content"]
    letter_categories = serialized_letter["categories"]

    session = Session()

    for recipient_email in recipients:
        print(recipient_email)
        user = session.query(User).filter(User.email == recipient_email).first()
        print(user)
        if user:
            user_categories = [category.id for category in user.categories]
            print(user_categories)
            print(letter_categories)
            common_categories = set(user_categories).intersection(letter_categories)
            if common_categories:
                print("common")
                letter = session.query(Letter).filter(Letter.id == letter_id).first()
                if letter:
                    print("letter")
                    user.letters.append(letter)
            try:
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = recipient_email
                em['Subject'] = letter_subject
                em.set_content(letter_content)

                context = ssl.create_default_context()
            
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, recipient_email, em.as_string())
            except smtplib.SMTPException as e:
                print(f"Error sending email: {str(e)}")

    session.commit()
    session.close()
    
@celery.task
def send_letters_task(user_id, time):
    session = Session()
    user = session.query(User).get(user_id)

    if user is None:
        print(f"User with ID {user_id} not found.")
        return

    # Calculate the datetime threshold based on the provided time
    now = datetime.now()
    if time == "past_minute":
        threshold = now - timedelta(minutes=1)
    elif time == "past_hour":
        threshold = now - timedelta(hours=1)
    elif time == "past_day":
        threshold = now - timedelta(days=1)
    elif time == "past_month":
        threshold = now - timedelta(days=30)
    else:
        print(f"Invalid time option: {time}")
        return
    
    letters = session.query(Letter).filter(
        Letter.created_time >= threshold)

    if not letters:
        print(f"No letters found for user {user_id} within the specified time.")
        return

    recipients = [user.email]

    for letter in letters:
        serialized_letter = {
            "id": letter.id,
            "subject": letter.subject,
            "content": letter.content,
            "categories": [category.id for category in letter.categories]
        }
        send_letter_task(serialized_letter, recipients)

    print(f"Letters sent to user {user_id} within the specified time.")

    session.close()

