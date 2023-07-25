# -*- coding: utf-8 -*-
# It's a PostgreSQL db functions
# Written by M1x7urk4
#
# █───█──█─██─██─████─█─█─████─█──█─█───
# ██─██─██──███──█──█─█─█─█──█─█─█──█──█
# █─█─█──█───█─────██─█─█─████─██───████
# █───█──█──███───██──█─█─█─█──█─█─────█
# █───█──█─██─██─██───███─█─█──█──█────█



# Import functions ------------------------------------------------------------

import psycopg2

# -----------------------------------------------------------------------------


# Main db class 

class DB:
    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host

        self.table_names = list()

    # --- other functions ---
    # Crate a table
    def create_table(self, table_name):
        conn = psycopg2.connect(dbname=self.dbname, user=self.user, 
                                password=self.password, host=self.host)
        cursor = conn.cursor()

        cursor.execute(f"""CREATE TABLE {table_name} (
                        data JSON NOT NULL
                    );""")
        cursor.close()

        conn.commit()
        conn.close()

    # Delete table
    def delete_table(self, table_name):
        conn = psycopg2.connect(dbname=self.dbname, user=self.user, 
                                password=self.password, host=self.host)
        cursor = conn.cursor()

        cursor.execute(f"""DROP TABLE {table_name};""")
        cursor.close()

        conn.commit()
        conn.close()
    

    # Clear table
    def clear_table(self, table_name):
        self.delete_table(table_name)
        self.create_table(table_name)


    # Get all data from db by table name
    def get_all(self, table_name, limit=None):
        conn = psycopg2.connect(dbname=self.dbname, user=self.user, 
                                password=self.password, host=self.host)
        cursor = conn.cursor()

        if limit is None:
            cursor.execute(f"SELECT * FROM {table_name}")
        else:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        
        data = cursor.fetchall()
        conn.close()

        return data
    

    # Save all data to db
    def save_all(self, table_name, save_data):
        conn = psycopg2.connect(dbname=self.dbname, user=self.user, 
                                password=self.password, host=self.host)
        cursor = conn.cursor()

        if len(self.get_all(table_name)) != 0:
            cursor.execute(f"UPDATE {table_name} SET data='{save_data}'")    
        else:
            cursor.execute(f"INSERT INTO {table_name} VALUES('{save_data}')")
        cursor.close()

        conn.commit()
        conn.close()


# ---- Test commands ------------------

# db = DB('sender_ch', 'ch_admin', '1234', '212.113.119.199')
# data = {
#     '1': 2,
#     'test': 'hello!'
# }

# db.delete_table('test')
# db.create_table('test')
# db.save_all('test', json.dumps(data))

# db.delete_table('test')
# db.create_table('test')

# data = db.get_all('test')[0][0]
# print(data)

# -------------------------------------


# db.create_table('all_data')
# db.delete_table('all_data')

# db = DB('sender_ch', 'ch_admin', '1234', '212.113.119.199')
# data = {
#     '1': 2,
#     'test': 'hello!'
# }
# data2 = {
#     'test2': 'LSAD',
#     '23': '42!'
# }

# db.delete_table('all_data')
# db.create_table('all_data_test')
# db.save_all('all_data', json.dumps(data))

# db.clear_table('all_data_test')
# print(db.get_all('all_data'))
