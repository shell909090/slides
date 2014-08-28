# dpkg系统

## 简述

用于管理程序安装和删除的基础系统。

## 和make install的区别

1. 可以安装和卸载，并且可以管理依赖性关系。
2. 具有安装和卸载时进行配置管理的能力。
3. 可以被视做带有元信息，解压前后和删除前后会执行脚本的tar包

## 和apt的区别

1. 只能管理系统中已经安装的包
2. 不解决依赖性问题，只能报错
3. 不解决可信性问题

## 列出已安装的包和版本

	dpkg -l

# dpkg元信息

## 包元信息

1. 包名
2. 版本
3. 架构(arch)
4. 依赖(Depends)
5. 推荐(Recommands)
6. 建议(Suggests)
7. 描述

## 已安装包的状态

	dpkg -s <package>

## 查看包属性

	dpkg -I <debfile>

# dpkg内容

## 包内容

1. 所包含的文件，大小，属主，权限，日期
2. 安装前后脚本(preinst/postinst)
3. 卸载前后脚本(prerm/postrm)
4. 冲突文件(conffiles)

## 列出包里面包含的文件

	dpkg -L <package>

## 查看包内容

	dpkg -c <debfile>

# dpkg配置

## debconf

用于配置包的交互系统。

## 包状态

1. Status: Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
2. Err: (none)/Reinst-required (Status,Err: uppercase=bad)

状态标明了包在系统中处于哪个阶段。

## 安装包

	dpkg -i <debfile>

## 删除包

	dpkg -r <package>

删除配置

	dpkg -P <package>

## 配置继续

	dpkg --configure -a

# dpkg杂项

## 查找某个文件属于哪个包

	dpkg -S filepath

## 不安装解开包内容

	dpkg -x <debfile> <target>

# apt系统

## 简述

用于管理程序源的基础系统。

## 包列表

整个系统中所列的所有源里面载明的包列表。

列表里面有数据，指明某个包可以在哪个url取得，大小多少，md5/sha1/sha256。因此下载列表所指明的文件是不会遭到替换的(碰撞算法不算)。

## 更新包列表

	apt-get update
	aptitude update

## 下载包

	apt-get download <package>
	aptitude download <package>

下载源码

	apt-get source <package>
	aptitude source <package>

## 安装

	apt-get install <package>
	aptitude install <package>

## 删除

	apt-get remove <package>
	aptitude remove <package>

删除带配置

	apt-get purge <package>
	aptitude purge <package>

# apt源

## 源配置

/etc/apt/sources.list文件中，每行指明一个源。

	deb http://192.168.1.22:9999/debian/ wheezy main contrib non-free

1. 第一部分指明是二进制源(deb)还是源码源(deb-src)。
2. 第二部分指明基url。
3. 第三部分指明release。
4. 第四部分和后续指明category。

## 源的三要素

1. release，指发行版本。例如wheezy/stable, jessie/testing, sid/unstable，或者是precise/lucid等。
2. category，仓库分类。可自行选定的仓库分类，大部分发行上只有一个，即main。但是有补充，例如debian的non-free和ubuntu的restricted。
3. arch，cpu架构。无需指定安装时固定。可以用dpkg --print-architecture查看和管理。debian目前已经支持multiarch，但是效果不好说。

## 可信赖源

源给出的包列表使得下载包是安全的，但是包列表本身还可能遭到替换。为了解决这个问题，需要对包列表进行签名。apt使用的是gpg签名系统。在每个系统上，都安装了可信签名公钥。

	sudo apt-key list

凡是经过可信密钥签名的仓库，都是可信仓库。而非可信仓库添加进去的第一件事，就是添加签名公钥。

## 自建源缓存

安装approx，修改/etc/approx/approx.conf

每行一条，开始指明缓存路径，后续指明上游目标。例如：

	debian          http://mirrors.ustc.edu.cn/debian
	ubuntu          http://mirrors.163.com/ubuntu
	gplhost         http://mirrors.shell909090.org/gplhost

第一条说明[http://server:9999/debian](http://server:9999/debian)映射到[http://mirrors.ustc.edu.cn/debian](http://mirrors.ustc.edu.cn/debian)。后续同。第三条为openstack在wheezy上的backport附加源。

# 依赖求解

## 依赖关系图

1. Depends, Recommands。
2. 依赖版本>=和==。

## 手工安装和依赖安装

	aptitude search '.*' | grep '^i'
	apt-mark showmanual
	apt-mark showauto

## 冲突

	apt-cache show nginx-light
	Conflicts: nginx-extras, nginx-full, nginx-naxsi

冲突主要用于解决有相同路径的文件，具有替代功能的程序，或不兼容的版本。

## 版本升级

	apt-get upgrade
	aptitude upgrade

在版本升级中，很容易出现冲突。例如新包依赖于一个新的库，但是系统中某个未升级的程序依赖于一个老的库。两者都是强制依赖，因此不能同时存在于系统中。

## 冲突解决方案

使用aptitude，进入后可以看到冲突的存在。按E查看冲突解决方案，或调整方案。

最有效的方法是自行求解。通过自行标记某些包为安装或删除状态，解除冲突。

## 只升级安全补丁

	unattended-upgrades

由于升级的量更小，因此几乎不可能碰到冲突。
