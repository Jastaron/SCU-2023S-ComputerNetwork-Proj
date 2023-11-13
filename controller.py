from model import *
from view import *
from lib import *

class EmailController(QObject):
    state = INBOX_STATE
    model = None
    view = None

    def __init__(self):
        super().__init__()

        # 创建view对象
        self.view = EmailView()

        # 将view的信号与自身方法连接
        self.view.login_signal.connect(self.login)
        self.view.login_init_signal.connect(self.get_init_all_emails)
        self.view.show_inbox_signal.connect(self.get_inbox)
        self.view.show_drafts_signal.connect(self.get_drafts)
        self.view.show_email_details_signal.connect(self.get_email_details)
        self.view.download_email_signal.connect(self.download_email)
        self.view.attach_file_signal.connect(self.attach_file)
        self.view.send_email_signal.connect(self.send_email)
        self.view.delete_email_signal.connect(self.delete_email)

        # 展示
        self.show()

    # 页面展示
    def show(self):
        self.view.show()

    # 设置状态
    def set_state(self,state):
        self.state = state

    # 登录函数
    def login(self, user_id, mandate):
        if user_id == '' or mandate == '':
            self.view.login_done(False)
            return

        # 根据用户输入的邮箱和密码，创建model对象
        self.model = EmailModel(user_id, mandate)
        success = self.model.login()
        self.view.login_done(success)

    # 初始化邮箱
    def get_init_all_emails(self):
        self.model.get_init_e_list()
        self.view.login_init_done()

    # 获得指定邮箱
    def get_selected_box_emails(self, select_state):
        self.view.clear_email_list()
        emails = self.model.get_clicked_box_emails(select_state)
        self.state = select_state
        self.view.show_email_list(emails)

    # 获取收件箱
    def get_inbox(self):
        self.get_selected_box_emails(INBOX_STATE)

    # 获取草稿箱
    def get_drafts(self):
        self.get_selected_box_emails(DRAFT_STATE)

    # 获取邮件内容细节
    def get_email_details(self, email_text):
        details = self.model.get_email_details(email_text, self.state)
        self.view.display_email_details(details)

    # 删除邮件
    def delete_email(self, email_h):
        success = self.model.delete_email(email_h, self.state)
        if success:
            self.view.display_email_delete_success()
            self.get_selected_box_emails(self.state)
        else:
            self.view.display_email_delete_error()

    # 下载邮件
    def download_email(self, email_h, email_c):
        success = self.model.download_email(email_h, email_c, self.state)
        if success:
            self.view.display_attachment_download_success()
        else:
            self.view.display_attachment_download_error()

    # 发送邮件
    def send_email(self, to, subject, content):
        send_success = self.model.send_email(to, subject, content)
        if send_success:
            self.view.send_success()
        else:
            self.view.display_send_error()

    # 添加附件
    def attach_file(self, content):
        content = self.model.attach_file(content)
        if content is not None:
            self.view.update_send_content(content)
        else:
            self.view.display_attach_file_error()