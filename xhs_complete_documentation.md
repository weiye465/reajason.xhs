# 小红书 API 完整文档

> 来源：https://reajason.github.io/xhs/

---

# 目录

1. [主页](#主页)
2. [快速入门](#快速入门)
3. [主页爬取](#主页爬取)
4. [笔记发布](#笔记发布)

---

## 主页

# 介绍[¶](https://reajason.github.io/xhs/#id1 "永久链接至标题")
[![PyPI](https://img.shields.io/pypi/v/xhs)](https://pypi.org/project/xhs/) [![PyPI - License](https://img.shields.io/pypi/l/xhs)](https://pypi.org/project/xhs/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/xhs)](https://pypi.org/project/xhs/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xhs)](https://pypi.org/project/xhs/)
**xhs** 是一个封装小红书网页端的请求工具，既包含 [小红书（www.xiaohongshu.com）](https://www.xiaohongshu.com/) 也包含 [创作服务页（creator.xiaohongshu.com）](https://creator.xiaohongshu.com/)。
  * [介绍](https://reajason.github.io/xhs/)
  * [快速入门](https://reajason.github.io/xhs/basic.html)
    * [基础使用](https://reajason.github.io/xhs/basic.html#id2)
    * [进阶使用](https://reajason.github.io/xhs/basic.html#id3)
      * [环境安装](https://reajason.github.io/xhs/basic.html#id4)
      * [开启 Flask 签名服务](https://reajason.github.io/xhs/basic.html#flask)
      * [使用 XhsClient](https://reajason.github.io/xhs/basic.html#xhsclient)
  * [主页爬取](https://reajason.github.io/xhs/crawl.html)
    * [初始化](https://reajason.github.io/xhs/crawl.html#id2)
    * [获取笔记信息](https://reajason.github.io/xhs/crawl.html#id3)
    * [获取当前用户信息](https://reajason.github.io/xhs/crawl.html#id4)
    * [获取用户信息](https://reajason.github.io/xhs/crawl.html#id5)
    * [获取主页推荐](https://reajason.github.io/xhs/crawl.html#id6)
    * [搜索笔记](https://reajason.github.io/xhs/crawl.html#id7)
    * [获取用户笔记](https://reajason.github.io/xhs/crawl.html#id8)
    * [获取用户收藏笔记](https://reajason.github.io/xhs/crawl.html#id9)
    * [获取用户点赞笔记](https://reajason.github.io/xhs/crawl.html#id10)
    * [获取笔记评论](https://reajason.github.io/xhs/crawl.html#id11)
    * [获取笔记子评论](https://reajason.github.io/xhs/crawl.html#id12)
    * [评论笔记](https://reajason.github.io/xhs/crawl.html#id13)
    * [删除笔记评论](https://reajason.github.io/xhs/crawl.html#id14)
    * [评论用户](https://reajason.github.io/xhs/crawl.html#id15)
    * [关注用户](https://reajason.github.io/xhs/crawl.html#id16)
    * [取关用户](https://reajason.github.io/xhs/crawl.html#id17)
    * [收藏笔记](https://reajason.github.io/xhs/crawl.html#id18)
    * [取消收藏笔记](https://reajason.github.io/xhs/crawl.html#id19)
    * [点赞笔记](https://reajason.github.io/xhs/crawl.html#id20)
    * [取消点赞笔记](https://reajason.github.io/xhs/crawl.html#id21)
    * [点赞评论](https://reajason.github.io/xhs/crawl.html#id22)
    * [取消点赞评论](https://reajason.github.io/xhs/crawl.html#id23)
    * [获取二维码](https://reajason.github.io/xhs/crawl.html#id24)
    * [检查二维码状态](https://reajason.github.io/xhs/crawl.html#id25)
  * [笔记发布](https://reajason.github.io/xhs/creator.html)


# [xhs](https://reajason.github.io/xhs/)
### 导航
  * [介绍](https://reajason.github.io/xhs/)
  * [快速入门](https://reajason.github.io/xhs/basic.html)
  * [主页爬取](https://reajason.github.io/xhs/crawl.html)
  * [笔记发布](https://reajason.github.io/xhs/creator.html)


  * [ReaJason](https://reajason.eu.org)


### Related Topics
  * [Documentation overview](https://reajason.github.io/xhs/)
    * Next: [快速入门](https://reajason.github.io/xhs/basic.html "下一章")


### 快速搜索
©Copyright ReaJason. | Powered by [Sphinx 4.5.0](http://sphinx-doc.org/) & [Alabaster 0.7.12](https://github.com/bitprophet/alabaster) | [Page source](https://reajason.github.io/xhs/_sources/index.rst.txt)
[ ![Fork me on GitHub](https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png) ](https://github.com/ReaJason/xhs)


## 快速入门

# 快速入门[¶](https://reajason.github.io/xhs/basic.html#id1 "永久链接至标题")
由于 x-s 签名较复杂，因此使用 [playwright](https://playwright.dev/python/) 进行模拟浏览器行为进行 js 函数调用获取签名算法， 并且其中存在大量的环境检测的行为，因此需要使用到 [stealth.min.js](https://github.com/requireCool/stealth.min.js) 进行绕过。
**环境安装** :
```
pip install xhs # 下载 xhs 包
pip install playwright # 下载 playwright
playwright install # 安装浏览器环境
curl -O https://cdn.jsdelivr.net/gh/requireCool/stealth.min.js/stealth.min.js # 下载 stealth.min.js

```

## 基础使用[¶](https://reajason.github.io/xhs/basic.html#id2 "永久链接至标题")
请注意 cookie 的获取，a1、web_session 和 webId 三个字段为必需字段。
具体代码参考：[basic_usage.py](https://github.com/ReaJason/xhs/blob/master/example/basic_usage.py)
## 进阶使用[¶](https://reajason.github.io/xhs/basic.html#id3 "永久链接至标题")
将 playwright 封装为服务端，主函数使用 requests 请求，获取签名，多账号使用统一签名服务请确保 cookie 中的 a1 字段统一，防止签名一直出现错误
### 环境安装[¶](https://reajason.github.io/xhs/basic.html#id4 "永久链接至标题")
可以直接使用 Docker 来起下面的 Flask 服务，然后使用 XhsClient 即可，服务启动会打印 a1，推荐将自己的 cookie 中的 a1 与服务端设置成一致
```
docker run -it -d -p 5005:5005 reajason/xhs-api:latest

```

如果在本机启动 Flask 需要安装如下依赖：
```
pip install flask, gevent, requests

```

### 开启 Flask 签名服务[¶](https://reajason.github.io/xhs/basic.html#flask "永久链接至标题")
具体代码参考： [basic_sign_server](https://github.com/ReaJason/xhs/blob/master/example/basic_sign_server.py)
### 使用 XhsClient[¶](https://reajason.github.io/xhs/basic.html#xhsclient "永久链接至标题")
具体代码参考： [basic_sign_usage](https://github.com/ReaJason/xhs/blob/master/example/basic_sign_usage.py)
# [xhs](https://reajason.github.io/xhs/index.html)
### 导航
  * [介绍](https://reajason.github.io/xhs/index.html)
  * [快速入门](https://reajason.github.io/xhs/basic.html)
    * [基础使用](https://reajason.github.io/xhs/basic.html#id2)
    * [进阶使用](https://reajason.github.io/xhs/basic.html#id3)
      * [环境安装](https://reajason.github.io/xhs/basic.html#id4)
      * [开启 Flask 签名服务](https://reajason.github.io/xhs/basic.html#flask)
      * [使用 XhsClient](https://reajason.github.io/xhs/basic.html#xhsclient)
  * [主页爬取](https://reajason.github.io/xhs/crawl.html)
  * [笔记发布](https://reajason.github.io/xhs/creator.html)


  * [ReaJason](https://reajason.eu.org)


### Related Topics
  * [Documentation overview](https://reajason.github.io/xhs/index.html)
    * Previous: [介绍](https://reajason.github.io/xhs/index.html "上一章")
    * Next: [主页爬取](https://reajason.github.io/xhs/crawl.html "下一章")


### 快速搜索
©Copyright ReaJason. | Powered by [Sphinx 4.5.0](http://sphinx-doc.org/) & [Alabaster 0.7.12](https://github.com/bitprophet/alabaster) | [Page source](https://reajason.github.io/xhs/_sources/basic.rst.txt)
[ ![Fork me on GitHub](https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png) ](https://github.com/ReaJason/xhs)


## 主页爬取

# 主页爬取[¶](https://reajason.github.io/xhs/crawl.html#id1 "永久链接至标题")
## 初始化[¶](https://reajason.github.io/xhs/crawl.html#id2 "永久链接至标题")
```
xhs_client = XhsClient(cookie="", # 用户 cookie
            user_agent="", # 自定义用户代理
            timeout=10, # 自定义超时
            proxies={}) # 自定义代理

```

## 获取笔记信息[¶](https://reajason.github.io/xhs/crawl.html#id3 "永久链接至标题")
`xhs_client.get_note_by_id("笔记ID")`
## 获取当前用户信息[¶](https://reajason.github.io/xhs/crawl.html#id4 "永久链接至标题")
`xhs_client.get_self_info()`
## 获取用户信息[¶](https://reajason.github.io/xhs/crawl.html#id5 "永久链接至标题")
`xhs_client.get_user_info("用户ID")`
## 获取主页推荐[¶](https://reajason.github.io/xhs/crawl.html#id6 "永久链接至标题")
`xhs_client.get_home_feed(xhs.FeedType.RECOMMEND)`
## 搜索笔记[¶](https://reajason.github.io/xhs/crawl.html#id7 "永久链接至标题")
`xhs_client.get_note_by_keyword("搜索关键字")`
## 获取用户笔记[¶](https://reajason.github.io/xhs/crawl.html#id8 "永久链接至标题")
`xhs_client.get_user_notes("用户ID")`
## 获取用户收藏笔记[¶](https://reajason.github.io/xhs/crawl.html#id9 "永久链接至标题")
`xhs_client.get_user_collect_notes("用户ID")`
## 获取用户点赞笔记[¶](https://reajason.github.io/xhs/crawl.html#id10 "永久链接至标题")
`xhs_client.get_user_like_notes("用户ID")`
## 获取笔记评论[¶](https://reajason.github.io/xhs/crawl.html#id11 "永久链接至标题")
`xhs_client.get_note_comments("笔记ID")`
## 获取笔记子评论[¶](https://reajason.github.io/xhs/crawl.html#id12 "永久链接至标题")
`xhs_client.get_note_sub_comments("笔记ID", "父评论ID")`
## 评论笔记[¶](https://reajason.github.io/xhs/crawl.html#id13 "永久链接至标题")
`xhs_client.comment_note("笔记ID", "评论内容")`
## 删除笔记评论[¶](https://reajason.github.io/xhs/crawl.html#id14 "永久链接至标题")
`xhs_client.delete_note_comment("笔记ID", "评论ID")`
## 评论用户[¶](https://reajason.github.io/xhs/crawl.html#id15 "永久链接至标题")
`xhs_client.delete_note_comment("笔记ID", "评论ID", "评论内容")`
## 关注用户[¶](https://reajason.github.io/xhs/crawl.html#id16 "永久链接至标题")
`xhs_client.follow_user("用户ID")`
## 取关用户[¶](https://reajason.github.io/xhs/crawl.html#id17 "永久链接至标题")
`xhs_client.unfollow_user("用户ID")`
## 收藏笔记[¶](https://reajason.github.io/xhs/crawl.html#id18 "永久链接至标题")
`xhs_client.collect_note("笔记ID")`
## 取消收藏笔记[¶](https://reajason.github.io/xhs/crawl.html#id19 "永久链接至标题")
`xhs_client.uncollect_note("笔记ID")`
## 点赞笔记[¶](https://reajason.github.io/xhs/crawl.html#id20 "永久链接至标题")
`xhs_client.like_note("笔记ID")`
## 取消点赞笔记[¶](https://reajason.github.io/xhs/crawl.html#id21 "永久链接至标题")
`xhs_client.dislike_note("笔记ID")`
## 点赞评论[¶](https://reajason.github.io/xhs/crawl.html#id22 "永久链接至标题")
`xhs_client.like_comment("笔记ID", "评论ID")`
## 取消点赞评论[¶](https://reajason.github.io/xhs/crawl.html#id23 "永久链接至标题")
`xhs_client.dislike_comment("评论ID")`
## 获取二维码[¶](https://reajason.github.io/xhs/crawl.html#id24 "永久链接至标题")
`xhs_client.get_qrcode()`
## 检查二维码状态[¶](https://reajason.github.io/xhs/crawl.html#id25 "永久链接至标题")
`xhs_client.check_qrcode("二维码ID", "二维码编码")`
# [xhs](https://reajason.github.io/xhs/index.html)
### 导航
  * [介绍](https://reajason.github.io/xhs/index.html)
  * [快速入门](https://reajason.github.io/xhs/basic.html)
  * [主页爬取](https://reajason.github.io/xhs/crawl.html)
    * [初始化](https://reajason.github.io/xhs/crawl.html#id2)
    * [获取笔记信息](https://reajason.github.io/xhs/crawl.html#id3)
    * [获取当前用户信息](https://reajason.github.io/xhs/crawl.html#id4)
    * [获取用户信息](https://reajason.github.io/xhs/crawl.html#id5)
    * [获取主页推荐](https://reajason.github.io/xhs/crawl.html#id6)
    * [搜索笔记](https://reajason.github.io/xhs/crawl.html#id7)
    * [获取用户笔记](https://reajason.github.io/xhs/crawl.html#id8)
    * [获取用户收藏笔记](https://reajason.github.io/xhs/crawl.html#id9)
    * [获取用户点赞笔记](https://reajason.github.io/xhs/crawl.html#id10)
    * [获取笔记评论](https://reajason.github.io/xhs/crawl.html#id11)
    * [获取笔记子评论](https://reajason.github.io/xhs/crawl.html#id12)
    * [评论笔记](https://reajason.github.io/xhs/crawl.html#id13)
    * [删除笔记评论](https://reajason.github.io/xhs/crawl.html#id14)
    * [评论用户](https://reajason.github.io/xhs/crawl.html#id15)
    * [关注用户](https://reajason.github.io/xhs/crawl.html#id16)
    * [取关用户](https://reajason.github.io/xhs/crawl.html#id17)
    * [收藏笔记](https://reajason.github.io/xhs/crawl.html#id18)
    * [取消收藏笔记](https://reajason.github.io/xhs/crawl.html#id19)
    * [点赞笔记](https://reajason.github.io/xhs/crawl.html#id20)
    * [取消点赞笔记](https://reajason.github.io/xhs/crawl.html#id21)
    * [点赞评论](https://reajason.github.io/xhs/crawl.html#id22)
    * [取消点赞评论](https://reajason.github.io/xhs/crawl.html#id23)
    * [获取二维码](https://reajason.github.io/xhs/crawl.html#id24)
    * [检查二维码状态](https://reajason.github.io/xhs/crawl.html#id25)
  * [笔记发布](https://reajason.github.io/xhs/creator.html)


  * [ReaJason](https://reajason.eu.org)


### Related Topics
  * [Documentation overview](https://reajason.github.io/xhs/index.html)
    * Previous: [快速入门](https://reajason.github.io/xhs/basic.html "上一章")
    * Next: [笔记发布](https://reajason.github.io/xhs/creator.html "下一章")


### 快速搜索
©Copyright ReaJason. | Powered by [Sphinx 4.5.0](http://sphinx-doc.org/) & [Alabaster 0.7.12](https://github.com/bitprophet/alabaster) | [Page source](https://reajason.github.io/xhs/_sources/crawl.rst.txt)
[ ![Fork me on GitHub](https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png) ](https://github.com/ReaJason/xhs)


## 笔记发布

# 笔记发布[¶](https://reajason.github.io/xhs/creator.html#id1 "永久链接至标题")
详见 👉 [测试用例](https://github.com/ReaJason/xhs/blob/6397751d1df914c84cf4d417ad2a929737d8678e/tests/test_xhs.py#L309)
# [xhs](https://reajason.github.io/xhs/index.html)
### 导航
  * [介绍](https://reajason.github.io/xhs/index.html)
  * [快速入门](https://reajason.github.io/xhs/basic.html)
  * [主页爬取](https://reajason.github.io/xhs/crawl.html)
  * [笔记发布](https://reajason.github.io/xhs/creator.html)


  * [ReaJason](https://reajason.eu.org)


### Related Topics
  * [Documentation overview](https://reajason.github.io/xhs/index.html)
    * Previous: [主页爬取](https://reajason.github.io/xhs/crawl.html "上一章")


### 快速搜索
©Copyright ReaJason. | Powered by [Sphinx 4.5.0](http://sphinx-doc.org/) & [Alabaster 0.7.12](https://github.com/bitprophet/alabaster) | [Page source](https://reajason.github.io/xhs/_sources/creator.rst.txt)
[ ![Fork me on GitHub](https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png) ](https://github.com/ReaJason/xhs)


