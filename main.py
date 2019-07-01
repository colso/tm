#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys					# system by core
import re					# regular expression by core
import tdb 
import config
import time
import mt

def main():
	c_ini = config.TwalConfig('./config.ini', debug=False)
	db_conn = tdb.connect_to_db(
			c_ini.DB.db_address, 
			c_ini.DB.db_port, 
			c_ini.DB.db_user_id, 
			c_ini.DB.db_user_pass, 
			c_ini.DB.db_name)
	if db_conn:
		print("DB connected")
	else:
		print("DB NOTTTTTTT connected")
	
	mt.proc_run('', 
			c_ini.TR.host,
			c_ini.TR.t_id,
			c_ini.TR.t_port,
			t_pass)


if __name__ in ("__main__"):
	main()
