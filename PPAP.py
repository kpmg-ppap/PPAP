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

        self.sum_btn.clicked.connect(self.summary)
        self.sum_input.setTextColor(QColor(0, 0, 0))

        self.clm_btn.clicked.connect(self.claim)
        self.clm_btn.setVisible(False)
        self.clm_input.setTextColor(QColor(0, 0, 0))

        self.search_btn.clicked.connect(self.search)
        self.search_btn.setVisible(False)
        self.search_output.setVisible(False)
        self.reset_btn.clicked.connect(self.reset)

        self.title_btn.clicked.connect(self.title)
        self.title_btn.setVisible(False)
        self.title_text.setTextColor(QColor(100,100,100))
        self.title_text.setFontPointSize(20)
        self.title_text.insertPlainText("제목 없는 문서")
        self.title_list.setVisible(False)
        MyWindow.initial_clipboard_len = len(QApplication.clipboard().text())

    def summary(self):
        # if MyWindow.initial_clipboard_len != 0 :
            # 일단 만약 기존 클립보드에 뭐가 있으면 지워
        QApplication.clipboard().clear()
        # else :
        #     # 없으면 패스
        #     pass

        # 만약 선택영역이 있으면 복사가 될거야
        self.sum_input.copy()

        if len(QApplication.clipboard().text()) == 0 :
            # 만약 클립보드에 아무것도 없으면 input 박스에 있는 텍스트 전체를 인풋으로 받아라
            text = self.sum_input.toPlainText()
            self.sum_output.append(text)
            self.clm_btn.setVisible(True)
            self.title_btn.setVisible(True)
            QApplication.clipboard().clear()

        else :
            # 선택영역을 인풋으로 받아라
            self.search_btn.setVisible(True)
            self.search_output.setVisible(True)
            self.sum_input.setTextBackgroundColor(QColor(85, 170, 0))
            text = QApplication.clipboard().text()
            self.search_output.append(text)
            self.sum_input.moveCursor(QTextCursor.Right)
            self.sum_input.setTextBackgroundColor(QColor(255, 255, 255))
            QApplication.clipboard().clear()

    def claim(self):
        QApplication.clipboard().clear()

        # 만약 선택영역이 있으면 복사가 될거야
        self.clm_input.copy()

        if len(QApplication.clipboard().text()) == 0:
            # 만약 클립보드에 아무것도 없으면 input 박스에 있는 텍스트 전체를 인풋으로 받아라
            text = self.clm_input.toPlainText()
            self.clm_output.append(text)
            self.clm_btn.setVisible(True)
            self.title_btn.setVisible(True)
            QApplication.clipboard().clear()

        else:
            # 선택영역을 인풋으로 받아라
            self.search_btn.setVisible(True)
            self.search_output.setVisible(True)
            self.clm_input.setTextBackgroundColor(QColor(255, 106, 101))
            text = QApplication.clipboard().text()
            self.search_output.append(text)
            self.clm_input.moveCursor(QTextCursor.Right)
            self.clm_input.setTextBackgroundColor(QColor(255, 255, 255))
            QApplication.clipboard().clear()


    def search(self):
        pass
        # google search

        # self.output_text.clear()
        # exp1 = self.exp_in.toPlainText()
        # ctx1 = self.ctx_in.toPlainText()
        # self.output_text.insertPlainText("[표현검색 텍스트]")
        # self.output_text.append(exp1)
        # self.output_text.append("")
        # self.output_text.append("")
        # self.output_text.insertPlainText("[내용검색 텍스트]")
        # self.output_text.append(ctx1)
        # self.output_text.append("")

    def reset(self):
        clm_original = self.clm_input.toPlainText()
        self.clm_output.clear()
        self.clm_input.setTextBackgroundColor(QColor(255, 255, 255))
        self.clm_input.setTextColor(QColor(0, 0, 0))
        self.clm_input.setText(clm_original)

        sum_original = self.sum_input.toPlainText()
        self.sum_output.clear()
        self.sum_input.setTextBackgroundColor(QColor(255, 255, 255))
        self.sum_input.setTextColor(QColor(0, 0, 0))
        self.sum_input.setText(sum_original)

        self.search_output.clear()

    def title(self):
        self.title_list.clear()
        self.title_list.setVisible(True)
        self.title_list.addItem("후보1")
        self.title_list.addItem("후보2")
        self.title_list.addItem("후보3")
        self.title_list.itemClicked.connect(self.chkItemClicked)

    def chkItemClicked(self):
        # self.title_text.setBackgroundColor(Qt::blue)
        self.title_text.clear()
        self.title_text.setFontPointSize(20)
        self.title_text.insertPlainText(self.title_list.currentItem().text())
        self.title_list.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MyWindow()
    editor.show()
    app.exec_()