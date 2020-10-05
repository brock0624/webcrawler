# web crawler

web crawler是一个简单的爬虫工具类，需要不断地完善

1、京东，根据给出一个起始地址，将该页面上的所有商品抓取部分信息写入数据库，可根据需要卸载其他地方。

​	如果页面上有下一页，则递归处理后续数据

​	需要使用selenium控制浏览器

通过以下查看复用优惠的商品

~~~
select DISTINCT * from 
(select  good_url from jd_items where good_sign = '300-60') t1
INNER JOIN
(select  good_url from jd_items where good_sign = '399-200') t2
where t1.good_url = t2.good_url
~~~

