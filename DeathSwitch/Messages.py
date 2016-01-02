
#Store the messages to be sent out and export as a variable

from email.mime.text import MIMEText

sara_message_text = """

If you are reading this Sara, it means the second test was successful.

"""

sara_message = MIMEText(sara_message_text)
sara_message.add_header("To","*****@gmail.com")
sara_message.add_header("Subject","I have some more news")


msgs = [sara_message]
