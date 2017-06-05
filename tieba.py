# _*_ coding:utf-8 _*_
import re
import json
import Queue
import hashlib
import requests
import threading

from settings import *
from create_table import *


##----通过贴吧名kw获取tids帖子列表-------##
def getTidsByKw(kw='', start_page=0, end_page=0):
    tids = []
    for pn in xrange(start_page, end_page):
        data = [
            '_client_id=wappc_1396611108603_817',
            '_client_type=2',
            '_client_version=5.7.0',
            '_phone_imei=642b43b58d21b7a5814e1fd41b08e2a6',
            'from=tieba',
            'kw=' + kw,
            'pn=' + str(pn),
            'q_type=2',
            'rn=30',
            'with_group=1']
        # print getSignByPostData(data)
        # print data
        data.append("sign=" + getSignByPostData(data))
        # 定义post的地址
        url = 'http://c.tieba.baidu.com/c/f/frs/page'
        # post_data = urllib.urlencode(data)
        post_data = "&".join(data)
        # 设置头部
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Referer': 'http://tieba.baidu.com/',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
                   'Connection': 'keep-alive'}
        # req.add_header('Content-Type','application/x-www-form-urlencoded');
        # req.add_header('Referer','http://tieba.baidu.com/');
        # req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0');
        # req.add_header('Connection','keep-alive');
        # print post_data
        # 提交，发送数据
        response = requests.post(url=url,data=post_data,headers=headers)
        content = response.content
        forum_json = json.loads(content)
        tids = tids + forum_json['forum']['tids'].split(',')
    return tids

##----通过tid获取帖子内容，依然用抓包的形式----##
def getThreadByTid(tid, pn='0'):
    data = ['_client_id=wappc_1396611108603_817',
            '_client_type=2',
            '_client_version=5.7.0',
            '_phone_imei=642b43b58d21b7a5814e1fd41b08e2a6',
            'from=tieba',
            'kz=' + tid,
            'pn=' + pn,
            'q_type=2',
            'rn=30',
            'with_floor=1']
    # print getSignByPostData(data)
    # print data
    data.append("sign=" + getSignByPostData(data))
    # 定义post的地址
    url = 'http://c.tieba.baidu.com/c/f/pb/page'
    # post_data = urllib.urlencode(data)
    post_data = "&".join(data)
    # 设置头部
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Referer': 'http://tieba.baidu.com/',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
               'Connection': 'keep-alive'}
    # req.add_header('Content-Type','application/x-www-form-urlencoded');
    # req.add_header('Referer','http://tieba.baidu.com/');
    # req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0');
    # req.add_header('Connection','keep-alive');
    # print post_data
    # 提交，发送数据
    response = requests.post(url=url,data=post_data,headers=headers)
    content = response.content
    return content


##----从获取的tid的帖子中，抓取贴吧名、tid等信息放入字典中（中间包含获取贴吧内容函数和正则匹配函数）----##
def fetchByThreadId(tid):
    info_list = []
    thread_json = getThreadByTid(tid=tid, pn='0')
    thread = json.loads(thread_json)
    if thread is None or 'thread' not in thread:
        return []
    pn_total = int(thread['thread']['valid_post_num']) / 30 + 1
    for x in xrange(0, pn_total):
        thread_json = getThreadByTid(tid=tid, pn=str(x))
        thread = json.loads(thread_json)
        for thread_text in thread['post_list']:
            # print thread_text['content'][0]['text'].encode('utf8')
            if len(thread_text['content']) > 0:
                if thread_text['content'][0].has_key('text'):
                    info = getInfoByInput(thread_text['content'][0]['text'].encode('utf8')) #正则匹配贴吧内容
                    if len(info) != 0:
                        info_dict = {}
                        info_dict['tieba'] = thread['forum']['name']
                        info_dict['name'] = thread_text['author']['name']
                        info_dict['email'] = info['email']
                        info_dict['telephone'] = info['phone']
                        info_dict['thread'] = thread_text['content'][0]['text'].encode('utf8')
                        info_dict['tid'] = tid
                        info_dict['cid'] = thread_text['id']
                        info_list.append(info_dict)
    return info_list


##----通过post数据获得sign校验码----##
def getSignByPostData(post_data):
    sign = hashlib.md5()
    # print "".join(post_data)
    sign.update("".join(post_data) + "tiebaclient!!!")
    return sign.hexdigest()

##-------用正则匹配电话号和邮箱---------##
def getInfoByInput(input):
    """
    说明：
    [^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$匹配邮箱。
    综合目前国内常用的邮箱，大概通用的规则包括：
    1、[^\._]，不能以下划线和句点开头。
    2、[\w\.]+，包括字母、数字。而对句点及下划线各提供商有差别，对此有效性不做更严格的判断。
    3、@是必须的。
    4、(?:[A-Za-z0-9]+\.)+[A-Za-z]+$，@后以xxx.xxx结尾，考虑到多级域名，会有这种情况xxx.xxx.xxx如xxx@yahoo.com.cn
    ^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}$匹配电话号码。
    只考虑国内的情况,大概通用的规则包括：
    1、^0\d{2,3}，固定电话区号3-4位数字，以0开头。
    2、d{7,8}$，固定电话一般7-8位数字。
    3、国内目前的手机号码都是11位数字，三大运营商的号码段基本都在上面列出来了，我们这里除了147的号码的段，其他的都只考虑前两位，
    第三位就不考虑了，否则，工作量也很大。前两位包括13*、15*、18*。
    """

    regex_email = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b", re.IGNORECASE)
    regex_phone = re.compile(r"1[3|4|5|7|8]\d{9}\b", re.IGNORECASE)
    result = {}
    result['email'] = re.findall(regex_email, input)
    result['phone'] = re.findall(regex_phone, input)
    return result


##-----建立线程函数，运营函数----##
class Worker(threading.Thread):

    def run(self):
        while True:
            tid = tids_queue.get()
            print('fetch thread by tid : ' + tid)
            info = fetchByThreadId(tid)
            for x in info:
                if len(x['email']) != 0 or len(x['telephone']) != 0:
                    print x
                    Sql().mysql_insert_data(x)
            # signals to queue job is done
            tids_queue.task_done()

##------------开始运行------------##
def start_run():
    tids_queue = Queue.Queue() #创建队列
    tids_list = getTidsByKw(kw=kw, start_page=start_page, end_page=end_page)
    print len(tids_list)

    if len(tids_list) == 0:
        print "无法抓取到tid"
        quit()
    ##--- tids加入queue中 ----##
    for tid in tids_list:
        tids_queue.put(tid)
    return tids_queue

if __name__ == '__main__':
    tids_queue = start_run()
    for x in range(thread_count):
        t = Worker()
        t.setDaemon(True)
        t.start()

    tids_queue.join()
    print u'先森，您要的邮箱和球球号都为你准备到数据库里啦，请注意查收'
