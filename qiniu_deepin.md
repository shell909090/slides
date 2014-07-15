# 授权 #

cc-by-sa 3.0 [cn](http://creativecommons.org/licenses/by-sa/3.0/cn/) [en](http://creativecommons.org/licenses/by-sa/3.0/)

# 自我介绍 #

* python程序员
* C/C++程序员
* linux深度用户
  * debian系用户

![](http://xuzhixiang.u.qiniudn.com/photo/aboutme.png)

---

![](http://xuzhixiang.u.qiniudn.com/photo/shell01.jpg)

---

咳咳，刚刚那张不知道为什么有新浪的LOGO，让我们忽略他。

![](http://xuzhixiang.u.qiniudn.com/photo/shell01.jpg?imageMogr/crop/!300x250a150a0)

# 七牛简介 #

* 2011年创立于上海
* 做开发者的数据在线托管，加速，处理

# 云存储的意义 #

* 备份
* 高可用
* 弹性费用计算
* CDN

---

* 备份
  * 备份策略
  * 如何保证备份成功
* 高可用
 * 多机+盘阵
 * 多节点同步
 * 其他方案
* 弹性费用计算
 * 为峰值留出预量
* CDN

# 七牛云存储的特色 #

* UGC
  * 减少带宽占用，加速用户上传
  * 提供回调
* 数据处理
  * 不只是图片
* 丰富的sdk
  * C...
  * C#
  * Java
  * nodejs
  * php
  * ruby
  * python
  * ...

# 图片处理 #

* 基本信息获取
* EXIF信息获取
* 缩略图
* 裁剪，旋转
* 水印

# 流媒体处理 #

* 音频转码
* 视频转码
* 视频缩略图
* HTTP Live Streaming

# 文档转换 #

* markdown转html

# 其他 #

* 数据处理组合
* 生成qr码
* 结果持久化
* 用户提供的任意处理代码

# SDK library #

* 全部开源
* MIT授权
  * 可以链接到商业项目中
  * 可以加入Powered by qiniu
* 随时update，支持最新feature
* 使用github，鼓励用户提交pull request

# SDK utils #

* qrsync

# 实例一，本文档上传 #

* 申请帐号（10G空间，10G下载，免费），获得ak和sk
* 创建空间xuzhixiang
* 建立配置文件qiniu.json
* 下载[七牛工具组](http://docs.qiniu.com/tools/v6/qrsync.html)
* 执行`qrsync qiniu.json`
* 结果在[这里](http://xuzhixiang.u.qiniudn.com/slide/qiniu_deepin.md?md2html)

# 实例二，文章开头的图片裁剪 #

* 原始图片地址：http://xuzhixiang.u.qiniudn.com/photo/shell01.jpg
* 裁剪图片地址：http://xuzhixiang.u.qiniudn.com/photo/shell01.jpg?imageMogr/crop/!300x250a150a0

# 实例二，以html方式阅读本文档 #

在[url](http://xuzhixiang.u.qiniudn.com/slide/qiniu_deepin.md)的结尾加上md2html[试试](http://xuzhixiang.u.qiniudn.com/slide/qiniu_deepin.md?md2html)。

# 实例三，经过reveal渲染后的文档 #

* 执行自己写的工具[md2html](https://github.com/shell909090/utils/blob/master/md2slide)
* 再次执行`qrsync qiniu.json`，内容会差量上传
* 直接访问[这里](http://xuzhixiang.u.qiniudn.com/slide/qiniu_deepin.html)，可以看到结果

# 感谢观赏 #

本文可以猛击[这里](http://xuzhixiang.u.qiniudn.com/slide/qiniu_deepin.html)

![或者扫这里](http://xuzhixiang.u.qiniudn.com/slide/qiniu_deepin.html?qrcode)
