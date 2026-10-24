from PyQt6.QtWidgets import QDialog,QPushButton,QHBoxLayout,QVBoxLayout,QFormLayout,QLineEdit,QDateEdit,QComboBox
from PyQt6.QtCore import QDate

class Dialog(QDialog):
    def __init__(self,db,transaction,parent):
        super().__init__(parent)
        self.db=db
        self.transaction=transaction
        self.setWindowTitle("Редактирование транзакций")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.editUi()
        self.editData=None

    def editUi(self):
        verticalLayout=QVBoxLayout(self)
        formLayout=QFormLayout()
        verticalLayout.addLayout(formLayout)
        self.amountEdit=QLineEdit()
        self.categoryEdit=QComboBox()
        self.dateEdit=QDateEdit()
        self.descriptionEdit=QLineEdit()

        formLayout.addRow("Сумма: ",self.amountEdit)
        formLayout.addRow("Категория: ",self.categoryEdit)
        formLayout.addRow("Дата: ",self.dateEdit)
        formLayout.addRow("Комментарий: ",self.descriptionEdit)
        self.loadData()

        #создаем кнопки
        buttonLayout=QHBoxLayout()
        verticalLayout.addLayout(buttonLayout)
        confirmButton=QPushButton("Подтвердить")
        confirmButton.clicked.connect(self.accept)
        cancelButton=QPushButton("Отмена")
        cancelButton.clicked.connect(self.cancel)
        buttonLayout.addWidget(confirmButton)
        buttonLayout.addWidget(cancelButton)

    def loadData(self):
        self.amountEdit.setText(str(self.transaction["amount"]))
        self.descriptionEdit.setText(str(self.transaction["description"]))
        y,m,d=map(int,self.transaction["date"].split("-"))
        self.dateEdit.setDate(QDate(y,m,d))
        categories=self.db.getCategories()
        for i in categories:
            self.categoryEdit.addItem(i["name"],i["id"])

        indexCategory=self.transaction["categoryId"] #из базы данных
        #self.categoryEdit.setCurrentIndex(indexCategory)
        indexComboBox=self.categoryEdit.findData(indexCategory) #индекс в выпадающем списке
        self.categoryEdit.setCurrentIndex(indexComboBox)
        self.transactionId=self.transaction["id"]

    def accept(self):
        self.editData={
            "id":self.transactionId,
            "amount":self.amountEdit.text(),
            "categoryId":self.categoryEdit.currentData(),
            "date":self.dateEdit.date().toString("yyyy-MM-dd"),
            "description":self.descriptionEdit.text()
        }

        super().accept()


    def cancel(self):
        self.reject()