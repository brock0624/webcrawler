# -*- coding:utf-8 -*-
from selenium import webdriver
import os
import random
import time
import json
import re
from bs4 import BeautifulSoup
import requests

def login_qzone(driver, user, passwd):
    driver.get('https://user.qzone.qq.com/%s/' % user)  # URL
    driver.implicitly_wait(10)  # 隐示等待，为了等待充分加载好网址
    driver.find_element_by_id('login_div')
    driver.switch_to_frame('login_frame')  # 切到输入账号密码的frame
    driver.find_element_by_id('switcher_plogin').click()  ##点击‘账号密码登录’
    driver.find_element_by_id('u').clear()  ##清空账号栏
    driver.find_element_by_id('u').send_keys(user)  # 输入账号
    driver.find_element_by_id('p').clear()  # 清空密码栏
    driver.find_element_by_id('p').send_keys(passwd)  # 输入密码
    driver.find_element_by_id('login_button').click()  # 点击‘登录’
    driver.switch_to_default_content()
    print("login success")
    driver.implicitly_wait(10)
    time.sleep(3)


def get_cookies(driver, filepath):
    cookie = {}  # 初始化cookie字典
    filename = os.path.join(filepath, "cookies.txt")
    with open(filename,"w") as f:
        for elem in driver.get_cookies():  # 取cookies
            cookie[elem['name']] = elem['value']
            f.write("%s=%s\n" % (elem['name'], elem['value']))
    return cookie

def get_qzonetoken(driver,uin):
    url = "https://user.qzone.qq.com/%s/" % uin
    driver.get(url)
    html = driver.page_source
    g_qzonetoken = re.search('window\.g_qzonetoken = \(function\(\)\{ try\{return (.*?);\} catch\(e\)',
                             html)

    return g_qzonetoken

def get_GTK(cookie):
    hashes = 5381
    for letter in cookie['p_skey']:
        hashes += (hashes << 5) + ord(letter)
    return hashes & 0x7fffffff

# 获得好友列表  注意下面的链接
def get_friend_list(driver,uin,gtk,qzonetoken):
    url = "https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_hat_get.cgi?hat_seed=1&uin={uin}&fupdate=1&g_tk={gtk}&qzonetoken={qzonetoken}".format(
        uin=uin,gtk=gtk,qzonetoken=qzonetoken
    )
    driver.get(url)
    friends = str(driver.page_source).lstrip("_Callback(").rstrip(");")
    friends_dict = json.loads(friends)
    print(friends_dict)
    return friends_dict

def format_time(date):
    a = date[:-6].replace('年', '-').replace('月', '-').strip('日')
    b = a.split('-')
    for i in range(2):
        b[1] = b[1].zfill(2)  # 左填充
        b[2] = b[2].zfill(2)
    b = ''.join(b)
    return b

def download_img(img_url, img_name):
    print(img_url)
    header = {}
    # header = {"Authorization": "Bearer " + api_token} # 设置http header，视情况加需要的条目，这里的token是用来鉴权的一种方式
    try:
        r = requests.get(img_url, headers=header, stream=True)
        print(r.status_code) # 返回状态码
        if r.status_code == 200:
            open(img_name, 'wb').write(r.content) # 将内容写入图片
        del r
    except Exception as e:
        print("图片没有下载成功 %s %s" % (img_name,img_url))

def get_qzone(driver,qq,filepath,startpage,pagetotal):
    driver.get('https://user.qzone.qq.com/{}/311'.format(qq))
    driver.implicitly_wait(10)
    time.sleep(3)
    # 判断是否QQ空间加了权限,如果能拿到头像说明已经进入
    try:
        driver.find_element_by_id('QM_OwnerInfo_Icon')
    except:
        print("该qq: %s没有访问权限" % qq)
        return 1

    if not os.path.exists(os.path.join(filepath,qq)):
        os.mkdir(os.path.join(filepath,qq))
        os.mkdir(os.path.join(filepath, qq,"images"))
    filename = os.path.join(filepath,qq,"title.txt")
    page = 1
    if startpage != 1:
        page = startpage
        # 跳转至指定页
        driver.switch_to_frame('app_canvas_frame')
        driver.find_element_by_id("pager_go_0").send_keys(startpage)
        driver.find_element_by_id("pager_gobtn_0").click()  # 点击下一页
        driver.switch_to.default_content()  # 跳出当前frame

    try:
        while page <= pagetotal:
            ##下拉
            for j in range(1, 5):
                driver.execute_script("window.scrollBy(0,5000)")
                time.sleep(2)

            driver.switch_to_frame('app_canvas_frame')  # 切入说说frame
            bs = BeautifulSoup(driver.page_source.encode('GBK', 'ignore').decode('gbk'))

            pres = bs.find_all('pre', class_='content')

            for pre in pres:
                id = random.randint(11,99)
                shuoshuo = pre.text
                tx = pre.parent.parent.find('a', class_="c_tx c_tx3 goDetail")['title']
                dt = format_time(tx)
                imglist = pre.parent.parent.find('div',class_="img-attachments-inner clearfix")
                print(tx + "\t" + shuoshuo.replace("\r","").replace("\n","&&"))
                with open(filename,"a+") as f:
                    f.write(dt+"\t"+str(id)+"\t"+tx + "\t" + shuoshuo.replace("\r","").replace("\n","&&")+"\n")
                if not imglist:
                    continue
                elif not imglist:
                    continue
                for img in imglist.contents:
                    imgid = random.randint(1001,2001)
                    imgname = "IMG_%s_%s%s.jpg" % (dt,str(id),str(imgid))
                    imgurl = img.attrs["href"]
                    print(imgurl)
                    download_img(imgurl,os.path.join(filepath, qq,"images",imgname))

            print("page %s 当前页已经处理完成" % page)
            driver.find_element_by_link_text(u'下一页').click()  # 点击下一页
            page = page + 1
            driver.switch_to.default_content()  # 跳出当前frame
            time.sleep(3)

        driver.quit()
    except Exception as e:
        # 我没有判断什么时候为最后一页，当爬取到最后一页，
        # 默认点击下一页，会出现异常，我直接在这认为它是爬到末尾了，还是有待优化
        print(e)
        print("没有跳转到下一页，可能出现了问题")

        driver.quit()
        driver.close()




def main():
    print("start")
    filepath = 'D:\\data\\webcrawler\\qqzone'
    user = 'xxxxx'
    passwd = 'xxxxx'
    puin = 'xxxxx'
    startpage = 10
    # 爬取前多少页的记录
    pagetotal = 1000
    driver = webdriver.Chrome("D:\\app\\chromedriver\\chromedriver.exe")
    driver.maximize_window()  # 窗口最大化
    login_qzone(driver, user, passwd)
    # cookies = get_cookies(driver, filepath)
    # gtk = get_GTK(cookies)
    # qzonetoken = get_qzonetoken(driver,user)
    # get_friend_list(driver,user,gtk,qzonetoken)

    get_qzone(driver,puin,filepath,startpage,pagetotal)



if __name__ == '__main__':
    main()
