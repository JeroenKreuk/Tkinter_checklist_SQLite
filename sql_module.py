import sqlite3
from sqlite3 import Error
import datetime
import pandas as pd

def return_table_name():
    """ Based on the date of today it returns the table name
    :return: Tablename
    """
    date_time = datetime.datetime.now().strftime("%Y%m%d")
    table_name = f"tbl{date_time}"
    return table_name

def create_connection(db_file):
    """ create a database connection to the SQLite database. If the database does not excist it will create one.
    :param db_file: database filename
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def check_table_exist():
    """
    Query all tables of the database and checks if the table already exist or not
    :param conn: the Connection object
    :return: the database name if it exist or a None value it
    """
    table_name = [return_table_name()]
    database = 'sqlite.db'
    conn = create_connection(database)
    cur = conn.cursor()
    sql = '''SELECT name
                FROM sqlite_master 
                WHERE name = ?
                AND type='table' '''
    cur.execute(sql, table_name)
    table = cur.fetchone()
    conn.close()
    return table

def create_database():
    """
    When there is no database table created for this day then a new sqlite table is created. The table gets the name of the date.
    :param date_time: the date of today, this will be the name of the sqlite table.
    """
    table_name = return_table_name()
    xlsx = ("userdata_ checklist.xlsx")
    df_main = pd.read_excel(xlsx, 'Main')
    database = 'sqlite.db'
    conn = create_connection(database)
    df_main.to_sql(table_name, conn, if_exists='replace', index = False)
    conn.close()


def create_and_retrieve_database():
    """
    Checks if database exist, if not create one and retrieve the database, if database is already created then only retrieve the databasee.
    """
    # Check if database exist, if not create one and retrieve the database, if database is already created then only retrieve the database
    if check_table_exist() is None:
        create_database()

def retrieve_sqlite_to_pandas():
    """
    Retrieve the complete sql table for that day and put it into a pandas dataframe object
    :return: pandas dataframe object
    """
    table_name = return_table_name()
    database = 'sqlite.db'
    conn = create_connection(database)
    cur = conn.cursor()
    sql = '''
            SELECT *
            FROM '''+table_name+'''
            '''
    cur.execute(sql)
    rows_sqlite = cur.fetchall()
    headers = list(map(lambda x: x[0], cur.description))
    conn.close()
    df_sqlite = pd.DataFrame(rows_sqlite, columns=headers)
    return df_sqlite



def update_row_database(column_name, column_name_value, column_name2, column_name2_value, row_number):
    """
    Update the sql database table
    :param column_name: the column in the database that needs to be updated, this is first_check_name or second_check_name
    :param column_name_value: this i the username
    :param column_name2: the second column in the database that needs to be updated, this is first_time or second_time
    :param column_name2_value: this is the time
    :param row_number: the row number of the colums of the database that needs to be updated
    """
    table_name = return_table_name()
    database = 'sqlite.db'
    conn = create_connection(database)
    question_marks = (column_name_value, column_name2_value, row_number)
    sql = ''' UPDATE '''+table_name+'''
                  SET '''+column_name+''' = ?,
                  '''+column_name2+''' = ?
                  WHERE rowid = ?
                  '''
    cur = conn.cursor()
    cur.execute(sql, question_marks)
    conn.commit()
    conn.close()

def last_update_table(first_time= "first_time", second_time = "second_time"):
    """
    Checks what the last time was the database was updated
    :return: time of the last database update
    """
    table_name = return_table_name()
    database = 'sqlite.db'
    conn = create_connection(database)
    sql = ''' SELECT MAX(''' + first_time + ''')                  
                FROM ''' + table_name + '''
                '''
    cur = conn.cursor()
    cur.execute(sql)
    rows = str(cur.fetchall()[0][0])
    rows = "00:01" if rows == "None" else rows
    sql2 = ''' SELECT MAX(''' + second_time + ''')                  
                FROM ''' + table_name + '''
                '''
    cur2 = conn.cursor()
    cur2.execute(sql2)
    rows2 = str(cur2.fetchall()[0][0])
    rows2 = "00:01" if rows2 == "None" else rows2
    latest_update = rows2 if rows2 > rows else rows
    return latest_update

