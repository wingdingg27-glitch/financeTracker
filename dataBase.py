import sqlite3

class DataBaseManager:
    def __init__(self,path="base.db"):
        self.path=path
        self.initDb()

    def initDb(self):
        # createDb=sqlite3.connect(self.path)
        # try:
        with sqlite3.connect(self.path) as createDb:
            cursor=createDb.cursor()
            #таблица категорий
            cursor.execute("""CREATE TABLE IF NOT EXISTS category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK(type IN ('income','expence'))
            )""")
            #транзакции
            cursor.execute("""CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK (amount>0),
                categoryId INTEGER NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (categoryId) REFERENCES category(id) ON DELETE CASCADE
            )""")
            defaultCategories=[
                ("развлечения","expence"),
                ("еда","expence"),
                ("подарок","income"),
                ("зарплата","income"),
                ("одежда","expence")
            ]
            for name,type in defaultCategories:
                try:
                    cursor.execute("INSERT INTO category (name,type) VALUES (?,?)",(name,type))
                except:
                    pass

    def getCategories(self):
        with sqlite3.connect(self.path) as connect:
            connect.row_factory = sqlite3.Row
            cursor=connect.cursor()
            cursor.execute("SELECT * FROM category ORDER BY name")
            data=cursor.fetchall()
            # for d in data:
            #     print(d)
            data=[dict(d) for d in data]
            return data

    def addTransactions(self,amount,categoryId,date,description):
        if amount<=0:
            raise ValueError("количество не может быть ниже нуля!")

        with sqlite3.connect(self.path) as connect:
            cursor=connect.cursor()
            #cursor.execute("INSERT INTO transactions (amount,categoryId,date,description) VALUES(?,?,?,?)",(amount,categoryId,date,description))
            cursor.execute("INSERT INTO transactions (amount,categoryId,date,description) VALUES(?,?,?,?)",(amount, categoryId, date, description))

    def deleteTransactions(self,id):
        if id==None:
            return
        with sqlite3.connect(self.path) as connect:
            cursor=connect.cursor()
            cursor.execute("DELETE FROM transactions WHERE id=?",(id,))

    def getTransactions(self):
        with sqlite3.connect(self.path) as connect:
            connect.row_factory=sqlite3.Row
            cursor=connect.cursor()
            query="""SELECT
                t.id,
                t.amount,
                t.categoryId,
                t.date,
                t.description,
                c.name AS nameCategory,
                c.type AS typeCategory
                FROM transactions t
                JOIN category c ON t.categoryId=c.id
                ORDER BY t.id
            """
            cursor.execute(query)
            data=cursor.fetchall()
            data=[dict(d) for d in data]
            return data

    def search(self, searchText):
        with sqlite3.connect(self.path) as connect:
            connect.row_factory = sqlite3.Row
            cursor = connect.cursor()
            query = """SELECT
            t.id,
            t.amount,
            t.categoryId,
            t.date,
            t.description,
            c.name AS nameCategory,
            c.type AS typeCategory
            FROM transactions t
            JOIN category c ON t.categoryId=c.id
            WHERE t.description LIKE ?
            ORDER BY t.id"""
            cursor.execute(query,(searchText,))
            data=cursor.fetchall()
            print(data)
            data=[dict(d) for d in data]
            return data

    def updateBalance(self):
        with sqlite3.connect(self.path) as connect:
            cursor=connect.cursor()
            cursor.execute("""
            SELECT COALESCE(SUM(
            CASE WHEN c.type='income' THEN t.amount ELSE -t.amount END
            ),0) AS balance FROM transactions t JOIN category c ON t.categoryId=c.id
            """)
            data=cursor.fetchone()
            return data[0]

    def updateTransaction(self,**kwargs):
        with sqlite3.connect(self.path) as connect:
            cursor=connect.cursor()
            amount,categoryId,date,description,id=kwargs['amount'],kwargs['categoryId'],kwargs['date'],kwargs['description'],kwargs['id']
            query="""UPDATE transactions 
            SET amount=?,categoryId=?,date=?,description=? 
            WHERE id=?"""
            cursor.execute(query,(amount,categoryId,date,description,id))


