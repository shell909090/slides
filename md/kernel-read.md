# Abstract

1. Quick introduce how TCP handshake works, how listen and accept works.
2. Introduce several ways and tools to read kernel.
3. Demonstrate how to do it.

# Keywords

* linux
* tcp
* listen
* accept
* synflood

# Copyright & License

Copyright (C) 2019  Shell.Xu <shell909090@gmail.com>

Text is available under the [Creative Commons Attribution-ShareAlike License](https://creativecommons.org/licenses/by-sa/4.0/legalcode)

# 摘要

1. 简单介绍tcp握手原理，理解listen和accept的机制。
2. 介绍代码阅读的几种手段和工具。
3. 简单演示如何阅读linux源码。

# TCP握手

TCP握手可以简单分为三步[13]，但实际上加上前后过程总共有六步。

假定发起方为A，接收方为B。A的连接socket称为Ac。B的listen socket称为Bl，accept出来的socket成为Ba。

1. B首先建立Bl，调用listen，设定队列大小。 (前置步骤例如建立socket等省略)
2. A对Ac调用connect，内核发送SYN报文。
3. B内核收到SYN报文，找到Bl。Bl在内核经过一定处理后决定是否返回SYN&ACK报文。
4. A收到SYN&ACK报文，找到Ac。Ac在内核经过一定处理后返回ACK报文，并且A连接建立就绪，可以收发数据。
5. B收到ACK报文，找到或建立Ba。Ba连接建立就绪，进入accept队列。
6. B对Bl调用accept，获得Ba。

不同系统实现的差别有：

1. 第3步中，内核如何决定是否返回SYN&ACK报文。其中主要考虑SYN flood[3][4]的防御。
2. Ba在第3步建立还是第5步建立。
3. Ba在第3步到第5步的状态(我们称为半握手状态)，是否放入accept队列，还是保持一个单独队列[1]。
4. 如何加速上述流程。

# manual

根据文献[10]

    The behavior of the backlog argument on TCP sockets changed with Linux 2.2.  Now it specifies the queue length for completely established sockets waiting to be accepted, instead of the number  of  incomplete  connection  re‐
	quests.   The  maximum  length  of  the  queue for incomplete sockets can be set using /proc/sys/net/ipv4/tcp_max_syn_backlog.  When syncookies are enabled there is no logical maximum length and this setting is ignored.  See
	tcp(7) for more information.

# utils

1. [lxr](https://elixir.bootlin.com/linux/latest/source)
2. [github repository](https://github.com/torvalds/linux)
3. [github release](https://github.com/torvalds/linux/releases)

# 阅读重点

1. struct sock
2. struct socket
2. struct inet\_connection\_sock
3. struct inet\_sock

sock和socket互相指向。inet\_connection\_sock包含inet\_sock，inet\_sock包含sock。

1. EXPORT\_SYMBOL(inet\_listen)
2. EXPORT\_SYMBOL(inet\_accept)
3. tcp\_v4\_rcv
   1. \_\_inet\_lookup\_skb
	   1. \_\_inet\_lookup
	   2. \_\_inet\_lookup\_established 开链法(Separate chaining with linked lists)[8][9]
	   3. \_\_inet\_lookup\_listener 注意reuseport[11][12]和INADDR_ANY的处理
   2. tcp\_check\_req
	   1. inet\_csk\_complete\_hashdance
	   2. inet\_csk\_reqsk\_queue\_add
   3. tcp\_v4\_do\_rcv
	   1. tcp\_rcv\_state\_process 重点process
	   2. tcp\_v4\_conn\_request
	   3. tcp\_conn\_request
	   4. inet\_csk\_reqsk\_queue\_hash\_add req加hash表，不是sk
	   5. reqsk\_queue\_hash\_req
	   6. inet\_ehash\_insert

# 结论

1. 当没有synflood[3][4]时，正常返回。synflood时(超过sysctl\_max\_syn\_backlog[2]的3/4)，未开启syncookie[4][5]则丢弃。
2. Ba在第3步建立，而后进入hashinfo结构。第5步通过hashinfo找到Ba，检验ack通过后进入accept\_queue。
3. Ba在半握手状态直接装入hashinfo。后续使用定时器重发SYN&ACK，直到超过tcp\_synack\_retries[2]规定的极限。
4. fastopen[6][7]有助于这个过程。

# references

1. [How TCP backlog works in Linux](http://veithen.io/2014/01/01/how-tcp-backlog-works-in-linux.html) [14]
2. [ip-sysctl.txt](https://github.com/torvalds/linux/blob/master/Documentation/networking/ip-sysctl.txt)
3. [SYN flood](https://en.wikipedia.org/wiki/SYN_flood)
4. [SYN Flood Mitigation with synsanity](https://github.blog/2016-07-12-syn-flood-mitigation-with-synsanity/) [15]
5. [SYN cookies](https://en.wikipedia.org/wiki/SYN_cookies)
6. [TCP Fast Open](https://en.wikipedia.org/wiki/TCP_Fast_Open)
7. [TCP-Fast-Open-Experimentation](https://github.com/derikclive/TCP-Fast-Open-Experimentation)
8. [Hash table](https://en.wikipedia.org/wiki/Hash_table)
9. [An hashtable implementation in C](https://gist.github.com/phsym/4605704)
10. [listen](http://man7.org/linux/man-pages/man2/listen.2.html)
11. [socket](http://man7.org/linux/man-pages/man7/socket.7.html)
12. [The SO_REUSEPORT socket option](https://lwn.net/Articles/542629/)
13. [Transmission Control Protocol#Connection establishment](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Connection_establishment)
14. [github bsd kernel](https://github.com/freebsd/freebsd/blob/master/sys/netinet/tcp_input.c#L544)
15. [tproxy](https://github.com/torvalds/linux/blob/master/Documentation/networking/tproxy.txt)
