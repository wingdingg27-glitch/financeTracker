import sys

from dataBase import DataBaseManager
from ui import Ui_MainWindow
from editDialog import Dialog
from PyQt6.QtWidgets import QApplication,QMainWindow,QMessageBox,QHeaderView,QTableWidgetItem,QTableWidget,QDialog,QMenu
from PyQt6.QtCore import QEvent,Qt
from PyQt6.QtGui import QAction,QBrush,QColor

class Tracker(QMainWindow,Ui_MainWindow):
    def __init__(self,db):
        super().__init__()
        self.setupUi(self)
        self.db=db
        self.newSelectionRow=None
        self.selectionRow=None
        self.extension()
        self.loadCategories()
        self.confirmButton.clicked.connect(self.addTransactions)
        self.deleteButton.clicked.connect(self.deleteTransactions)
        self.redactButton.clicked.connect(self.editTransactions)
        self.tableWidget.itemSelectionChanged.connect(self.selectionChanged)
        self.updateTable()
        self.selectionChanged()
        self.tableWidget.viewport().installEventFilter(self)
        self.tableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.contextMenu)
        self.searchEdit.setPlaceholderText("поиск по комментариям")
        self.searchEdit.textChanged.connect(self.updateTable)

    def extension(self):
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.clearSelection()

    def loadCategories(self):
        data=self.db.getCategories()
        self.categoryCombo.clear()
        for i in data:
            self.categoryCombo.addItem(i["name"],i["id"])

    def addTransactions(self):
        try:
            amount=float(self.sumLineEdit.text().replace(",","."))
        except:
            raise ValueError("Введите корректную сумму!")
        categoryId=self.categoryCombo.currentData()
        date=self.dateEdit.date().toString("yyyy-MM-dd")
        com=self.comLineEdit.text()
        self.db.addTransactions(amount,categoryId,date,com)
        self.updateTable()

    def deleteTransactions(self):
        try:
            self.db.deleteTransactions(self.transactionId[self.selectionRow])
            self.updateTable()
            #print(self.tableWidget.currentRow())
        except:
            pass
        self.clearSelection()

    def editTransactions(self):
        transaction=self.transactions[self.tableWidget.currentRow()]
        dialog=Dialog(self.db,transaction,self)
        if dialog.exec()==QDialog.DialogCode.Accepted:  #пользователь сохранил данные
            data=dialog.editData
            self.db.updateTransaction(**data)
            self.updateTable()
        self.clearSelection()

    def updateTable(self):

        searchText=self.searchEdit.text().strip()
        if searchText!="":
            self.transactions=self.db.search(searchText)
        else:
            self.transactions=self.db.getTransactions()
        self.tableWidget.setRowCount(len(self.transactions))
        self.transactionId = []
        for a, i in enumerate(self.transactions):
            amount = QTableWidgetItem(str(i["amount"]))
            if i["typeCategory"]=="income":
                amount.setForeground(QBrush(QColor("lime")))
            else:
                amount.setForeground(QBrush(QColor("red")))
            self.transactionId.append(i["id"])
            self.tableWidget.setItem(a,0,amount)
            self.tableWidget.setItem(a,1,QTableWidgetItem(str(i["nameCategory"])))
            date=str(i["date"])
            y,m,d=date.split("-")
            date=f"{d}.{m}.{y}"
            self.tableWidget.setItem(a,2,QTableWidgetItem(date))
            self.tableWidget.setItem(a,3,QTableWidgetItem(str(i["description"])))
        balance = self.db.updateBalance()
        self.amountLabel.setText("Баланс: " + str(balance))

    def selectionChanged(self):
        if len(self.tableWidget.selectedItems())==0:
            self.selectionRow=None
            self.deleteButton.hide()
            self.redactButton.hide()
            self.confirmButton.show()
            return
        self.deleteButton.show()
        self.redactButton.show()
        self.confirmButton.hide()
        self.selectionRow=self.tableWidget.currentRow()

    def eventFilter(self,obj,event):
        if obj==self.tableWidget.viewport():
            if event.type()==QEvent.Type.MouseButtonPress:
                index=self.tableWidget.indexAt(event.pos())
                if not index.isValid():
                    self.clearSelection()
                else:
                    #self.selectionRow=self.tableWidget.currentRow()
                    row=index.row()
                    element=self.tableWidget.item(row,3)
                    if element.isSelected():
                        self.clearSelection()
                    #print(self.selectionRow)
                    #print(self.newSelectionRow)
                    #if self.selectionRow!=self.newSelectionRow:
                    #     self.newSelectionRow=self.selectionRow
                    # else:
                    #     self.clearSelection()
                        return True
        return super().eventFilter(obj,event)

    def keyPressEvent(self,event):
        if event.key()==Qt.Key.Key_Escape:
            self.clearSelection()
        return super().keyPressEvent(event)
    def clearSelection(self):
        self.tableWidget.clearSelection()
        self.deleteButton.hide()
        self.redactButton.hide()
        self.confirmButton.show()
        self.tableWidget.setCurrentCell(-1,-1)

    def contextMenu(self,pos):
        index=self.tableWidget.indexAt(pos)
        row=index.row()
        item=self.tableWidget.item(row,0)
        if item!=None:
            menu=QMenu(self)
            editAction=QAction("Редактировать",self)
            editAction.triggered.connect(self.editTransactions)
            deleteAction=QAction("Удалить",self)
            deleteAction.triggered.connect(self.deleteTransactions)
            menu.addAction(editAction)
            menu.addAction(deleteAction)
            menu.addSeparator()
            clearAction=QAction("Отмена",self)
            clearAction.triggered.connect(self.clearSelection)
            menu.addAction(clearAction)
            menu.exec(self.tableWidget.viewport().mapToGlobal(pos))

if __name__=="__main__":
    manager=DataBaseManager()
    QApp = QApplication(sys.argv)
    tracker=Tracker(manager)
    tracker.show()
    sys.exit(QApp.exec())