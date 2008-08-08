# pyPentago - a board game
# Copyright (C) 2008 Florian Mayer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
This module is intended to supply functions to send emails.
"""


import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid, getaddresses
from email.header import Header


def format_recipients(recipients):
    """
    format_recipients(recipients) -> list
    
    Attempts to format elements of recipients according to (name, email), if the
    element is not an iterable, it is inserted as is.
    
    Returns list of strings containing email addresses that can be used in 
    email headers, mind that a separator is needed in the header.
    
    >>> format_recipients(
    ...     (
    ...         ("Florian Mayer", "myemail@address.com"), 
    ...         ("Florian Mayer", "otheremail@address.com"), 
    ...         "foo@bar.com"
    ...     )
    ... )
    ['Florian Mayer <myemail@address.com>', 
    'Florian Mayer <otheremail@address.com>', 'foo@bar.com']
    """
    if not hasattr(recipients, "__iter__"):
        return [recipients]

    ret = []
    for recipient in recipients:    
        if not hasattr(recipient, "__iter__"):
            ret.append((False, recipient))
        else:
            ret.append(recipient)
    return [formataddr(pair) for pair in ret]


class Email:
    def __init__(self, sender, recipients, subject="No Subject", content="", 
                 reply_to=False, copy_recipients=False, blind_copy=False, 
                 content_type="plain", encoding="us-ascii"):
        """
        Create a new email from sender to recipients.
        """
        # Save original sender and recipient list for send():
        self.sender = sender
        self.recipients = recipients
        
        content = content.encode(encoding)
        self.mail = MIMEText(content, content_type, encoding)
        self.mail['From'] = sender
        self.mail['To'] = ", ".join(format_recipients(recipients))
        # Encode subject:
        self.mail['Subject'] = Header(subject, encoding)
        self.mail['Date'] = formatdate(usegmt=True)
        self.mail['Message-ID'] = make_msgid()
        if reply_to:
            self.mail['ReplyTo'] = reply_to
        if copy_recipients:
            self.mail['CC'] = ', '.join(format_recipients(copy_recipients))
        if blind_copy:
            self.mail['BCC'] = ', '.join(format_recipients(blind_copy))

    def send(self, host, port=25, user=False, password=False):
        """
        Send the email via SMTP on host:port. Supply user and password if 
        SMTP server requires login.
        """
        message = self.mail.as_string()
        # Filter unnecessary information, the realname, out of the recipients
        recipients = getaddresses(format_recipients(self.recipients))
        recipients = [x[1] for x in recipients]    
        # Filter unnecessary information out of the sender
        sender = getaddresses(format_recipients(self.sender))
        sender = sender[0][1]
    
        server = smtplib.SMTP(host, port)
        if user and password:
            server.login(user, password)
        server.sendmail(sender, recipients, message)

