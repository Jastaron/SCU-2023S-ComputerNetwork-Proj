from datetime import datetime
from smtplib import SMTP
from imaplib import IMAP4_SSL, IMAP4, Commands
from email import message_from_bytes
from email.header import decode_header, make_header, Header
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import filedialog
from bs4 import BeautifulSoup
from lib import *


class EmailModel:
    inbox_emails_h = None  # 收件箱header列表
    drafts_h = None  # 草稿箱header列表
    attachments = []  # 附件列表
    # smtp字典
    smtp_dict = {
        'qq.com': {
            'server': 'smtp.qq.com'
        },
        '163.com': {
            'server': 'smtp.163.com'
        },
        '126.com': {
            'server': 'smtp.126.com'
        }
    }
    # imap字典
    imap_dict = {
        'qq.com': {
            'server': 'imap.qq.com',
            'draft': 'Drafts'
        },
        '163.com': {
            'server': 'imap.163.com',
            'draft': '&g0l6P3ux-'
        },
        '126.com': {
            'server': 'imap.126.com',
            'draft': '&g0l6P3ux-'
        }
    }

    # 初始化方法
    def __init__(self, user_id, mandate):
        self.user_id = user_id
        self.mandate = mandate
        self.server_name = self.user_id.split('@')[1]
        self.smtp_server = None
        self.imap_server = None

    # 登录
    def login(self):
        try:
            # smtp连接
            self.smtp_server = SMTP(self.smtp_dict[self.server_name]['server'], 25)
            self.smtp_server.login(self.user_id, self.mandate)
            # imap连接
            if any(i == self.server_name for i in ['126.com', '163.com']):
                Commands['ID'] = ('AUTH')
            self.imap_server = IMAP4_SSL(self.imap_dict[self.server_name]['server'], 993)
            self.imap_server.login(self.user_id, self.mandate)
            if any(i == self.server_name for i in ['126.com', '163.com']):
                args = (
                "name", self.user_id.split('@')[0], "contact", self.user_id, "version", "1.0.0", "vendor", "myclient")
                typ, dat = self.imap_server._simple_command('ID', '("' + '" "'.join(args) + '")')
                self.imap_server._untagged_response(typ, dat, 'ID')
            # print(self.imap_server.list())
            return True
        except:
            return False

    # 获得指定邮箱header列表
    def get_clicked_box_emails(self, state):
        self.imap_server.select(self.get_email_box(state))
        if state == INBOX_STATE:
            return self.inbox_emails_h
        elif state == DRAFT_STATE:
            return self.drafts_h
        else:
            return []

    # 获得邮箱header
    def get_email_header(self, email_id):
        try:
            # print(email_id)
            data = self.imap_server.fetch(email_id, 'BODY[header]')[1]
            msg = message_from_bytes(data[0][1])
            msg_subject = make_header(decode_header(msg['Subject']))
            msg_from = make_header(decode_header(msg['From']))
            msg_to = make_header(decode_header(msg['To']))
            msg_date, msg_time_stamp = self.get_email_date(msg['Date'])
            msg_eid = email_id
            return f"Subject: {msg_subject}{' ' * 4}e_id: {msg_eid}\nFrom: {msg_from}{' ' * 4}To: {msg_to}\nDate: {msg_date}{' ' * 4}", msg_time_stamp
        except UnicodeDecodeError:
            # print("get header fail")
            return None, None

    # 获得邮件日期
    def get_email_date(self, date):
        utcstr = date
        try:
            if date is None:
                return 'None', None
            if 'GMT' in utcstr:
                utcdatetime = datetime.strptime(utcstr, '%a, %d %b %Y %H:%M:%S %z (GMT)')
            elif 'CDT' in utcstr:
                utcdatetime = datetime.strptime(utcstr, '%a, %d %b %Y %H:%M:%S %z (CDT)')
            else:
                utcdatetime = datetime.strptime(utcstr, '%a, %d %b %Y %H:%M:%S %z')
            local_time_stamp = utcdatetime.timestamp()
            return utcdatetime, local_time_stamp
        except:
            return None, None

    # 获得邮件body
    def get_email_body(self, email_id):
        self.attachments.clear()
        data = self.imap_server.fetch(email_id, '(RFC822)')[1]
        msg = message_from_bytes(data[0][1])
        default_code = decode_header(msg['Subject'])[0][1]
        if default_code is None:
            default_code = 'utf-8'
        result = ""
        body_tag = False
        for part in msg.walk():
            file_name = part.get_filename()
            if file_name:
                dh = decode_header(Header(file_name))
                filename = dh[0][0]
                if dh[0][1]:
                    filename = self.decode_str(str(filename, dh[0][1]))
                data = part.get_payload(decode=True)
                self.attachments.append([filename, data])
            if not part.get_param("name") and body_tag is False:
                content_type = part.get_content_type()
                if content_type == 'text/plain':  # 如果内容为text/plain就直接提取
                    try:
                        result = str(part.get_payload(decode=True), default_code)
                    except:
                        result = str(part.get_payload(decode=True), 'utf-8')
                    body_tag = True
                elif content_type == 'text/html':  # 如果内容为text/html就要进行处理
                    try:
                        html = str(part.get_payload(decode=True), part.get('content-type').split('=')[1])
                    except:
                        try:
                            html = str(part.get_payload(decode=True), default_code)
                        except:
                            try:
                                html = str(part.get_payload(decode=True), 'utf-8')
                            except:
                                html = str(part.get_payload())
                    soup = BeautifulSoup(html, 'lxml')
                    divs = soup.select('body')
                    for d in divs:
                        text = d.get_text(strip=True, separator='\n')
                        result += text
                    body_tag = True
        return result

    # 解码字符串
    def decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    # 获得邮件附件
    def get_attachments(self, email_id):
        data = self.imap_server.fetch(email_id, 'BODYSTRUCTURE')[1]
        msg = message_from_bytes(data[0])
        try:
            fn_list = msg.get_payload().split('"filename"')
            if len(fn_list) == 1:
                return ''
            fn_list = fn_list[1:]
            att_str = ''
            for fn in fn_list:
                filename = self.decode_str(fn.split('"')[1])
                att_str += f'{filename}\n'
            return att_str
        except:
            return ''

    # 下载附件
    def download_attachments(self, filepath):
        if len(self.attachments) > 0:
            for filename, data in self.attachments:
                with open(f"{filepath}//{filename}", 'wb') as att_file:
                    att_file.write(data)
                    att_file.close()

    # 获得邮件信息（内容）
    def get_email_information(self, email_id, email_h):
        try:
            msg_att = self.get_attachments(email_id)
            msg_body = self.get_email_body(email_id)
            msg_content = f"{email_h}\n" \
                          f"{EMAIL_CONTENT_LINE}" \
                          f"{msg_body}\n" \
                          f"{EMAIL_ATTACHMENT_LINE}" \
                          f"{msg_att}" \
                          f"{EMAIL_END_LINE}"
            return msg_content
        except:
            return None

    # 获得指定邮箱邮件（header列表的初始化）
    def get_selected_box_emails(self, imap_select_str):
        try:
            # 选择收件箱
            self.imap_server.select(imap_select_str)
            # print('imap select done')
            # 搜索收件箱中的邮件
            result, data = self.imap_server.search(None, 'ALL')
            # print('imap search done')
            email_ids = data[0].split()

            emails_h = []
            emails_t = []
            cnt = 0
            # 获取邮件详情
            for i in range(len(email_ids) - 1, 0, -1):
                try:
                    if cnt > MAIL_BOX_MAX:
                        break
                    msg_head, msg_time_stamp = self.get_email_header(email_ids[i])
                    if msg_time_stamp is None:
                        continue
                    emails_h.append(msg_head)
                    emails_t.append(msg_time_stamp)
                    cnt += 1
                except:
                    continue

            if len(emails_t) > 0:
                ts_sort = sorted(emails_t, reverse=True)
                ts_i = [emails_t.index(i) for i in ts_sort]
                emails_h = [emails_h[ts_i[i]] for i in range(len(emails_t))]
            return emails_h
        except IMAP4.error as e:
            # print(e)
            return []

    # header列表初始化
    def get_init_e_list(self):
        self.inbox_emails_h = self.get_selected_box_emails(self.get_email_box(INBOX_STATE))
        self.drafts_h = self.get_selected_box_emails(self.get_email_box(DRAFT_STATE))

    # 获得邮件细节
    def get_email_details(self, email_h, state):
        b_e_id = self.get_email_id(email_h, state)
        return self.get_email_information(b_e_id, email_h)

    # 获得哪个邮箱
    def get_email_box(self, state):
        if state == INBOX_STATE:
            return 'INBOX'
        elif state == DRAFT_STATE:
            return self.imap_dict[self.server_name]['draft']
        elif state == SENT_STATE:
            return self.imap_dict[self.server_name]['sent']

    # 获得邮件id
    def get_email_id(self, email_h, state):
        self.imap_server.select(self.get_email_box(state))
        result, data = self.imap_server.search(None, 'ALL')
        email_ids = data[0].split()
        email_ids_str = [str(i) for i in email_ids]
        e_id = email_h.split('e_id: ')[1].split('\n')[0]
        if e_id not in email_ids_str:
            # print('error')
            return None
        b_e_id = email_ids[email_ids_str.index(e_id)]
        return b_e_id

    # 下载邮件
    def download_email(self, email_h, email_c, state):
        b_e_id = self.get_email_id(email_h, state)
        if b_e_id is None:
            return False
        file_path = filedialog.askdirectory()  # 询问用户打开哪个文件夹
        if file_path == '':
            return False
        try:
            with open(f'{file_path}//{str(b_e_id)}.txt', 'w') as content_txt:
                content_txt.write(email_c)
                content_txt.close()
            self.download_attachments(file_path)
            return True
        except:
            return False

    # 删除邮件
    def delete_email(self, email_h, state):
        b_e_id = self.get_email_id(email_h, state)
        if b_e_id is None:
            return False
        try:
            self.imap_server.store(b_e_id, "+FLAGS", "\\Deleted")
            self.imap_server.expunge()
            if state == INBOX_STATE:
                self.inbox_emails_h.remove(email_h)
            elif state == DRAFT_STATE:
                self.drafts_h.remove(email_h)
            return True
        except:
            # print("no")
            return False

    # 发送邮件
    def send_email(self, To, Subject, Content):
        # print(To == '', 'no')
        # print(To == None, 'None')
        if To == '':
            return False

        attachments_tag = False
        attachments_list = []
        if EMAIL_ATTACHMENT_LINE in Content:
            attachments_tag = True
            content = Content.split(EMAIL_ATTACHMENT_LINE)[0]
            try:
                attachments_list = Content.split(EMAIL_ATTACHMENT_LINE)[1] \
                                       .split(EMAIL_END_LINE)[0] \
                                       .split('\n')[:-1]
            except:
                return False
        else:
            content = Content
        content = MIMEText(content, 'plain', 'utf-8')

        if attachments_tag:  # 如果有附件就要处理附件内容
            msg = MIMEMultipart()
            msg.attach(content)
            for fp in attachments_list:
                try:
                    if any([i in fp for i in IMAGE_TYPE]):
                        imageApart = MIMEImage(open(fp, 'rb').read(), fp.split('.')[-1])
                        imageApart.add_header('Content-Disposition', 'attachment', filename=fp.split('/')[-1])
                        msg.attach(imageApart)
                    else:
                        fileApart = MIMEApplication(open(fp, 'rb').read())
                        fileApart.add_header('Content-Disposition', 'attachment', filename=fp.split('/')[-1])
                        msg.attach(fileApart)
                except:
                    return False
        else:
            msg = content
        msg['From'] = self.user_id
        msg['To'] = To
        msg['Subject'] = Subject

        try:
            self.smtp_server.sendmail(self.user_id, msg['To'], msg.as_string())
            return True
        except:
            return False

    # 添加附件
    def attach_file(self, content):
        try:
            if EMAIL_ATTACHMENT_LINE not in content:
                new_content = content + '\n\n'
                new_content += EMAIL_ATTACHMENT_LINE
            else:
                new_content = content.split(EMAIL_END_LINE)[-2]
            attach_list = filedialog.askopenfilenames()
            for a in attach_list:
                if a in new_content:
                    continue
                new_content += f'{a}\n'
            new_content += EMAIL_END_LINE
            return new_content
        except:
            return None

    # 关闭smtp连接
    def close_smtp_server(self):
        self.smtp_server.quit()

    # 关闭imap连接
    def close_imap_server(self):
        self.imap_server.logout()