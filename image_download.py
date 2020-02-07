#http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&word=%E7%BE%8E%E5%A5%B3&pn=0&rn=60
# 根据不断尝试，可以发现，rn代表传输多少数据，最大为60，pn代表从第几个数据显示

from threading import Thread
from bs4 import BeautifulSoup
import requests
import imghdr
import json
import re    #正则匹配
import time  #延时用
import os

class BaiDuImage(object):

    def __init__(self):
        # self.url = 'https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&rn=60&word=xxx'
        self.url = 'https://image.baidu.com/search/acjson'
        self.key_word = input("what you want to download:")
        self.image_path = ''
        dir_list = os.listdir('./')
        self.image_path = './' + self.key_word + '/'
        if self.key_word not in dir_list:
            os.mkdir(self.image_path)
        self.image_num = input("how much photo you want:")  # html request times
        while not self.image_num.isdigit():
            self.image_num = input("wrong input.please re-enter:")

        self.image_num = int(self.image_num)
        print("you want " + str(self.image_num) + " photo about :[" + self.key_word + "].")
        time.sleep(1)
        self.count = 0
        self.page_count = 0
        self.num_per_page = 30                                      #the number of image per page
        self.header = {}                                            #html request header
        self.start_time = time.time()

    def get_input(self):
        self.key_word = input("what you want to download:")
        self.image_path = ''
        dir_list = os.listdir('./')
        if self.key_word not in dir_list:
            self.image_path = './' + self.key_word
        os.mkdir(self.image_path)
        self.image_num = input("how much page you want:")  # html request times
        while not self.page_num.isdigit():
            self.image_num = input("wrong input.please re-enter:")

        self.image_num = int(self.image_num)
        print("you want " + str(self.image_num) + " page image about :[" + self.key_word + "].")
        time.sleep(1)
        return

    def download(self):
        while self.count < self.image_num:
            self.data = {'word': self.key_word,                 # key word
                    'pn': self.num_per_page * self.page_count,  # start position
                    'rn': self.num_per_page,                    # image quantity per page
                    'ipn': 'rj', 'tn': 'resultjson_com'}        # request word,but I don't know how it works
            html = self.get_html()
            links = self.get_image_url(html=html)
            self.thread_save(links=links)
            self.page_count += 1

    def get_html(self):
        html = requests.get(self.url,params=self.data,headers=self.header)
        if str(html.status_code) == '200':
            print("[INFO]:requests 200,OK! image number:[{}:{}].".format(self.data['pn'],self.data['pn']+self.data['rn']))
            return html
        else:
            print('[INFO]:request failed.--[{}] URL[{}]'.format(html.status_code,html.url))
            return False

    def get_image_url(self,html):
        links = []
        cnt = 0
        js = json.loads(html.content.decode())
        for data in js["data"]:
            if ('replaceUrl' in data) and (len(data['replaceUrl']) > 1):
                link = data['replaceUrl'][1]['ObjURL']
                links.append(link)
        return links

    def get_image(self,link,image_name):
        try:
            img = requests.get(link)
            if str(img.status_code) == '200':
                with open(image_name,'wb') as f:
                    f.write(img.content)
                    f.close()
                if imghdr.what(image_name) == None:                         #image break,remove it
                    os.remove(image_name)
                    print('[INFO]:iamge break.delete {}'.format(image_name))
                else:
                    dir_path = image_name.replace(image_name.split('/')[-1],'')
                    with open(dir_path + 'image_url.txt','a') as txt:
                        txt.write(str(self.count) + '\t' + link + '\r\n')
                    final_name = image_name + '.' + imghdr.what(image_name)
                    os.rename(image_name,final_name)
                    print("[INFO]:image {} saved.".format((final_name)))
                    self.count += 1
            else:
                print('[INFO]:get image failed.--[{}]'.format(img.status_code))
        except Exception as err:
            print(err)
            return

    def thread_save(self, links):
        for i,link in enumerate(links):
            image_name = self.image_path + str(self.count)
            print("[INFO]:saving image:{} URL:{}".format(image_name,link))
            t = Thread(self.get_image(link=link,image_name=image_name))
            t.start()
            t.join()
            if self.count >= self.image_num:
                return

    def __del__(self):
        print('download quantity:{}'.format(self.count))
        print('time used:{} s'.format(time.time() - self.start_time))

def main():
    image_saver = BaiDuImage()
    image_saver.download()

if __name__ == "__main__":
    main()