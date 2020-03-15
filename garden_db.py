import sqlite3 as sql
from sqlite3 import Error
 

db_location = r'./my_gardens.db'

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sql.connect(db_file)
        return conn
    except Error as e:
        print(e)

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
    
def add_kindergarden(conn, val):

    sql = ''' INSERT INTO kindergardens(name,pay_method,city) VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, val)
    return cur.lastrowid

def add_recept(conn, task):
    """
    Create a new recepet
    :param conn:
    :param recepet:
    :return:
    """
    sql = ''' INSERT INTO recepts(name,kindergarden,month,year,status,img_num) VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    return cur.lastrowid    

        
def init_db(db_path):
    conn= create_connection(db_path)
    sql_create_kindergarden_table = """ CREATE TABLE IF NOT EXISTS kindergardens (
                                        name text PRIMARY KEY,
                                        pay_method text,
                                        city text
                                    ); """

    sql_create_recept_table = """CREATE TABLE IF NOT EXISTS recepts (
                                    id integer PRIMARY KEY,
                                    kindergarden text NOT NULL,
                                    month integer NOT NULL,
                                    year integer NOT NULL,
                                    status integer ,
                                    payment_day DATETIME ,
                                    img_url text ,
                                    amount int ,
                                    FOREIGN KEY (kindergarden) REFERENCES kindergardens (name)
                                );"""
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_kindergarden_table)
        # create tasks table
        create_table(conn, sql_create_recept_table)
    else:
        print("Error! cannot create the database connection.")
    
        
    return conn

## 
