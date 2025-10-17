# -*- encoding: utf-8 -*-
"""
@File    : bit_torrent_utils.py
@Time    : 2022/5/8 19:01
@Author  : smy
@Email   : smyyan@foxmail.com
@Software: PyCharm
"""

from config import ReadConfig
import time
import requests
from lxml import html
import os
import shutil
import sys
import hashlib
import bencodepy
import inspect

def log_msg(msg):
    # 获取调用栈中上一级（即调用 log_msg 的函数）的帧
    frame = inspect.stack()[1]
    
    # 获取函数名
    func_name = frame.function
    
    # 获取文件绝对路径
    abs_path = frame.filename
    
    # 将绝对路径转换为相对路径（相对当前工作目录）
    rel_path = os.path.relpath(abs_path, start=os.getcwd())
    
    # 输出日志
    print(f"[{rel_path}::{func_name}] {msg}")

def get_infohash_from_torrent(torrent_content):
    torrent_data = bencodepy.decode(torrent_content)
    # 取出 info 部分
    info = torrent_data[b'info']
    # bencode 再编码一次
    encoded_info = bencodepy.encode(info)
    # SHA1 计算
    infohash = hashlib.sha1(encoded_info).hexdigest().upper()
    return infohash

class TorrentInfo:
    def __init__(self, torrent_info):
        # 根据utorrent的返回结果来定义
        self.id = torrent_info[0]  # id=hash，这套代码的逻辑是按照hash开始
        self.name = torrent_info[2]  # name
        self.total_size = torrent_info[3]  # size
        # self.status = torrent_info[21]  # status text
        self.date_added = torrent_info[23]  # added date
        self.download_dir = torrent_info[26]  # download path
        self.downloaded_size = torrent_info[5]  # downloaded
        self.uploaded_size = torrent_info[6]  # uploaded
        self.rateUpload = torrent_info[8]  # upload speed
        self.rateDownload = torrent_info[9]  # download speed
        self.status = TorrentStatus(torrent_info[21])  # status text

class TorrentStatus:
    def __init__(self, status_string):
        # 解析状态字符串，适用于utorrent
        self.checking = '检查' in status_string
        self.downloading = '下载' in status_string
        self.seeding = '做种' in status_string
        self.paused = '暂停' in status_string
        self.stopped = '停止' in status_string

class UTorrent:
    def __init__(self, config):
        self.host = config.get_utorrent_config('utorrent-host')
        self.port = config.get_utorrent_config('utorrent-port')
        self.username = config.get_utorrent_config('utorrent-username')
        self.password = config.get_utorrent_config('utorrent-password')
        self.download_path = config.get_utorrent_config('utorrent-download-path')
        self.base_url = f"http://{self.host}:{self.port}/gui"
        self.auth     = requests.auth.HTTPBasicAuth(self.username, self.password)
        self.token, self.cookies  = self._get_token()

    def _get_token(self):
        url = self.base_url + '/token.html'

        token    = -1
        cookies  = -1

        try:
            response = requests.get(url, auth=self.auth)

            token = -1

            if response.status_code == 200:
                xtree = html.fromstring(response.content)
                token = xtree.xpath('//*[@id="token"]/text()')[0]
                guid  = response.cookies['GUID']
            else:
                token = -1

            cookies = dict(GUID = guid)

        except requests.ConnectionError as error:
            token = 0
            cookies = 0
            log_msg(error)
        except:
            log_msg('error')

        return token, cookies

    def is_online(self):
        if self.token != -1 and self.token != 0:
            return True
        else:
            return False

# public sectin -->
    def get_list(self):
        torrent_ls = []
        time.sleep(1)  # wait 1s for token get
        try:
            status, response = self._action('list=1')
            if status == 200:
                torrents_json = response.json()
            else:
                raise ValueError('cannot get list')
                # 解析成TorrentInfo对象列表
            for torrent_info in torrents_json['torrents']:
                torrent = TorrentInfo(torrent_info)
                torrent_ls.append(torrent)
            return torrent_ls

        except Exception as e:
            log_msg(f'[ERROR] ' + repr(e))
            return None

    def remove(self, ids, delete_data=False):
        try:
            self._torrentaction('removedata', ids) # 实际上是removedata
            return True
        except Exception as e:
            log_msg('[ERROR] ' + repr(e))
            return False

    def start_torrent(self, ids):
        try:
            self._torrentaction('start', ids)
            return True
        except Exception as e:
            log_msg('[ERROR] ' + repr(e))
            return False
        
    def get_free_space(self):
        try:
            total, used, free = shutil.disk_usage(self.download_path)
            return free
        except Exception as e:
            log_msg('[ERROR] ' + repr(e))
            return None
        
    def download_from_content(self, content, paused=False):
        url = '%s/?%s&token=%s' % (self.base_url, 'action=add-file', self.token)
        headers = {
        'Content-Type': "multipart/form-data"
        }

        files = {'torrent_file': content}

        try:
            response = requests.post(url, files=files, auth=self.auth, cookies=self.cookies)
            hash_info = get_infohash_from_torrent(content)
            time.sleep(1)  # wait 1s for torrent add to utorrent
            torrent_info = self.get_list()
            for torrent in torrent_info:
                if torrent.id == hash_info:
                    if paused:
                        self.start(torrent.id)
                    return torrent
            else:
                log_msg("[WARNING] No torrent data found in response")
                return None
        except Exception as e:
            log_msg('[ERROR] ' + repr(e))
            return None

    def get_files(self, torrentid):
        path = 'action=getfiles&hash=%s' % (torrentid)
        status, response = self._action(path)

        files = []

        if status == 200:
            files = response.json()
        else:
            print(response.status_code)

        return files

    def start(self, torrentid):
        return self._torrentaction('start', torrentid)

    def stop(self, torrentid):
        return self._torrentaction('stop', torrentid)

    def pause(self, torrentid):
        return self._torrentaction('pause', torrentid)

    def forcestart(self, torrentid):
        return self._torrentaction('forcestart', torrentid)

    def unpause(self, torrentid):
        return self._torrentaction('unpause', torrentid)

    def recheck(self, torrentid):
        return self._torrentaction('recheck', torrentid)

    # def remove(self, torrentid):
    #     return self._torrentaction('remove', torrentid)

    def removedata(self, torrentid):
        return self._torrentaction('removedata', torrentid)

    def recheck(self, torrentid):
        return self._torrentaction('recheck', torrentid)

    def set_priority(self, torrentid, fileindex, priority):
        # 0 = Don't Download
        # 1 = Low Priority
        # 2 = Normal Priority
        # 3 = High Priority
        path = 'action=%s&hash=%s&p=%s&f=%s' % ('setprio', torrentid, priority, fileindex)
        status, response = self._action(path)

        files = []

        if status == 200:
            files = response.json()
        else:
            print(response.status_code)

        return files

    def add_file(self, file_path):

        file = []

        url = '%s/?%s&token=%s' % (self.base_url, 'action=add-file', self.token)
        headers = {
        'Content-Type': "multipart/form-data"
        }

        files = {'torrent_file': open(file_path, 'rb')}

        try:
            if files:
                response = requests.post(url, files=files, auth=self.auth, cookies=self.cookies)
                if response.status_code == 200:
                    file = response.json()
                    log_msg('file added')
                else:
                    log_msg(response.status_code)
            else:
                log_msg('file not found')

            pass
        except requests.ConnectionError as error:
            log_msg(error)
        except Exception as e:
            log_msg(e)

        return file

    def add_url(self, fiel_path):
        path = 'action=add-url&s=%s' % (fiel_path)
        status, response = self._action(path)

        files = []

        try:
            if status == 200:
                files = response.json()
            else:
                print(response.status_code)

            pass
        except requests.ConnectionError as error:
            print(error)
        except Exception as e:
            print(e)

        print(files)

        return files


# private section -->
    def _torrentaction(self, action, torrenthash):
        path = 'action=%s&hash=%s' % (action, torrenthash)

        files = []

        try:
            status, response = self._action(path)

            if status == 200:
                files = response.json()
            else:
                print(response.status_code)

        except requests.ConnectionError as error:
            print(error)
        except:
            print('error')

        return files

    def _action(self, path):
        url = '%s/?%s&token=%s' % (self.base_url, path, self.token)
        headers = {
        'Content-Type': "application/json"
        }
        try:
            response = requests.get(url, auth=self.auth, cookies=self.cookies, headers=headers)
            # use utf8 for multi-language 
            # default is ISO-8859-1
            response.encoding = 'utf8'
        except requests.ConnectionError as error:
            print(error)
        except:
            pass

        return response.status_code, response

if __name__ == '__main__':
    config = ReadConfig(filepath='../config/config.ini')
    utorrent = UTorrent(config)
    torrents = utorrent.list_torrents()
