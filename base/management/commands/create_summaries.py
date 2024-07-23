# base/management/commands/create_summaries.py

from django.core.management.base import BaseCommand
from base.models import Room
from django.conf import settings
from django.core.mail import send_mail
from base.models import Message
from groq import Groq  # Assuming you have installed and configured the Groq library

client = Groq(api_key="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")

def generate_summary(messages):
    # Function to generate a summary using Groq
    content = "\n".join(message.body for message in messages)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": f"Please provide a summary of:\n{content}"}
        ],
        model="llama3-8b-8192",  # Adjust model as per your Groq setup
    )
    if chat_completion.choices:
        summary = chat_completion.choices[0].message.content
    else:
        summary = "Summary generation failed."
    return summary

def send_summary_to_host(summary, host_email):
    # Function to send summary via email
    subject = 'Summary of Recent Messages'
    message = summary
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [host_email]
    send_mail(subject, message, from_email, recipient_list)

class Command(BaseCommand):
    help = 'Creates summaries of messages in rooms and sends them to hosts.'

    def handle(self, *args, **options):
        rooms = Room.objects.all()

        for room in rooms:
            messages = room.message_set.all()  # Adjust to read last messages

            if len(messages) > 0:
                summary = generate_summary(messages)
                send_summary_to_host(summary, room.host.email)
                self.stdout.write(self.style.SUCCESS(f'Summary sent to {room.host.email}'))
