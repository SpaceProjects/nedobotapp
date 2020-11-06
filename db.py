import sqlite3

def connect(dbname, dbtable, args):
	'''input: dbconnect('dbname', 'dbtable', '(args)')\nUPD: warning! args may be str, concatenate it before assign'''
	global conn, cursor
	conn = sqlite3.connect(dbname)
	cursor = conn.cursor()
	string = """
cursor.execute("CREATE TABLE IF NOT EXISTS {1} {2}")""".format(dbname, dbtable, str(args))
	eval(string)
	return string

def insert(dbtable, args):
	string = """
cursor.execute("INSERT INTO {0} VALUES {1}")""".format(dbtable, str(args))
	eval(string); conn.commit(); return string

def update(dbtable, where_what, where_eq, set_what, set_var):
	string = """
cursor.execute("UPDATE {0} SET {1} = {2} WHERE {3} = {4}")""".format(dbtable, set_what, set_var, where_what, where_eq)
	eval(string); conn.commit(); return string

def select(dbtable, select, where_what, where_eq):
	string = """
cursor.execute("SELECT {0} FROM {1} WHERE {2} LIKE {3}")""".format(select, dbtable, where_what, where_eq)
	eval(string); return cursor.fetchone()[0]