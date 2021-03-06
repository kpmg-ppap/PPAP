import sys
import webbrowser
from PyQt5.Qt import *
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QDesktopServices
from sample import find_similar
from sim_code import find_claim
from sim_code import find_term_show

# UI파일은 Python 코드 파일과 같은 디렉토리에 위치
form_class = uic.loadUiType("PPAP_UI.ui")[0]
global_claim = []

class MyWindow(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.search_hyperlink.linkActivated.connect(self.link)

        self.sum_btn.clicked.connect(self.summary)
        self.sum_input.setTextColor(QColor(0, 0, 0))
        self.sum_input.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sum_input.customContextMenuRequested.connect(self.on_context_menu)
        self.sum_input.installEventFilter(self)
        # self.popMenu.addSeparator()

        self.clm_btn.clicked.connect(self.claim)
        self.clm_btn.setVisible(False)
        self.clm_input.setTextColor(QColor(0, 0, 0))
        self.clm_input.installEventFilter(self)

        self.sum_output.installEventFilter(self)
        self.clm_output.installEventFilter(self)

        self.search_btn.clicked.connect(self.search)
        self.search_btn.setVisible(False)
        self.search_out_label.setVisible(False)
        self.search_output.setVisible(False)
        self.search_hyperlink.setVisible(False)
        self.reset_btn.clicked.connect(self.reset)

        self.title_btn.clicked.connect(self.title)
        self.title_btn.setVisible(False)
        self.title_text.setTextColor(QColor(100,100,100))
        self.title_text.insertPlainText("제목 없는 문서")
        self.title_list.setVisible(False)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:

            QApplication.clipboard().clear()

            if event.button() == QtCore.Qt.LeftButton:
                pass
            elif event.button() == QtCore.Qt.RightButton:
                #print(obj.objectName(), "Right click")
                # create context menu
                self.sum_input.copy()
                if len(QApplication.clipboard().text()) == 0 :
                    self.clm_input.copy()
                    if len(QApplication.clipboard().text()) == 0 :
                        self.sum_output.copy()
                        if len(QApplication.clipboard().text()) == 0 :
                            self.clm_output.copy()
                            if len(QApplication.clipboard().text()) == 0 :
                                self.popMenu = QtWidgets.QMenu(self)
                                self.popMenu.clear()
                                self.popMenu.addAction(QAction('(empty)', self))    

                            else:
                                self.popMenu = QtWidgets.QMenu(self)
                                self.popMenu.clear()
                                google_search = QAction('"' + QApplication.clipboard().text() + '" Google 검색', self)
                                patent_search = QAction('"' + QApplication.clipboard().text() + '" 특허 용례 검색', self)
                                self.popMenu.addAction(google_search)
                                self.popMenu.addAction(patent_search)
                                self.clm_output.customContextMenuRequested.connect(self.on_context_menu)
                                action = self.popMenu.exec_(self.clm_output.mapToGlobal(event.pos()))

                                if action == google_search:
                                    self.search(QApplication.clipboard().text())
                                    self.clm_output.moveCursor(QTextCursor.Right)
                                elif action == patent_search:
                                    #self.search_btn.setVisible(True)
                                    self.search_out_label.setVisible(True)
                                    self.search_output.setVisible(True)
                                    text = QApplication.clipboard().text()
                                    output = find_term_show(global_claim,target,text)
                                    self.show_output(self.search_output, text,('\n\n').join(output))
                                    self.clm_output.moveCursor(QTextCursor.Right)
                                    QApplication.clipboard().clear()
  
                        else:
                            self.popMenu = QtWidgets.QMenu(self)
                            self.popMenu.clear()
                            google_search = QAction('"' + QApplication.clipboard().text() + '" Google 검색', self)
                            patent_search = QAction('"' + QApplication.clipboard().text() + '" 특허 용례 검색', self)
                            self.popMenu.addAction(google_search)
                            self.popMenu.addAction(patent_search)
                            self.sum_output.customContextMenuRequested.connect(self.on_context_menu)
                            action = self.popMenu.exec_(self.sum_output.mapToGlobal(event.pos()))

                            if action == google_search:
                                self.search(QApplication.clipboard().text())
                                self.sum_output.moveCursor(QTextCursor.Right)
                            elif action == patent_search:
                                #self.search_btn.setVisible(True)
                                self.search_output.setVisible(True)
                                text = QApplication.clipboard().text()
                                output = find_term_show(global_claim,target,text)
                                self.show_output(self.search_output, text,('\n\n').join(output))
                                self.sum_output.moveCursor(QTextCursor.Right)
                                QApplication.clipboard().clear()

                    else:
                        self.popMenu = QtWidgets.QMenu(self)
                        self.popMenu.clear()
                        google_search = QAction('"' + QApplication.clipboard().text() + '" Google 검색', self)
                        patent_search = QAction('"' + QApplication.clipboard().text() + '" 특허 용례 검색', self)
                        self.popMenu.addAction(google_search)
                        self.popMenu.addAction(patent_search)
                        self.clm_input.customContextMenuRequested.connect(self.on_context_menu)
                        action = self.popMenu.exec_(self.clm_input.mapToGlobal(event.pos()))

                        if action == google_search:
                            self.search(QApplication.clipboard().text())
                        elif action == patent_search:
                            #self.search_btn.setVisible(True)
                            self.search_out_label.setVisible(True)
                            self.search_output.setVisible(True)
                            text = QApplication.clipboard().text()
                            output = find_term_show(global_claim,target,text)
                            self.show_output(self.search_output, text,('\n\n').join(output))
                            self.clm_input.moveCursor(QTextCursor.Right)
                            QApplication.clipboard().clear()
                        
                else:
                    self.popMenu = QtWidgets.QMenu(self)
                    self.popMenu.clear()
                    google_search = QAction('"' + QApplication.clipboard().text() + '" Google 검색', self)
                    patent_search = QAction('"' + QApplication.clipboard().text() + '" 특허 용례 검색', self)
                    self.popMenu.addAction(google_search)
                    self.popMenu.addAction(patent_search)
                    self.sum_input.customContextMenuRequested.connect(self.on_context_menu)
                    action = self.popMenu.exec_(self.sum_input.mapToGlobal(event.pos()))
                    
                    if action == google_search:
                        self.search(QApplication.clipboard().text())
                    elif action == patent_search:
                        #self.search_btn.setVisible(True)
                        self.search_out_label.setVisible(True)
                        self.search_output.setVisible(True)
                        text = QApplication.clipboard().text()
                        output = find_term_show(global_claim,target,text)
                        self.show_output(self.search_output, text,('\n\n').join(output))
                        self.sum_input.moveCursor(QTextCursor.Right)
                        QApplication.clipboard().clear()
                    
            elif event.button() == QtCore.Qt.MiddleButton:
                pass
        return QtCore.QObject.event(obj, event)

    def on_context_menu(self, point):
        # show context menu
        self.popMenu.exec_(self.sum_input.mapToGlobal(point))

    def show_output(self, where, what1, what2):
        where.clear()
        where.insertPlainText("[검색 텍스트]")
        where.append(what1)
        where.append("\n\n")
        where.insertPlainText("[검색 결과]")
        where.append(what2)
        where.append("")

    def on_context_menu(self, point):
        # show context menu
        self.popMenu.exec_(self.sum_input.mapToGlobal(point))

    def link(self, linkStr):
        QDesktopServices.openUrl(QUrl(linkStr))


    def summary(self):
        global global_claim
        global target
        QApplication.clipboard().clear()

        # 만약 선택영역이 있으면 복사 가능
        self.sum_input.copy()

        if len(QApplication.clipboard().text()) == 0 :
            # 만약 클립보드에 아무것도 없으면 input 박스에 있는 텍스트 전체를 인풋으로 받음
            text = self.sum_input.toPlainText()
            target = text
            _,_,abstract,_,claim,_ = find_similar(text)
            global_claim = claim
            self.show_output(self.sum_output, text, ('\n\n').join(abstract))
            self.clm_btn.setVisible(True)
            self.title_btn.setVisible(True)
            QApplication.clipboard().clear()

        else :
            # 선택영역을 인풋으로 받음
            #self.search_btn.setVisible(True)
            self.search_out_label.setVisible(True)
            self.search_output.setVisible(True)
            self.sum_input.setTextBackgroundColor(QColor(85, 170, 0))
            text = QApplication.clipboard().text()
            output = find_term_show(global_claim,target,text)
            self.show_output(self.search_output, text, ('\n\n').join(output))
            self.sum_input.moveCursor(QTextCursor.Right)
            self.sum_input.setTextBackgroundColor(QColor(255, 255, 255))
            QApplication.clipboard().clear()
    def claim(self):
        global global_claim
        global target
        QApplication.clipboard().clear()

        # 만약 선택영역이 있으면 복사 가능
        self.clm_input.copy()

        if len(QApplication.clipboard().text()) == 0:


            # 만약 클립보드에 아무것도 없으면 input 박스에 있는 텍스트 전체를 인풋으로 받음
            text = self.clm_input.toPlainText()
            target = text
            print('global_claim: ',global_claim)
            output = find_claim(global_claim,text)
            self.show_output(self.clm_output, '아래를 참고하세요!',('\n\n').join(output))
            self.clm_btn.setVisible(True)
            self.title_btn.setVisible(True)
            QApplication.clipboard().clear()

        else:
            # 선택영역을 인풋으로 받아라
            #self.search_btn.setVisible(True)
            self.search_out_label.setVisible(True)
            self.search_output.setVisible(True)
            self.clm_input.setTextBackgroundColor(QColor(255, 106, 101))
            text = QApplication.clipboard().text()
            output = find_term_show(global_claim,target,text)
            self.show_output(self.search_output, text,('\n\n').join(output))
            self.clm_input.moveCursor(QTextCursor.Right)
            self.clm_input.setTextBackgroundColor(QColor(255, 255, 255))
            QApplication.clipboard().clear()

    def search(self, keyword):
        # google search
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        urls = 'http://www.google.com/search?q=' + keyword
        webbrowser.get(chrome_path).open(urls)

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
        title_rcmd = ["후보1", "후보2", "후보3"]
        for title in title_rcmd:
            self.title_list.addItem(title)
        self.title_list.itemClicked.connect(self.chkItemClicked)

    def chkItemClicked(self):
        # self.title_text.setBackgroundColor(Qt::blue)
        self.title_text.clear()
        self.title_text.insertPlainText(self.title_list.currentItem().text())
        self.title_list.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MyWindow()
    editor.show()
    app.exec_()
