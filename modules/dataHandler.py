import sqlite3

# dataHandler: manages all communications with the SQLite3 database

class SavedData:
    def __init__(self):
        self.con = sqlite3.connect("modules/vault.db")
        self.cur = self.con.cursor()
        self.historyLenght = 5
        self.objects_per_page = 5

    def __extractTuple(self,_tuple):    # deprecated?
        return _tuple[0]
    
    def __getPureList(self,_list):      # deprecated?
        return list(map(self.__extractTuple,_list))

    def __keepHistoryLenght(self,history):
        if len(history) > self.historyLenght:
            SQL = f"DELETE FROM history WHERE expr='{history[0]}'"
            self.cur.execute(SQL)
            self.con.commit()

    def slicePages(self,_list):
        paginated_list = list()

        if len(_list) < self.objects_per_page:
            paginated_list.append(_list)
            return paginated_list

        while len(_list) > self.objects_per_page:
            paginated_list.append(_list[0:self.objects_per_page])
            del _list[0:self.objects_per_page]

        if _list:
            paginated_list.append(_list)

        return paginated_list
    
    def getHistory(self):
        res = self.cur.execute("SELECT * FROM history")
        return res.fetchall()
    
    def getVault(self):
        res = self.cur.execute("SELECT * FROM vault")
        pureList = res.fetchall()
        return self.slicePages(pureList)

    def updateHistory(self,entry,name):
        SQL = f"INSERT INTO history VALUES ('{entry}','{name}')"
        self.cur.execute(SQL)
        history = self.getHistory()
        self.__keepHistoryLenght(history)
        self.con.commit()

    def addToVault(self,entry,name):
        SQL = f"INSERT INTO vault VALUES ('{entry}','{name}')"
        self.cur.execute(SQL)
        self.con.commit()
    
    def addToVaultFromHistory(self,entry):
        SQL = f"INSERT INTO vault SELECT * FROM history WHERE expr='{entry}'"
        self.cur.execute(SQL)
        self.con.commit()

    def deleteVaultEntry(self, entry):
        SQL = f"DELETE FROM vault WHERE expr='{entry}'"
        self.cur.execute(SQL)
        self.con.commit()
    
    def updateColumn(self,table, entry, col, newVal):
        SQL = f"UPDATE {table} SET {col} = '{newVal}' WHERE expr='{entry}';"
        self.cur.execute(SQL)
        self.con.commit()

    def printTables(self):
        res = self.cur.execute("SELECT name FROM sqlite_master")
        print (self.__getPureList(res.fetchall()))

    def exit(self):
        self.con.close()