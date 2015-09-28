%title: linux system security and tuning - basic
%author: Shell.Xu <shell909090@gmail.com>
%date: 2015-09-18



-> linux system security and tuning - basic <-

-------------------------------------------------

-> 目录 <-

* linux基本系统设定
  * 设定sudo
  * 系统密码设定
  * 系统用户管理
  * 设定启动项
  * 设定apt
* 防火墙设定
  * 设定iptables
* ssh设定
  * 设定ssh服务端
  * ssh身份验证方法
  * 设定~/.ssh
  * 设定ssh client config
  * ssh的一些用法
* 内核参数设定
  * 设定sysctl

-------------------------------------------------

-> 设定sudo <-

安装sudo
^
adduser shell sudo
^
(options)%sudo ALL=(ALL:ALL) NOPASSWD: ALL
^
完成后可以使用user身份工作，而不是root。

-------------------------------------------------

-> 系统密码设定 <-

如果你的root密码强度小于10字节，那么加强强度。
root密码在防护很多猜解上都有意义，加强root密码是不论原因的。
建议root密码半年到一年一换。
^

系统密码主要有几个用途。

1. 防护console界面有人登录(例如有人获得虚拟机操作界面，或者接入了物理设备)。
2. 防止su。
3. 具有任意sudo权限的用户，被知道密码等同于root密码泄漏(su成该用户，sudo输密码)。
^

所以从上面可以看出。

1. root不能禁用。
2. 具备sudo权限的用户，也需要设定一个强密码。

-------------------------------------------------

-> 系统用户管理 <-

passwd的第二个字段是可选的加密后密码，现已废弃。如果不带':x:'的用户肯定是无法正常使用的
grep -v ':x:' /etc/passwd
^

找到没有密码的用户
cat /etc/shadow | cut -d: -f 1,2 | grep '!'
^

找到被锁定的用户
cat /etc/shadow | cut -d: -f 1,2 | grep '*'
^

passwd -u -l可以锁定解锁用户
^

找到带有过期密码的用户
cat /etc/shadow | cut -d: -f 1,2 | grep '!!'

-------------------------------------------------

-> 设定启动项 <-

安装sysv-rc-conf。
或者查看/etc/rc2.d和/etc/rcS.d。

-------------------------------------------------

-> 设定apt <-

检查/etc/apt/sources.list
^

正常的apt设定，一般包括一个主mirror，和一个security mirror。

例如我本地的配置中，主mirror为http://mirrors.ustc.edu.cn/debian
security mirror为http://security.debian.org/

不是每个mirror都做了security的！
^

在安装系统的最后一步，要设定合适的apt mirrors。更新列表并升级。

sudo apt-get update
sudo apt-get upgrade -s | grep -i security

-------------------------------------------------

需要分开的理由是。主mirror的镜像量很大，同步节点很多的时候，会有同步延迟周期。
从包进入主镜像，到你可以下载，中间有数小时到数天的延迟。

而安全有关的包不能停留数天后才安装。
因此security有关的mirrors越上游越好，内容越少越好。

一般我会直接做一个最上游的镜像，然后所有内部都指向镜像。
在万不得已时，可以清理缓存，直接从最上游更新补丁。

我也建议在允许的情况下，security不要使用缓存，自己能够控制的除外。

-------------------------------------------------

-> 设定iptables <-

1. 安装iptables-persistent
^
2. -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
^
3. -A INPUT -i lo -j ACCEPT
^
4. -A INPUT -p icmp -j ACCEPT
^
5. -P INPUT DROP
^
6. iptables-save > /etc/iptables/rules.v4
^
7. 检查ip addr，如果有ipv6地址，需要同样设定ipv6。

-------------------------------------------------

-> 设定ssh服务端 <-

UseDNS no
关闭DNS可以减少登录时开销
^

PermitRootLogin no
^

PasswordAuthentication no
如果没有特别的理由，一定要禁用密码登录
^

安装fail2ban(或者denyhosts)
^

设定AllowUsers(options)
^

设定ClientAliveInterval(options)
^

LogLevel to VERBOSE(options)

-------------------------------------------------

-> ssh身份验证方法 <-

pubkey是靠谱的方法，这应是第一建议和默认值
^

启用密码登录的话，需要注意哪些用户可以登录。
在没有设定PermitEmptyPasswords和AllowUsers的情况下，会有潜在风险。
当然，PermitEmptyPasswords默认关闭。
^

同时，有些很少用的帐号设定了弱密码，也一样会有问题。
所以最好禁止密码登录。一定要用的话建议开AllowUsers。
^

禁用root登录在很多地方有额外好处，例如密码登录的情况下，可以防护猜解root密码。
虽然在关闭了密码登录，或者启用fail2ban的情况下不需要顾虑这个。
^

禁用root登录的意义在于，"root登录"不是一个正常需求。
你不应当一直使用root干活，而是应当尽量以普通用户工作，直到需要sudo。
万一一直需要root，可以sudo bash。

-------------------------------------------------

-> 设定~/.ssh <-

需要登录的，生成~/.ssh/id\_rsa
需要被登录的，添加~/.ssh/authorized\_keys
^

id\_rsa需要加密，具体用ssh-keygen -p -f ~/.ssh/id\_rsa修改密码
^

使用ssh-agent可以简化密码输入，方法是启动ssh-agent，并将返回添加到环境变量中。
一般系统中默认会启动ssh-agent。
^

启动时用ssh-add添加一项密钥，添加时输入密码。连接时不需要密码。
ssh-add -L可以看到哪些被缓存了密码。
^

确认authorized_keys，id_rsa，id_dsa的权限小于600。建议将整个.ssh全部700掉

-------------------------------------------------

-> 设定ssh client config <-

设定control master
ControlMaster auto
ControlPath /tmp/ssh_mux_%h_%p_%r
ControlPersist 10m
^

优点是ssh断开时链接不断开，重复连接效率很高。
多次连接同一台机器也走同一根连接，不重复发起tcp连接。
^

缺点是ssh出问题时，master连接很久才会自动断开。
需要ssh -O exit手工断开。
修改配置也是一样的。
例如ssh上去后，想再开一个ssh -L。就需要先ssh -O exit。
^

Protocol 2
IgnoreRhosts yes
ForwardAgent yes
^

(options)X11Forwarding no

-------------------------------------------------

-> ssh的一些用法 <-

本地端口映射ssh -L localport:remoteip:remoteport。
将本地的localport端口映射到远程的remoteip:remoteport。
例如将本地的8080端口映射到www.google.com:80。
访问本地localhost:8080时，等于在目标机器上访问google。
^

可以用于访问内部网络中的端口，基本是安全的。
^

远程端口映射ssh -R remoteport:localip:localport。
将远程的remoteport映射到本地的localip:localport。
基本原理和-L类似，可以用于将本地服务公开到远程提供服务。

-------------------------------------------------

-> 设定sysctl <-

在/etc/sysctl.d/下面放文件即可生效，不需要直接修改/etc/sysctl.conf。
^

直接生效的方法。
sudo sysctl -p /etc/sysctl.d/net.conf
^

当然，保险的话在自己目录下写net.conf，生效，再复制到/etc/sysctl.d/下。
^

net.ipv4.tcp_congestion_control = htcp
拥塞控制算法，默认为cubic。如果是reno，请至少改成cubic。
