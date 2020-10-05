# -*- coding:utf-8 -*-
'''
爬取京东商品信息:
    请求url:
        https://www.jd.com/
    提取商品信息:
        1.商品详情页
        2.商品名称
        3.商品价格
        4.评价人数
        5.商品商家
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from threading import Thread
from models import JdItems, Session

session = Session()


def get_good(driver):
    try:

        # 通过JS控制滚轮滑动获取所有商品信息
        js_code = '''
            window.scrollTo(0,5000);
        '''
        driver.execute_script(js_code)  # 执行js代码

        # 等待数据加载
        time.sleep(2)

        # 3、查找所有商品div
        # good_div = driver.find_element_by_id('J_goodsList')
        good_list = driver.find_elements_by_class_name('gl-item')
        n = 1
        for good in good_list:
            # 根据属性选择器查找
            # 商品链接
            good_url = good.find_element_by_css_selector(
                '.p-img a').get_attribute('href')

            # 商品名称
            good_name = good.find_element_by_css_selector(
                '.p-name em').text.replace("\n", "--")

            # 商品价格
            good_price = good.find_element_by_class_name(
                'p-price').text.replace("\n", ":")

            # 评价人数
            good_commit = good.find_element_by_class_name(
                'p-commit').text.replace("\n", " ")

            # 促销方式
            # good_sign = good.find_element_by_class_name(
            #     'sign-title').text.replace("\n", ":")
            good_sign = "399-200"

            # 促销时间
            # good_sign_date = good.find_element_by_class_name(
            #     'sign-date').text.replace("\n", ":")
            good_sign_date = ""

            good_content = f'''
                        商品链接: {good_url}
                        商品名称: {good_name}
                        商品价格: {good_price}
                        评价人数: {good_commit}
                        促销方式: {good_sign}
                        促销时间: {good_sign_date}
                        \n
                        '''
            # print(good_content)
            save_to_db(good_url, good_name, good_price, good_commit, good_sign, good_sign_date)
            # with open('jd.txt', 'a', encoding='utf-8') as f:
            #     f.write(good_content)
        if driver.find_element_by_class_name('pn-next'):
            next_tag = driver.find_element_by_class_name('pn-next')
            # next_tag.click()
            next_tag.send_keys(Keys.ARROW_RIGHT)
            print("now:%s,next" % driver.current_url)
            time.sleep(2)

            # 递归调用函数
            get_good(driver)

            time.sleep(10)
        else:
            print("没有找到下一页了，END")

    finally:
        # driver.close()
        pass


def async_save_to_db(item):
    try:
        session.add(item)
        session.commit()
    except Exception as e:
        print("插入失败")
        raise


def save_to_db(good_url, good_name, good_price, good_commit, good_sign, good_sign_date):
    try:
        item = JdItems(good_url=good_url, good_name=good_name, good_price=good_price,
                       good_commit=good_commit, good_sign=good_sign,
                       good_sign_date=good_sign_date)
        # thr = Thread(target=async_save_to_db, args=[item])
        # thr.start()
        session.add(item)
        session.commit()
    except:
        print("{good_url}插入失败".format(good_url=good_url))


def get_youhui(youhui):
    start_url = "https://search.jd.com/Search?{youhui}".format(youhui=youhui)
    driver = webdriver.Chrome(executable_path="D:\\app\\chromedriver\\85.0.4183.87\\chromedriver.exe")
    driver.implicitly_wait(10)
    # 1、往京东主页发送请求
    driver.get(start_url)
    get_good(driver)


def get_search():
    good_name = input('请输入爬取商品信息:').strip()

    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    # 1、往京东主页发送请求
    driver.get('https://www.jd.com/')

    # 2、输入商品名称，并回车搜索
    input_tag = driver.find_element_by_id('key')
    input_tag.send_keys(good_name)
    input_tag.send_keys(Keys.ENTER)
    time.sleep(2)

    get_good(driver)
