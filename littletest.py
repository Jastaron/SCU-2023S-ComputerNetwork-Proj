import email
import imaplib

user_id = '1723181893@qq.com'
mandate = 'vpdejvhyyglbebgg'


def decode_str(s):
    value, charset = email.header.decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

if __name__ == '__main__':
    imap_server = imaplib.IMAP4_SSL('imap.qq.com', 993)
    imap_server.login(user_id, mandate)

    imap_server.select('INBOX')

    result, data = imap_server.fetch(b'543', 'BODY[2]')

    print(data[0][1].decode('utf-8'))



