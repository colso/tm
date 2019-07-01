#!/usr/bin/python
#-*-coding:utf-8

import pymysql
import sys
import time

def connect_to_db(host, port, user, passwd, db):
	conn = None
	try:
		conn = pymysql.connect(host=host, port=port, user=user, 
				passwd=passwd, db=db, autocommit=True, charset='utf8')
	except:
		print("Occur Exception from DB connect. "+
				"Please check connect infomation.({} {} {} {} {})".format(
					host, port, user, passwd, db))
	return conn

def close_db(conn):
	conn.close()

class torr_common_tbl:
	hash_magnet = ''
	title = ''
	add_time = 0
	status = 0
	category = ''
	sitename = ''

	def __init__(self, t_hash, t_title, t_add_time, t_status, t_category, t_sitename):
		self.hash_magnet = t_hash
		self.title = t_title
		self.add_time = t_add_time
		self.status = t_status
		self.category = t_category
		self.sitename = t_sitename
	
	def __str__(self):
		return "{} {} {} {} {} {}".format(
				self.hash_magnet, self.title, self.add_time, self.status, 
				self.category, self.sitename)

# CANDI_TBL
#+----------+--------------+------+-----+---------+-------+
#| Field    | Type         | Null | Key | Default | Extra |
#+----------+--------------+------+-----+---------+-------+
#| HASH     | varchar(64)  | NO   | PRI | NULL    |       |
#| TITLE    | varchar(128) | YES  |     | NULL    |       |
#| ADD_TIME | int(11)      | YES  |     | NULL    |       |
#| STATUS   | int(11)      | YES  |     | NULL    |       |
#| CATEGORY | varchar(16)  | YES  |     | NULL    |       |
#| SITENAME | varchar(64)  | YES  |     | NULL    |       |
#+----------+--------------+------+-----+---------+-------+

class candi_tbl_t(torr_common_tbl):
	def __str__(self):
		return "candi_tbl_t {} {} {} {} {} {}".format(
				self.hash_magnet, self.title, self.add_time, self.status, 
				self.category, self.sitename)

# RET_TBL
#+----------+--------------+------+-----+---------+-------+
#| Field    | Type         | Null | Key | Default | Extra |
#+----------+--------------+------+-----+---------+-------+
#| HASH     | varchar(64)  | NO   | PRI | NULL    |       |
#| TITLE    | varchar(128) | YES  |     | NULL    |       |
#| RET_TIME | int(11)      | YES  |     | NULL    |       |
#| CATEGORY | varchar(16)  | YES  |     | NULL    |       |
#| SITENAME | varchar(64)  | YES  |     | NULL    |       |
#+----------+--------------+------+-----+---------+-------+

class ret_tbl_t(torr_common_tbl):
	def __str__(self):
		return "ret_tbl_t {} {} {} {} {} {}".format(
				self.hash_magnet, self.title, self.add_time, self.category, self.sitename)

# RUN_TBL
#+----------+--------------+------+-----+---------+-------+
#| Field    | Type         | Null | Key | Default | Extra |
#+----------+--------------+------+-----+---------+-------+
#| HASH     | varchar(64)  | NO   | PRI | NULL    |       |
#| TITLE    | varchar(128) | YES  |     | NULL    |       |
#| ADD_TIME | int(11)      | YES  |     | NULL    |       |
#| STATUS   | int(11)      | YES  |     | NULL    |       |
#| CATEGORY | varchar(16)  | YES  |     | NULL    |       |
#| SITENAME | varchar(64)  | YES  |     | NULL    |       |
#+----------+--------------+------+-----+---------+-------+

class run_tbl_t(torr_common_tbl):
	def __str__(self):
		return "run_tbl_t {} {} {} {} {} {}".format(
				self.hash_magnet, self.title, self.add_time, self.category, self.sitename)



# ---------------------------- table management -------------------------------#

class torr_common_tbl:
	conn = None
	def _connect_to_db(self, host, port, user, passwd, db):
		try:
			if host and port and user and passwd and db:
				self.conn = pymysql.connect(
						host=host, port=port, user=user, passwd=passwd, 
						db=db, autocommit=True, charset='utf8')
		except:
			print("Occur Exception from DB connect.Please check connect infomation.({} {} {} {} {})".format(
						host, port, user, passwd, db))

	def __init__(self, host=None, port=None, user=None, passwd=None, db=None):
		if host and port and user and passwd and db:
			self._connect_to_db(host, port, user, passwd, db)

	def _common(self, sql):
		#LOG.debug("SQL :: {}".format(sql))
		if self.conn:
			cursor = self.conn.cursor(pymysql.cursors.DictCursor)
			return cursor, cursor.execute(sql)
		else:
			return None, -1

	def set_db_connection(self, conn):
		self.conn = conn

	def disconnect_db(self):
		if self.conn:
			self.conn.close()

	def create(self, sql):
		try:
			cursor, ret_num = self._common(sql)
		except:
			print("key error : {}".format(sql))
			return -1

		self.conn.commit()
		return ret_num
	
	def search(self, sql):
		cursor, ret_num = self._common(sql)
		if cursor:
			return ret_num, cursor.fetchall()
		else:
			return ret_num, None

	def update(self, sql):
		cursor, ret_num = self._common(sql)
		if cursor:
			self.conn.commit()
		return ret_num
	
	def delete(self, sql):
		cursor, ret_num = self._common(sql)
		return ret_num

	def __str__(self):
		return "{} {} {} {} {}".format(self.host, self.port, self.user, self.user,
					self.passwd, self.db)

class candi_tbl(torr_common_tbl):
	# conn: connection
	# ct_t: candi_tbl_t class
	def torr_candi_create(self, ct_t):	
		sqls = "insert into CANDI_TBL(HASH, TITLE, ADD_TIME, STATUS, CATEGORY, SITENAME) \
					values(\'{}\',\'{}\', {}, {}, \'{}\', \'{}\');".format(
					ct_t.hash_magnet, ct_t.title, ct_t.add_time, ct_t.status,
					ct_t.category, ct_t.sitename)
		
		return self.create(sqls)

	def torr_candi_search(self, hash_magnet):
		sqls = "select * from CANDI_TBL where HASH = \'{}\';".format(hash_magnet)
		return self.search(sqls)

	def torr_candi_update(self, ct_t):
		sqls = "update CANDI_TBL set TITLE=\'{}\', ADD_TIME={}, STATUS={}, CATEGORY=\'{}\', \
					SITENAME=\'{}\' where HASH=\'{}\';".format(
					ct_t.title, ct_t.add_time, ct_t.status,
					ct_t.category, ct_t.sitename, ct_t.hash_magnet)
		return self.update(sqls)

	def torr_candi_delete(self, hash_magnet):
		sqls = "delete from CANDI_TBL where HASH=\'{}\';".format(hash_magnet)
		return self.delete(sqls)

	def torr_candi_search_old_item(self):
		slqs = "select * from CANDI_TBL order by ADD_TIME limit 1"
		return self.search(slqs)

	def torr_candi_fill_result(self, r_dic):
		return candi_tbl_t(r_dic['HASH'], r_dic['TITLE'], r_dic['ADD_TIME'], r_dic['STATUS'], 
								r_dic['CATEGORY'], r_dic['SITENAME'])

	def __str__(self):
		return "CANDI_TBL " + self.__str__()

class run_tbl(torr_common_tbl):
	# conn: connection
	# run_t: run_tbl_t class
	def torr_run_create(self, run_t):	
		sqls = "insert into RUN_TBL(HASH, TITLE, ADD_TIME, STATUS, CATEGORY, SITENAME) \
					values(\'{}\',\'{}\', {}, {}, \'{}\', \'{}\');".format(
					run_t.hash_magnet, run_t.title, run_t.add_time, run_t.status,
					run_t.category, run_t.sitename)
		
		return self.create(sqls)

	def torr_run_search(self, hash_magnet):
		sqls = "select * from RUN_TBL where HASH = \'{}\';".format(hash_magnet)
		return self.search(sqls)

	def torr_run_search_old(self, timeout):
		sqls = "select * from RUN_TBL where ADD_TIME < {};".format(int(time.time() - timeout))
		return self.search(sqls)

	def torr_run_update(self, run_t):
		sqls = "update RUN_TBL set TITLE=\'{}\', ADD_TIME={}, STATUS={}, CATEGORY=\'{}\', \
					SITENAME=\'{}\' where HASH=\'{}\';".format(
					run_t.title, run_t.add_time, run_t.status,
					run_t.category, run_t.sitename, run_t.hash_magnet)
		return self.update(sqls)

	def torr_run_delete(self, hash_magnet):
		sqls = "delete from RUN_TBL where HASH=\'{}\';".format(hash_magnet)
		return self.delete(sqls)

	def torr_run_fill_result(self, r_dic):
		return run_tbl_t(r_dic['HASH'], r_dic['TITLE'], r_dic['ADD_TIME'], r_dic['STATUS'], 
								r_dic['CATEGORY'], r_dic['SITENAME'])

	def __str__(self):
		return "RUN_TBL " + self.__str__()

class ret_tbl(torr_common_tbl):
	# conn: connection
	# rt_t: ret_tbl_t class
	def torr_ret_create(self, rt_t):	
		sqls = "insert into RET_TBL(HASH, TITLE, RET_TIME, CATEGORY, SITENAME) \
					values(\'{}\', \'{}\', {}, \'{}\', \'{}\');".format(
					rt_t.hash_magnet, rt_t.title, rt_t.add_time, rt_t.category, rt_t.sitename)
		return self.create(sqls)

	def torr_ret_search(self, hash_magnet):
		sqls = "select * from RET_TBL where HASH = \'{}\';".format(hash_magnet)
		return self.search(sqls)

	def torr_ret_update(self, rt_t):
		sqls = "update RET_TBL set TITLE=\'{}\', RET_TIME={}, CATEGORY=\'{}\', \
					SITENAME=\'{}\' where HASH=\'{}\';".format(
					rt_t.title, rt_t.add_time, rt_t.category, 
					rt_t.sitename, rt_t.hash_magnet)
		return self.update(sqls)

	def torr_ret_delete(self, hash_magnet):
		sqls = "delete from RET_TBL where HASH=\'{}\';".format(hash_magnet)
		return self.delete(sqls)

	def __str__(self):
		return "RET_TBL " + self.__str__()
