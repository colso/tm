#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys					# system by core
import re					# regular expression by core
import tdb
import config
import time
import mt
import tmlogging as logger

LOG = logger.get_logger(__name__)

def move_to_run_table(db_conn, hash_key, title):
    if not db_conn:
        LOG.warning("Please Check DB Connection")
        return ''

    runp = tdb.run_tbl()
    runp.set_db_connection(db_conn)
    r_ret, r_result_set = runp.torr_run_search(hash_key)
    if not r_result_set:
        ctp = tdb.candi_tbl()
        ctp.set_db_connection(db_conn)
        c_ret, c_result_set = ctp.torr_candi_search(hash_key)
        if c_result_set:
            ctl = ctp.torr_candi_fill_result(c_result_set[0])
            runtl = tdb.run_tbl_t(ctl.hash_magnet, ctl.title, int(time.time()),
                                1, ctl.category, ctl.sitename)
        else:
            runtl = tdb.run_tbl_t(hash_key, title, int(time.time()),
                            1, 'Unknown', 'Unknown')

        runtp = tdb.run_tbl()
        runtp.set_db_connection(db_conn)
        runtp.torr_run_create(runtl)
    else:
        ctp = tdb.candi_tbl()
        ctp.set_db_connection(db_conn)
        ctp.torr_candi_delete(hash_key)

def move_to_complete_table(db_conn, hash_key, title):
    if not db_conn:
        LOG.warning("Please Check DB Connection")
        return ''

    comp = tdb.ret_tbl()
    comp.set_db_connection(db_conn)
    runtp = tdb.run_tbl()
    runtp.set_db_connection(db_conn)
    ctp = tdb.candi_tbl()
    ctp.set_db_connection(db_conn)

    com_ret, com_result_set = comp.torr_ret_search(hash_key)
    if not com_result_set:
        run_ret, run_result_set = runtp.torr_run_search(hash_key)
        if not run_result_set:
            c_ret, c_result_set = ctp.torr_candi_search(hash_key)
            if not c_result_set:
                comtl = tdb.ret_tbl_t(hash_key, title, int(time.time()),
                                100, 'Unknown', 'Unknown')
            else:
                ctl = ctp.torr_candi_fill_result(c_result_set[0])
                comtl = tdb.ret_tbl_t(ctl.hash_magnet, ctl.title, int(time.time()),
                                100, ctl.category, ctl.sitename)
        else:
            runtl = runtp.torr_run_fill_result(run_result_set[0])
            comtl = tdb.ret_tbl_t(runtl.hash_magnet, runtl.title, int(time.time()),
                                100, runtl.category, runtl.sitename)
        comp.torr_ret_create(comtl)

    # clear romplete item in candi and run table.
    ctp.torr_candi_delete(hash_key)
    runtp.torr_run_delete(hash_key)

def get_old_item_from_candi_tbl(db_conn):
    if not db_conn:
        LOG.warning("Please Check DB Connection")
        return {}

    ctp = tdb.candi_tbl()
    ctp.set_db_connection(db_conn)
    ret, result_set = ctp.torr_candi_search_old_item()
    if result_set:
        #print("GET OLD ONE FROM CANDI ({})".format(ctp.torr_candi_fill_result(result_set[0])))
        LOG.debug("GET OLD ONE FROM CANDI ")
        return result_set[0]
    return {}

def get_request_candidate(db_conn):
    candi_dic = get_old_item_from_candi_tbl(db_conn)
    if candi_dic:
        return candi_dic['HASH']
    return None

def check_old_running_item(db_conn, timeout):
    if not db_conn:
        LOG.warning("Please Check DB Connection")
        return {}

    runp = tdb.run_tbl()
    runp.set_db_connection(db_conn)
    r_ret, r_result_set = runp.torr_run_search_old(timeout)

    if r_result_set:
        old_list = []
        for i in range(len(r_result_set)):
            old_list.append(r_result_set[i]['HASH'])
    else:
        return None

    if old_list:
        for i in range(len(old_list)):
            mt.remove_torrent_and_data_from_magnet(old_list[i])
            runp.torr_run_delete(old_list[i])
            move_to_complete_table(old_list[i], "Expire Running")

    return None

def main():
	c_ini = config.TwalConfig('./config.ini', debug=False)
	db_conn = tdb.connect_to_db(
			c_ini.DB.db_address,
			c_ini.DB.db_port,
			c_ini.DB.db_user_id,
			c_ini.DB.db_user_pass,
			c_ini.DB.db_name)
    logger.setup(LOG, c_ini.LOG.logpath)
	if db_conn:
		LOG.debug("DB connected")
	else:
        LOG.error("DB NOTTTTTTT connected")

    db_conn.set_charset('utf8mb4')
	to_time = time.time() - c_ini.TIME.torrent_item_check_time
	while True:
		c_time = time.time()
		if to_time + c_ini.TIME.torrent_item_check_time < c_time:
			# get magnet from CANDI_TBL
			candi_magnet_one = get_request_candidate(db_conn)
			LOG.debug(candi_magnet_one)
			# try add to transmission
			r_dic = {}
			c_dic = {}
			running_cnt = 0
			r_dic, c_dic, running_cnt = mt.proc_run(candi_magnet_one, c_ini.TR.host,
				c_ini.TR.t_id,
                c_ini.TR.t_port,
                c_ini.TR.t_pass)
			for run_magnet in r_dic.keys():
				move_to_run_table(db_conn, run_magnet, r_dic[run_magnet]['title'])
			for com_magnet in c_dic.keys():
				move_to_complete_table(db_conn, com_magnet, c_dic[com_magnet]['title'])
			check_old_running_item(db_conn, c_ini.TIME.download_timeout)
			if running_cnt < 3:
				to_time = time.time() - c_ini.TIME.torrent_item_check_time + 2
			else:
				to_time = time.time()
		else:
			LOG.debug("Disk is ok. check next :: {}".format(c_time))
		time.sleep(2)


if __name__ in ("__main__"):
	main()
