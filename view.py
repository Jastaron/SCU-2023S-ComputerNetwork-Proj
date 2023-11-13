from qdarkstyle import load_stylesheet_pyqt5
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QListWidget, \
    QListWidgetItem, QTextBrowser, QPushButton, QMessageBox, QLineEdit, QDialog, QTextEdit, QApplication

class EmailView(QMainWindow):
    # 初始化view的信号
    login_signal = pyqtSignal(str, str)
    login_init_signal = pyqtSignal()
    show_inbox_signal = pyqtSignal()
    show_drafts_signal = pyqtSignal()
    show_sent_signal = pyqtSignal()
    show_email_details_signal = pyqtSignal(str)
    attach_file_signal = pyqtSignal(str)
    send_email_signal = pyqtSignal(str, str, str)
    download_email_signal = pyqtSignal(str, str)
    delete_email_signal = pyqtSignal(str)

    # 初始化函数，设计界面
    def __init__(self):
        super().__init__()

        self.setWindowTitle("J-Mail")
        self.setStyleSheet(load_stylesheet_pyqt5()
        + "QLabel, QPushButton, QLineEdit, QTextBrowser, QTextEdit { font-size: 20px; }")

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.login_widget = QWidget()
        self.setGeometry(100, 100, 400, 200)
        self.login_layout = QVBoxLayout()

        self.user_id_label = QLabel("邮箱:")
        self.user_id_input = QLineEdit()
        self.user_id_layout = QHBoxLayout()
        self.user_id_layout.addWidget(self.user_id_label)
        self.user_id_layout.addWidget(self.user_id_input)
        self.password_label = QLabel("授权码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit { font-size: 14px; }
        """)
        self.password_layout = QHBoxLayout()
        self.password_layout.addWidget(self.password_label)
        self.password_layout.addWidget(self.password_input)
        self.login_button = QPushButton("登录")
        self.login_button.clicked.connect(self.login_wait_task)

        self.login_layout.addLayout(self.user_id_layout)
        self.login_layout.addLayout(self.password_layout)
        self.login_layout.addWidget(self.login_button)
        self.login_widget.setLayout(self.login_layout)

        self.login_wait_dialog = QDialog(self)
        self.login_wait_dialog.setWindowTitle('登录中')
        self.login_wait_dialog_layout = QVBoxLayout(self.login_wait_dialog)
        self.login_wait_dialog_label = QLabel('正在登录\n请稍候...')
        self.login_wait_dialog_label.setAlignment(Qt.AlignCenter)
        self.login_wait_dialog_layout.addWidget(self.login_wait_dialog_label)
        self.login_wait_dialog.setLayout(self.login_wait_dialog_layout)
        self.login_wait_dialog.setFixedSize(250,120)
        self.login_wait_dialog.setWindowModality(Qt.NonModal)

        self.login_init_dialog = QDialog(self)
        self.login_init_dialog.setWindowTitle('初始化')
        self.login_init_dialog_layout = QVBoxLayout(self.login_init_dialog)
        self.login_init_dialog_label = QLabel('登陆成功!\n正在初始化您的邮箱')
        self.login_init_dialog_label.setAlignment(Qt.AlignCenter)
        self.login_init_dialog_layout.addWidget(self.login_init_dialog_label)
        self.login_init_dialog.setLayout(self.login_init_dialog_layout)
        self.login_init_dialog.setFixedSize(250,120)
        self.login_init_dialog.setWindowModality(Qt.NonModal)

        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()

        self.sidebar_widget = QWidget()
        self.sidebar_layout = QVBoxLayout()

        self.inbox_button = QPushButton("收件箱")
        self.inbox_button.clicked.connect(self.show_inbox_clicked)
        self.inbox_button.clicked.connect(self.set_download_disable)
        self.inbox_button.clicked.connect(self.set_delete_disable)
        self.drafts_button = QPushButton("草稿箱")
        self.drafts_button.clicked.connect(self.show_drafts_clicked)
        self.drafts_button.clicked.connect(self.set_download_disable)
        self.drafts_button.clicked.connect(self.set_delete_disable)
        self.sent_button = QPushButton("发送邮件")
        self.sent_button.clicked.connect(self.show_sent_clicked)

        self.sidebar_layout.addWidget(self.inbox_button)
        self.sidebar_layout.addWidget(self.drafts_button)
        self.sidebar_layout.addWidget(self.sent_button)
        self.sidebar_widget.setLayout(self.sidebar_layout)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()

        self.download_button = QPushButton("下载邮件(和附件)")
        self.download_button.clicked.connect(self.download_email_clicked)
        self.download_button.setEnabled(False)
        self.delete_button = QPushButton("删除邮件")
        self.delete_button.clicked.connect(self.delete_email_clicked)
        self.delete_button.setEnabled(False)

        self.email_list = QListWidget()
        self.email_list.setStyleSheet("""
            QListWidget::item {
                font-size: 20px;
                border-bottom: 1px solid gray;
                color: white;
            }
            QListWidget::item:selected {
                color: black;
                background-color: lightblue;
                border-left: 5px solid #777777;
            }
        """)  # 设置分割线样式和选中效果
        self.email_text = QTextBrowser()
        self.email_list.itemClicked.connect(self.show_email_details_clicked)
        self.email_list.itemClicked.connect(self.set_download_enable)
        self.email_list.itemClicked.connect(self.set_delete_enable)

        self.content_layout.addWidget(self.email_list)
        self.content_layout.addWidget(self.email_text)
        self.dd_layout = QHBoxLayout()
        self.dd_layout.addWidget(self.download_button)
        self.dd_layout.addWidget(self.delete_button)
        self.content_layout.addLayout(self.dd_layout)
        self.content_widget.setLayout(self.content_layout)

        self.send_widget = QWidget()
        self.send_layout = QVBoxLayout()

        self.recipient_label = QLabel("收件人邮箱:")
        self.recipient_input = QLineEdit()
        self.recipient_layout = QHBoxLayout()
        self.recipient_layout.addWidget(self.recipient_label)
        self.recipient_layout.addWidget(self.recipient_input)
        self.send_layout.addLayout(self.recipient_layout)

        self.subject_label = QLabel("主题:")
        self.subject_input = QLineEdit()
        self.subject_layout = QHBoxLayout()
        self.subject_layout.addWidget(self.subject_label)
        self.subject_layout.addWidget(self.subject_input)
        self.send_layout.addLayout(self.subject_layout)

        self.send_content_label = QLabel("正文:")
        self.send_content_input = QTextEdit()
        self.send_layout.addWidget(self.send_content_label)
        self.send_layout.addWidget(self.send_content_input)

        self.send_attachment_btn = QPushButton("添加附件")
        self.send_attachment_btn.clicked.connect(self.send_attachment_clicked)
        self.send_send_btn = QPushButton("发送")
        self.send_send_btn.clicked.connect(self.send_btn_clicked)
        self.send_send_layout = QHBoxLayout()
        self.send_send_layout.addWidget(self.send_attachment_btn)
        self.send_send_layout.addWidget(self.send_send_btn)
        self.send_layout.addLayout(self.send_send_layout)
        self.send_widget.setLayout(self.send_layout)

        self.main_layout.addWidget(self.sidebar_widget)
        self.main_layout.addWidget(self.content_widget)
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.login_widget)

    # 点击登录按钮
    def login_clicked(self):
        user_id = self.user_id_input.text()
        mandate = self.password_input.text()
        self.login_signal.emit(user_id, mandate)

    # 登录等待任务，一个线程负责通知Controller，另一个线程负责提示用户等待
    def login_wait_task(self):
        self.login_wait_dialog.show()
        self.lw_thread = QThread()
        self.lw_thread.started.connect(self.login_clicked)
        self.lw_thread.start()

    # 登录完成
    def login_done(self,b):
        self.lw_thread.quit()
        self.login_wait_dialog.close()
        if b:
            self.login_init_data()
        else:
            self.display_login_error()

    # 登录初始化内容
    def login_init_data(self):
        self.login_init_dialog.show()
        self.li_thread = QThread()
        self.li_thread.started.connect(self.login_init_signal.emit)
        self.li_thread.start()

    # 登录初始化完成
    def login_init_done(self):
        self.li_thread.quit()
        self.login_init_dialog.close()
        self.setCentralWidget(self.main_widget)
        self.setGeometry(100, 100, 1440, 960)

    # 点击收件箱模块
    def show_inbox_clicked(self):
        self.main_layout.removeWidget(self.send_widget)
        self.main_layout.addWidget(self.content_widget)
        self.main_widget.setLayout(self.main_layout)
        self.send_widget.hide()
        self.content_widget.show()
        self.show_inbox_signal.emit()

    # 点击草稿箱模块
    def show_drafts_clicked(self):
        self.main_layout.removeWidget(self.send_widget)
        self.main_layout.addWidget(self.content_widget)
        self.main_widget.setLayout(self.main_layout)
        self.send_widget.hide()
        self.content_widget.show()
        self.show_drafts_signal.emit()

    # 点击发送邮件模块
    def show_sent_clicked(self):
        self.main_layout.removeWidget(self.content_widget)
        self.main_layout.addWidget(self.send_widget)
        self.main_widget.setLayout(self.main_layout)
        self.content_widget.hide()
        self.send_widget.show()
        self.show_sent_signal.emit()

    # 清除邮件列表
    def clear_email_list(self):
        self.email_list.clear()
        self.email_text.clear()

    # 展示邮件列表
    def show_email_list(self, email_list):
        for e in email_list:
            item = QListWidgetItem(e)
            self.email_list.addItem(item)

    # 点击发送按钮
    def send_btn_clicked(self):
        msg_to = self.recipient_input.text()
        msg_subject = self.subject_input.text()
        msg_content = self.send_content_input.toPlainText()
        self.send_email_signal.emit(msg_to, msg_subject, msg_content)

    # 点击添加附件按钮
    def send_attachment_clicked(self):
        content = self.send_content_input.toPlainText()
        self.attach_file_signal.emit(content)

    # 更新发送编辑内容
    def update_send_content(self, content):
        self.send_content_input.clear()
        self.send_content_input.setText(content)

    # 发送成功提示
    def send_success(self):
        QMessageBox.information(self, "提示", "发送成功！")
        self.recipient_input.clear()
        self.subject_input.clear()
        self.send_content_input.clear()

    # 点击具体邮件展示
    def show_email_details_clicked(self, email):
        self.show_email_details_signal.emit(email.text())

    # 设置下载按键可用
    def set_download_enable(self):
        self.download_button.setEnabled(True)

    # 设置删除按键可用
    def set_delete_enable(self):
        self.delete_button.setEnabled(True)

    # 设置下载按键不可用
    def set_download_disable(self):
        self.download_button.setEnabled(False)

    # 设置删除按键不可用
    def set_delete_disable(self):
        self.delete_button.setEnabled(False)

    # 点击删除按键
    def delete_email_clicked(self):
        email_h = self.email_list.currentItem().text()
        self.delete_email_signal.emit(email_h)

    # 点击下载按键
    def download_email_clicked(self):
        email_h = self.email_list.currentItem().text()
        email_c = self.email_text.toPlainText()
        self.download_email_signal.emit(email_h, email_c)

    # 展示登录错误
    def display_login_error(self):
        QMessageBox.critical(self, "Error", "无效的邮箱或密码\n请重试...")

    # 展示邮件细节
    def display_email_details(self, details):
        self.email_text.clear()
        self.email_text.append(details)

    # 提示删除失败
    def display_email_delete_error(self):
        QMessageBox.critical(self, "Error", "删除邮件失败")

    # 提示删除成功
    def display_email_delete_success(self):
        QMessageBox.information(self, "Success", "邮件删除成功")

    # 提示下载失败
    def display_attachment_download_error(self):
        QMessageBox.critical(self, "Error", "下载邮件(附件)失败")

    # 提示下载成功
    def display_attachment_download_success(self):
        QMessageBox.information(self, "Success", "邮件(和附件)下载成功！")

    # 提示添加附件失败
    def display_attach_file_error(self):
        QMessageBox.critical(self, 'Error', '添加附件失败')

    # 提示发送失败
    def display_send_error(self):
        QMessageBox.critical(self, 'Error', '发送失败')
