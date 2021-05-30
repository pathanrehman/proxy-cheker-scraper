import smtplib
from email.message import EmailMessage

# Don't put a space before the text. Fix typos.
mail_content = '''This is to inform that your stock is empty.
Please Check the stock list and refill the stock'''

#The mail addresses and password
def email_alert(receiver_address):
    sender_address = 'inventorymangement.a@gmail.com'
    sender_pass = '@Rehman2002'
    # Comment out, utterly pointless
    # receiver_address = receiver_address

    message = EmailMessage()    
    message['From'] = sender_address
    message['to'] = receiver_address
    # Don't lie i the subject
    message['Subject'] = 'Alert Your Inventory Stock Is Low'
    message.set_content(mail_content)

    # Use a context manager
    with smtplib.SMTP('smtp.gmail.com', 587) as session:
        # EHLO is required ... twice
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(sender_address, sender_pass)
        # Prefer send_message
        session.send_message(message)
    # Probably don't print anything
    print('Mail Sent')
    