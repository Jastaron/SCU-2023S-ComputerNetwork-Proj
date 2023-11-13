from controller import *

if __name__ == "__main__":
    app = QApplication([])
    controller = EmailController()
    controller.show()
    app.exec_()