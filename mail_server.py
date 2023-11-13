import imaplib

# 邮件代理服务器的配置
IMAP_SERVER = 'imap.qq.com'
IMAP_PORT = 993

# 邮箱登录凭据
EMAIL_ADDRESS = '1723181893@qq.com'
PASSWORD = '030415Jastaron'

# 连接到邮件代理服务器
def connect_to_server():
    server = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    server.login(EMAIL_ADDRESS, PASSWORD)
    return server

# 获取邮件列表
def get_mail_list(server):
    server.select('INBOX')  # 选择收件箱
    typ, data = server.search(None, 'ALL')  # 搜索所有邮件
    mail_ids = data[0].split()
    return mail_ids

# 下载邮件附件
def download_attachment(server, mail_id, save_path):
    typ, data = server.fetch(mail_id, '(BODY.PEEK[])')  # 获取邮件内容
    if typ == 'OK':
        for response_part in data:
            if isinstance(response_part, tuple):
                content = response_part[1]
                if content and b'Content-Disposition: attachment' in content:
                    # 解析附件信息
                    filename_start = content.find(b'filename="') + len(b'filename="')
                    filename_end = content.find(b'"', filename_start)
                    filename = content[filename_start:filename_end].decode()

                    # 保存附件
                    with open(save_path + filename, 'wb') as f:
                        f.write(content)
                    print(f'Saved attachment: {filename}')
                    return

# 删除邮件
def delete_mail(server, mail_id):
    server.store(mail_id, '+FLAGS', '\\Deleted')
    server.expunge()

# 断开与邮件代理服务器的连接
def disconnect_from_server(server):
    server.logout()

# 主函数
def main():
    # 连接到邮件代理服务器
    server = connect_to_server()

    # 获取邮件列表
    mail_ids = get_mail_list(server)

    # 遍历邮件列表
    for mail_id in mail_ids:
        # 下载附件
        download_attachment(server, mail_id, 'attachments/')

        # 删除邮件
        delete_mail(server, mail_id)

    # 断开与邮件代理服务器的连接
    disconnect_from_server(server)

if __name__ == '__main__':
    main()
