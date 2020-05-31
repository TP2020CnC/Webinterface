# Autor: Robin Schepp
##############import#################
import json
import sqlite3
import time
from builtins import print
from socket import create_connection


class DatenbankVerwalter:

    ##############Init#################

    ##############Properties#################

    ##############Methods#################
    # Datenbank verbinden
    def createConnection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Exception as e:
            print(e)

        return conn

    # Projekt erstellen
    def createMessdatenTable(self, conn):
        c = conn.cursor()
        c.execute("""CREATE TABLE messdaten (
    				id	INTEGER PRIMARY KEY AUTOINCREMENT,
    	            typ	TEXT,
    	            sensornummer INTEGER,
    	            millisekunden INTEGER,
    	            messwert REAL
    				)""")
        conn.commit()

    # Reihe einfügen
    def insertData(self, conn, task):
        """
        Create a new task
        :param conn:
        :param task:
        :return:
        """

        sql = ''' INSERT INTO messdaten(typ, sensornummer, millisekunden, messwert)
                  VALUES(?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, task)


    # erstelle unix Zeitstempel
    def current_milli_time(self):
        return int(round(time.time() * 1000))
    
    # erstellt eintrag
    def updateDatabase(self, db_file, jsonString):
        conn = self.createConnection(db_file)
        task = []
        i = 0
        task.append(jsonString["typ"])
        task.append(jsonString["sensornummer"])
        task.append(self.current_milli_time())
        #task.append(jsonString["millisekunden"])
        task.append(jsonString["messwert"])
        print(task)
        try:
            self.insertData(conn, task)
        except Exception as e:
            self.createMessdatenTable(conn)
            self.insertData(conn, task)
        conn.commit()
        conn.close()


####
    def GetDreck(self, dreckConn, lastTime):
        myTime = self.current_milli_time()
        c = dreckConn.cursor()
        hasResult = False
        try: 
            c.execute("SELECT * FROM messdaten WHERE millisekunden BETWEEN ? AND ?", (lastTime, myTime))
        except Exception as e:
            self.createMessdatenTable(dreckConn)
            c.execute("SELECT * FROM messdaten WHERE millisekunden BETWEEN ? AND ?", (lastTime, myTime))        
        div = 0
        result = 0
        values = c.fetchall()
        if len(values) > 0:
            mini = values[0][4]
            if mini is not None:
                for x in values:
                    if x[4] < mini:
                        mini = x[4]
                    #print(x[4])  # Debug # Debug # Debug
                hasResult = True
        c.execute("SELECT * FROM messdaten ORDER BY id DESC LIMIT 1")
        print(c.fetchone())
        dreckConn.close()
        if hasResult == True: return mini
#####################################################


    #schreibt Testdaten
    def insertTestData(self, db_file):
        conn = self.createConnection(db_file)
        task = []
        i = 0
        task.append("test")
        task.append("4")
        task.append(self.current_milli_time())
        #task.append(jsonString["millisekunden"])
        task.append(11000)
        print(task)
        try:
            self.insertData(conn, task)
        except Exception as e:
            self.createMessdatenTable(conn)
            self.insertData(conn, task)
        conn.commit()
        conn.close()

    # löscht alle einträge eines tables
    def delTable(self, db_file):
        conn = self.createConnection(db_file)
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM messdaten;")
        except Exception as e:
            conn.close()
        conn.commit()
        conn.close()
