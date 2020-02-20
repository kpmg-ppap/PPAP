import sys
from PyQt5.Qt import *
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic

#UI파일은 Python 코드 파일과 같은 디렉토리에 위치
form_class = uic.loadUiType("PPAP_UI.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.exp_btn.clicked.connect(self.expression)
        self.ctx_btn.clicked.connect(self.context)
        self.search_btn.clicked.connect(self.search)
        self.reset_btn.clicked.connect(self.reset)

        self.title_btn.clicked.connect(self.title)
        self.title_text.setTextColor(QColor(100,100,100))
        self.title_text.setFontPointSize(20)
        self.title_text.insertPlainText("제목 없는 문서")
        self.listWidget.setVisible(False)

    def expression(self):
        QApplication.clipboard().clear()
        # self.input_text.setFontWeight(QFont.Bold)
        self.input_text.copy()
        if len(QApplication.clipboard().text()) == 0:
            QApplication.clipboard().clear()
        else:
            self.input_text.setTextBackgroundColor(QColor(85, 170, 0))
            text1 = QApplication.clipboard().text()
            self.exp_in.append(text1)
            self.input_text.moveCursor(QTextCursor.Right)
            self.input_text.setTextBackgroundColor(QColor(255, 255, 255))
            QApplication.clipboard().clear()

    def context(self):
        QApplication.clipboard().clear()
        # self.input_text.setFontWeight(QFont.Bold)
        self.input_text.copy()
        if len(QApplication.clipboard().text()) == 0:
            QApplication.clipboard().clear()
        else:
            self.input_text.setTextBackgroundColor(QColor(255, 106, 101))
            text1 = QApplication.clipboard().text()
            self.ctx_in.append(text1)
            self.input_text.moveCursor(QTextCursor.Right)
            self.input_text.setTextBackgroundColor(QColor(255, 255, 255))
            QApplication.clipboard().clear()

    def search(self):
        self.output_text.clear()
        exp1 = self.exp_in.toPlainText()
        ctx1 = self.ctx_in.toPlainText()
        self.output_text.insertPlainText("[표현검색 텍스트]")
        self.output_text.append(exp1)
        self.output_text.append("")
        self.output_text.append("")
        self.output_text.insertPlainText("[내용검색 텍스트]")
        self.output_text.append(ctx1)
        self.output_text.append("")

    def reset(self):
        original_text = self.input_text.toPlainText()
        self.input_text.clear()
        self.output_text.clear()
        self.exp_in.clear()
        self.ctx_in.clear()
        self.input_text.setTextBackgroundColor(QColor(255, 255, 255))
        self.input_text.setTextColor(QColor(0, 0, 0))
        self.input_text.setText(original_text)

    def title(self):
        self.listWidget.clear()
        self.listWidget.setVisible(True)
        self.listWidget.addItem("후보1")
        self.listWidget.addItem("후보2")
        self.listWidget.addItem("후보3")
        self.listWidget.itemClicked.connect(self.chkItemClicked)

    def chkItemClicked(self):
        # self.listWidget.setBackgroundColor(Qt::blue)
        self.title_text.clear()
        self.title_text.setFontPointSize(20)
        self.title_text.insertPlainText(self.listWidget.currentItem().text())
        self.listWidget.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MyWindow()
    editor.show()
    app.exec_()