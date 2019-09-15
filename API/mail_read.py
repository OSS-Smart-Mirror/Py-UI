import re

def get_mails():
    # Returns Sender, Date, Subject of last 5 emails
    regexstr = r'From: (.*) <.*?>\nDate:(.*)\nMessage.*\nSubject: (.*)\n'
    with open("/var/mail/477grp1", "r") as mail_file:
        text = mail_file.read()
    mail_list = re.findall(regexstr, text)
    return mail_list[-5:]

if __name__ == "__main__":
    print(get_mails())
