#!/usr/bin/python

import transmissionrpc
from datetime import datetime
import time
import os

def connect_to_server(host, t_id, t_pass, t_port):
    try:
        tc = transmissionrpc.Client(host, port=t_port, user=t_id, password=t_pass)
    except:
        return None
    return tc

def release_for_connect(tc):
    del(tc)

def add_magnet_to_server(tc, magnet):
    try:
        tc.add(None, filename=magnet)
    except:
        return False
    return True

def remove_torrent_at_server(tc, t_id, remove_data=False):
    try:
        tc.remove_torrent(t_id, delete_data=remove_data)
    except:
        return False
    return True

def get_torrent_info(tc):
    res = tc.get_torrents()

    il = []
    for item in res:
        id_num = item.__getattr__('id')
        status = item.status
        name   = item._get_name_string().decode()
        hash_s = item.hashString.upper()
        d_time = (datetime.now() - item.date_started).seconds
        ratio  = item.ratio
        il.append({'id':id_num, 'status':status, 'name':name, 'hash_string':hash_s, 'delta_time':d_time, 'ratio':ratio})

    return il

def clear_complete_torrent(tr_id, tr_pass, tr_port):
    conn = connect_to_server(tr_id, tr_pass, tr_port)

    del_cnt = 0
    del_magnet = []
    if not conn:
        return del_cnt, del_magnet, "do not connect transmission server check your account information({} {} {})".format(tr_id, tr_pass, tr_port)

    item_list = get_torrent_info(conn)
    if not item_list:
        return del_cnt, del_magnet, "empty torrent list"

    try:
        for item in item_list:
            if item['status'] == 'seeding':
                remove_torrent_at_server(conn, item['id'])
                del_cnt += 1
                del_magnet.append(item['hash_string'])
    except:
        return del_cnt, del_magnet, "occur exception"

    return del_cnt, del_magnet, "delete complete"

def remove_torrent_and_data_from_magnet(magnet):
    u_id = "torr"
    u_pass = "sjrnfl"
    port = 9091
    tc = None

    tc = connect_to_server(u_id, u_pass, port)
    try:
        li = get_torrent_info(tc)
    except:
        print("get_torrent_info exception in remove torrent")
        print("Try to restart transmission service from remove torrent")
        return None

    if not li:
        print("Remove torrent from magnet :: List is empty")
        if tc:
            release_for_connect(tc)
        return None

    for item in li:
        full_hash_magnet = "magnet:?xt=urn:btih:"+item['hash_string'].upper()
        if magnet == full_hash_magnet:
            print("Serach done by list {} : {}".format(magnet, item['name']))
            remove_torrent_at_server(tc, item['id'], remove_data=True)

    if tc:
        release_for_connect(tc)

    return None

def proc_run(magnet, host=None, t_id=None, t_port=None, t_pass=None):
    u_id = t_id
    u_pass = t_pass
    port = t_port
    exist_magnet = ""
    running_dic = {}
    completed_dic = {}
    full_hash_magnet = ""
    max_cnt = 3
    stall_time = 3 * 60			# 3 min
    delete_flag = 0
    item_list = []

    conn = connect_to_server(host, u_id, u_pass, port)
    if not conn:
        print("Do not connect Transmission Server")
        return ''
    else:
        print("Connected Transmission server")
    try:
        item_list = get_torrent_info(conn)
    except:
        print("get_torrent_info exception")
        print("Try to stop transmission service")
        return {}, {}, max_cnt

    print(datetime.today())
    print(item_list)
    del_cnt = 0
    try:
        for item in item_list:
            print("info {} {} {} {}".format(item['id'], item['status'], item['name'], item['hash_string']))
            #full_hash_magnet = "magnet:?xt=urn:btih:"+item['hash_string'].upper()
            full_hash_magnet = item['hash_string'].upper()
            title = item['name']
            status = item['status']
            delta_time = item['delta_time']
            ratio = item['ratio']

            if status == 'seeding' or title.find('360p') >= 0:
                print("Download Done {} Remove item {}".format(item['name'], datetime.today()))
                completed_dic[full_hash_magnet]={'title':item['name'],'status':status}
                remove_torrent_at_server(conn, item['id'])
                del_cnt += 1
            elif ratio == -1.0 and delta_time > stall_time:
                print("Stall item in list. Remove item({}) ".format(full_hash_magnet))
                completed_dic[full_hash_magnet]={'title':item['name'],'status':"stall"}
                remove_torrent_at_server(conn, item['id'])
                delete_flag = 1
            else:
                running_dic[full_hash_magnet]={'title':item['name'],'status':status}
                continue;
    except Exception as e:
        print(e)
        return running_dic, completed_dic, max_cnt
#	time.sleep(10)

    add_cnt = 0

    if (delete_flag == 0) and magnet and \
             ((len(item_list) - del_cnt) < max_cnt) and \
             (not magnet in running_dic):
        magnet = "magnet:?xt=urn:btih:"+magnet
        print("[ {} ] Add magnet to server ({})".format(datetime.today(), magnet))
        add_magnet_to_server(conn, magnet)
        add_cnt += 1
    else:
        print("running magent : {}".format(magnet))

    release_for_connect(conn)
    return running_dic, completed_dic, (len(item_list) - del_cnt + add_cnt)

