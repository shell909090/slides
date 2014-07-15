# 元编程 #

## 黑魔法防御 ##

元编程是一种黑魔法，正派人士都很畏惧。——张教主

## 何谓元编程 ##

* 编写一个程序，能够操纵，改变其他程序，这就是元编程
* 最简单的来说，C的宏就是元编程的一种
* 元编程的另一大代表则是lisp的宏
* 虽然不常见，但是汇编级别也是可以元编程的，例如可执行文件压缩
* 如果源语言和目标语言一样，就是我们最常见的反射

## 元编程的几种形式 ##

* 文本宏语言，C宏，M4，Flex，Bison，Gperf
* S表达式宏，lisp/scheme
  S表达式的特殊之处在于，他既是数据又是代码，因此S表达式宏可以很轻易的改变代码结构
* 反射，动态数据结构变更

## python下元编程的几个手段 ##

* 预定义方法
* 函数赋值
* descriptor
* 元类
* eval

## 预定义方法 ##

没啥好多说的，看下面这个例子：

	class A(object):
	 
		def __init__(self, o):
			self.__obj__ = o
	 
		def __getattr__(self, name):
			if hasattr(self.__obj__, name):
				return getattr(self.__obj__, name)
			return self.__dict__[name]
	 
		def __iter__(self):
			return self.__obj__.__iter__()
			
	l = []
	a = A(l)
	 
	for i in xrange(101): a.append(i)
	 
	print sum(a)

---

这是一个再简单不过的agent类，不过不怎么完美。因为\_\_iter\_\_属于预定义函数，不会调用\_\_getattr\_\_来获得。因此还需要额外定义。下面章节中，我们将看到一种简单的多的方法来实现agent类。

另外，提一点细节的差异。\_\_getattr\_\_，\_\_setattr\_\_相对还是比较上层的，至少在这两个函数中，可以访问\_\_dict\_\_。而\_\_getattribute\_\_这个函数中，使用self.\_\_dict\_\_会引发递归，需要用object.\_\_getattribute\_\_(self, name)。相对的，\_\_getattribute\_\_只能用于new style class。

同样，\_\_getattr\_\_，\_\_setattr\_\_，\_\_getattribute\_\_的用法不止于此。通过定义这三个函数，可以对类的成员做出非常多的变化。但是，和下面提到的手段比起来，这无疑是比较初级的。

## 函数赋值 ##

我们看这个从socket.py中摘出来的例子：

	_delegate_methods = ("recv", "recvfrom", "recv_into", "recvfrom_into",
	                     "send", "sendto")

    def __init__(self, family=AF_INET, type=SOCK_STREAM, proto=0, _sock=None):
        if _sock is None:
            _sock = _realsocket(family, type, proto)
        self._sock = _sock
        for method in _delegate_methods:
            setattr(self, method, getattr(_sock, method))

当你调用s.recv(4)的时候，你以为自己在调用_socketobject的方法？错了，那方法其实是对应的\_realsocket的。这是替换实例函数的例子。

---

这可以做什么用？我们来看我写的一个http代理装饰器。

    def http_proxy(proxyaddr, username=None, password=None):
        def reciver(func):
            def creator(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
                sock = func(family, type, proto)
                sock.connect(proxyaddr)
                def newconn(addr): http_connect(sock, addr, username, password)
                sock.connect, sock.connect_ex = newconn, newconn
                return sock
            return creator
        return reciver

我们再看descriptor里面的这个例子：

---

	class A(object):
	 
		def b(self):
			print 'ok'
	 
	a = A()
	print A.b, a.b
	<unbound method A.b> <bound method A.b of <__main__.A object at 0x7f81620d9990>>
	print a.b.im_self == a, a.b.im_func == A.b.im_func
	True True
	print A.__dict__['b'], A.b.im_func
	<function b at 0x7f81620db500> <function b at 0x7f81620db500>

	def c(self): print 'not ok'
	A.b = c

	print A.b, a.b
	<unbound method A.c> <bound method A.c of <__main__.A object at 0x7f81620d9990>>
	print a.b.im_self == a, a.b.im_func == A.b.im_func
	True True
	print A.__dict__['b'], A.b.im_func
	<function c at 0x7f81620db488> <function c at 0x7f81620db488>

	a.b()
	not ok

这同样是函数替换，不过替换的是类函数方法。

## descriptor ##

所谓descriptor，就是带有\_\_get\_\_和\_\_set\_\_函数的对象。当访问某个对象的某个属性，这个属性又是一个descriptor时。返回值是descriptor的\_\_get\_\_调用的返回，set同理类推。带有\_\_set\_\_的称为data descriptor，只有\_\_get\_\_的称为non data descriptor。

python访问某个对象的某个属性时，是按照以下次序的：

1. class的data descriptor。
2. instance属性，无论其是否是descriptor，不调用\_\_get\_\_。
3. class属性，包括non data descriptor。

使用descriptor，可以很容易的定义a.name之类获得值和设定的操作中需要执行什么。

实际上，我们使用的类函数就是基于descriptor做的。

---

	class A(object):
	 
		def b(self):
			print 'ok'
	 
	a = A()
	print A.b, a.b
	print a.b.im\_self == a, a.b.im\_func == A.b.im\_func
	print A.__dict__['b'], A.b
	<function b at 0x7f81620db500> <unbound method A.b>

最后一个A.\_\_dict\_\_['b'], A.b，揭示了一个问题，两者不一致。至于为什么？那是因为descriptor在起作用，在A.b的时候，调用了某个\_\_get\_\_，将函数和类组合成和method对象丢了出来。这个\_\_get\_\_在哪里呢？我们来看这么个例子。

---

	def f(self): print self['a'], 'ok'

	print dir(f)
	['__call__', '__class__', '__closure__', '__code__', '__defaults__', '__delattr__', '__dict__', '__doc__', '__format__', '__get__', '__getattribute__', '__globals__', '__hash__', '__init__', '__module__', '__name__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'func_closure', 'func_code', 'func_defaults', 'func_dict', 'func_doc', 'func_globals', 'func_name']	
	f({'a': 1})
	1 ok
	 
	o = {'a': 1}
	m = f.__get__(o, dict)
	print m
	<bound method dict.f of {'a': 1}>
	m()
	1 ok

这可说的不能再明白了，function对象本身就具备\_\_get\_\_，是non data descriptor。按照上述的规则，排在instance之后。所以，我们给instance加载属性，可以重载掉类的函数。

我们看下面这个例子，这同样是从本公司的业务系统中摘出来简化的。

---

	class Meta(type):
		def __new__(cls, name, bases, attrs):
			for k, v in attrs.items():
				if hasattr(v, '__meta_init__'): v.__meta_init__(k)
			return type.__new__(cls, name, bases, attrs)
	 
	class AttrBase(object):
	 
		def __meta_init__(self, k): self.name = k
		def __get__(self, obj, cls): return obj[self.name]
		def __set__(self, obj, value): obj[self.name] = value
	 
	class Base(dict):
		__metaclass__ = Meta
	 
	class User(Base):
	 
		name = AttrBase()
	 
	b = User()
	b.name = 'shell'
	print b
	print b.name

注意到，当你访问b.name的时候，实际上是去访问了b['name']。这个过程不是通过User类重载\_\_getattr\_\_实现的，而是通过descriptor。另外，我们处理这个例子的时候，用到了元类。下面一节介绍一下元类。

## 元类 ##

我们先看这么一个例子：

	class Base(dict):
    	__metaclass__ = Meta
	    def output(self, o): print 'hello, %s' % o
	b = Base()
	b.output('world')

你认为输出是什么？

再加上下面的代码呢？

	class Meta(type):
	    def __new__(cls, name, bases, attrs):
	        output = attrs['output']
	        attrs['output'] = lambda self, x: output(self, 'python')
	        return type.__new__(cls, name, bases, attrs)

---

实际上，输出是hello, python。

---

为什么？我们要从type说起。在python中，出乎我们的意料，type不是一个函数，而是一个类。type的作用不仅仅可以显示某个对象属于哪个类，更重要的是，type可以动态的创建类。就像下面这样。

	A = type('A', (object,), {'b': 1})
	a = A()
	print A, a.b

我们稍加变化，可以变成这样的代码。没什么区别。

	def f(name, bases, attrs):
		attrs['c'] = 2
		return type(name, bases, attrs)

	A = f('A', (object,), {'b': 1})
	a = A()
	print A, a.b, a.c

最后，我们把代码变成这个样子。

	def f(name, bases, attrs):
		attrs['c'] = 2
		return type(name, bases, attrs)

	class A(object):
		__metaclass__ = f
		b = 1

	a = A()
	print A, a.b, a.c

\_\_metaclass\_\_实际上，就是指创建类A的时候，要用什么函数进行生成。

---

可是且慢，type并不是一个函数，而是一个类阿。其实我们不妨这么看，类本身，可以视作是一个构造函数。

	class A(object): pass
	def B(): return A()
	 
	a = A()
	b = B()
	print a, b

由两者创建出来的对象并没有什么本质区别。所以，以下两个东西，其实在使用上是等价的。

	class M(type):
		def __new__(cls, name, bases, attrs):
			attrs['c'] = 2
			return type.__new__(cls, name, bases, attrs)
	 
	def f(name, bases, attrs):
		attrs['c'] = 2
		return type(name, bases, attrs)
	 
	A = M('A', (object,), {'b': 1})
	a = A()
	print A, a.b, a.c

---

既然如此，我们当然可以在\_\_metaclass\_\_中，将f替换为M。

	class M(type):
		def __new__(cls, name, bases, attrs):
			attrs['c'] = 2
			return type.__new__(cls, name, bases, attrs)
	 
	class A(object):
		__metaclass__ = M
		b = 1
	 
	a = A()
	print A, a.b, a.c

---

这就是本文最上面的元类的来历。

我们甚至可以创建元类的元类。

	class M1(type):
		def __new__(cls, name, bases, attrs):
			def f(cls, name, bases, attrs):
				attrs['c'] = 2
				return type.__new__(cls, name, bases, attrs)
			attrs['__new__'] = f
			return type.__new__(cls, name, (type,), attrs)
	 
	class M2(object):
		__metaclass__ = M1
	 
	class A(object):
		__metaclass__ = M2
		b = 1
	 
	a = A()
	print A, a.b, a.c

---

当然，大家可能疑惑，为什么舍弃function，而使用元类。function固然简单，但是function是无法继承的。这里不仅仅指我们无法创建一个Meta的子类，扩充meta的行为。而且，使用function的类，一旦继承，其子类是不会管父类的\_\_metaclass\_\_定义的。

## eval ##

大家看看下面这个程序，谁能看出是干什么的？

	exec(compile(__import__('zlib').decompress(
	__import__('base64').b64decode('eJylU9Fq4zAQfPdX7FGKpOIqDZQ+BPIVfTlognDs\
	dSLOlowkN02/vru20jR3HIU7gbG0u5qZ1Ug3PxZjDIuddYvhlA7eFbYffEgQsIR4iiW8d3ZX\
	wq6K+PRYwh6TH1LRBt+Dj5CLhyodiqLBlmb1L9naDjmkVgXQONp0AD+g+0yUIIJQUEVo7VzD\
	I8A68+jd0yO62jcomV7Xvh8CxkgAOmDVSKXU36GPGdpfoFuvj8EmlEKImz9axjesJXMQhjRm\
	bsoYKZhcKN3gp4Cv2Vkr5Uktl5BacRuFUqRB0MewtCJKuIWgiiKg4Ri1GVCf+SjNwc1ZwOb5\
	jmnpd6GlxUzGkzPZRgqp75TYqM0VI68JVE1+jO5/HGl9gM46BOuu4jxsO6V0TFVIkRFl7ng1\
	OZmb1X2V6oPkUqX3wY9DlEv18rD9N/+m6/DFj8t9yQ4EvhpT6wfsBpkbHoJ1CcgdeF3qB2Cs\
	hA52J3imsk7/HNkj5teM6KoeJd1+XYX9K2lVv4G83I9boL7pNXyzr6BjMobjxsB6DcKYvrLO\
	GDELo8fU2ZhK4B10avP70vPvArVcbelgRjELaalwNpZdEPckngxqbJ1kxlOAXcTpNRbZLMa5\
	dpYivG9KQCunLvBtqFwzRgyS4vmVMdYqn2fxAdHyTCM=')),'', 'exec'))

---

看不出来是吧？那先看看这个例子：

	def remove_list(li, obj):
		lic = li[:]
		lic.remove(obj)
		return lic
	 
	ops = ["+", "-", "*", "/"]
	def gen_make(nums, *exes):
		if len(nums) == 0:
			try:
				if eval("".join(exes)) == 24: print "".join(exes).replace(".0", "")
			except: pass
		elif len(exes) == 0:
			for n in nums: gen_make(remove_list(nums, n), str(n) + ".0")
		else:
			if len(exes) > 1:
				exes = list(exes)
				exes.insert(0, '(')
				exes.append(')')
			for n in nums:
				for op in ops:
					gen_make(remove_list(nums, n), str(n) + ".0", op, *exes)
	 
	gen_make([3, 4, 6, 8])

---

这是我写的一个24点计算程序，相对有点取巧。核心是利用字符串拼装表达式，然后用eval看看是不是等于24。相对来说，不使用eval的代码就要复杂很多。当然，下面这个版本要完整很多。

	from itertools import combinations
	 
	class opt(object):
		def __init__(self, name, func, ex=True):
			self.name, self.func, self.exchangable = name, func, ex
		def __str__(self): return self.name
		def __call__(self, l, r): return self.func(l, r)
		def fmt(self, l, r):
			return '(%s %s %s)' % (fmt_exp(l), str(self), fmt_exp(r))
	 
	def eval_exp(e):
		if not isinstance(e, tuple): return e
		try: return e[0](eval_exp(e[1]), eval_exp(e[2]))
		except: return None
	 
	def fmt_exp(e): return e[0].fmt(e[1], e[2]) if isinstance(e, tuple) else str(e)
	def print_exp(e): print fmt_exp(e), eval_exp(e)

---
	 
	def chkexp(target):
		def do_exp(e):
			if abs(eval_exp(e) - target) < 0.001: print fmt_exp(e), '=', target
		return do_exp

	def iter_all_exp(f, ops, ns, e=None):
		if not ns: return f(e)
		for r in set(ns):
			ns.remove(r)
			if e is None: iter_all_exp(f, ops, ns, r)
			else:
				for op in ops:
					iter_all_exp(f, ops, ns, (op, e, r))
					if not op.exchangable:
						iter_all_exp(f, ops, ns, (op, r, e))
			ns.append(r)
	 
	opts = [
		opt('+', lambda x, y: x+y),
		opt('-', lambda x, y: x-y, False),
		opt('*', lambda x, y: x*y),
		opt('/', lambda x, y: float(x)/y, False),]
	 
	if __name__ == '__main__':
		iter_all_exp(chkexp(24), opts, [3, 4, 6, 8])

---

回到最上面的那个表达式，那是一个程序被zip后base64的结果。当然，这个结果字符串被写入一个程序中，程序会自动解开内容进行eval。这种方法能够将任何代码变为一行流。而这个被变换的程序，就是实现这个功能的。

## 语法合成转换 ##

语法转换的最著名例子是orm，为什么？orm实际上，将python语法转换成了sql语法。

## 慎用元类 ##

正派人士为什么畏惧黑魔法？因为元编程会破坏直觉。

作为一个受到多年训练的程序员，你应当对你熟练使用的语言有一种直觉。看到dict(zip(title, data))就应当想到，这是一个拼接数据生成字典的代码。看到[(k, v) for k, v in d.iteritems() if k...]就应当知道，这是一个过滤算法。这是在长期使用程序后形成的一种条件反射。

而元编程会很大程度的破坏这种直觉。这也是为什么我很讨厌C++的算符重载的原因。你能够想像么？o = a + b;这个表达式，其实想表达的是两颗特定条件的树的拼和(concat)过程，而非合并(merge)过程。每次使用重载过的系统，我都需要重新训练我的直觉系统。

python的元编程具有同样可怕的效果。还记得eval中那个自压缩的例子么？那是一个极端，将人类可理解的程序编码为了人类无法理解的。而meta的那个例子说明，元编程可以在不知不觉中修改原始的定义。

python中的元编程手段远远不止上述这些，很多时候，我们自己都毫无感觉。甚至，要修改一个行为，不一定需要元编程，重载同样也可以让人摸不着头脑。但是由于元编程的复杂性，用户更难在其中进行源码阅读，跟踪，调试。

在设计，规划这类代码的时候，必须注意。首先，你的设计需要尽量符合直觉，尽量让使用者感到舒服。其次，你需要比常规程序更多的文档，尽量减少用户在阅读源码上的时间——除非你万分的有信心，用户能够毫无障碍的阅读你的源码。最后，你需要比较精细的测试，和更多的，更友好错误处理。因为一旦发生异常，用户可能无法处理不友好的抛出。

# ORM的意义和目标 #

## 为什么要用ORM ##

ORM的根本目的，是将关系型数据库模型转换为面对对象模型。此外，他还兼具了一些其他功能。例如：

* 跨数据库
* 对象缓存
* 延迟执行

## 对象缓存 ##

对象缓存的目的在于减少SQL的执行，增加程序执行速度，减少数据库开销。从某种意义来说，写的好的程序是不需要对象缓存的。但是这个“写的好”对程序设计提出了及其变态的要求。他要求无论程序由多少个组件组成，他们都必须能彼此传递数据，甚至知道对方的存在和细节，这样才能消除无效的查询和提交。但是这一要求使得代码之间产生了紧耦合，不利于系统的扩展。

## lazy evaluation ##

lazy evaluation，中文翻译为惰性求值。指的是表达式的执行被延缓到真正需要值的时候。在ORM中，lazy evaluation一般是指查询过程不发生在查询语句生成的时候，而发生在实际发生数据请求的时候。

两者的区别在于，非lazy evaluation需要一次性完成表达式拼装，因此其逻辑是集中式的，不利于模块化。而lazy evaluation则可以将表达式逻辑的拼装分散在各个系统中。这同样是从系统耦合性和扩展性上来的需求。

另一种的lazy evaluation则是，在请求数据的时候只返回数据的一部分，当枚举到后续部分时再继续请求数据。如果情况合适，这个技巧可以有效减少计算开销和网络负载，或者减小响应时间。但是返回片段过小，请求过于频繁，应用场景不正确，反而会降低效率。

# redis和RDBMS的区别 #

## ACID ##

ACID是RDBMS的四个基本特性，即：

* 原子性（Atomicity）：一个事务(transaction)中的所有操作，要么全部完成，要么全部不完成，不会结束在中间某个环节。
* 一致性（Consistency）：在事务开始之前和事务结束以后，数据库的完整性限制没有被破坏。
* 隔离性（Isolation，又称独立性）：当两个或者多个事务并发访问（此处访问指查询和修改的操作）数据库的同一数据时所表现出的相互关系。
* 持久性（Durability）：在事务完成以后，该事务对数据库所作的更改便持久地保存在数据库之中，并且是完全的。

redis的ACID：

* 原子性：redis本身是原子的，但是redis集群做不到原子性。redis只有一个线程（后台线程不处理实际业务），因此redis线性化处理每个指令。每个指令的处理都是不可打断的，原子化的。对于一系列指令，redis有pipeline。然而，如果使用kv将数据存储分布在多个节点上，那么实际上是无法保证多个节点同时成功或失败的。
* 一致性：一般而言，在单个节点上，只要写的不是太差，满足原子性的多数都满足一致性。但是当冗余数据或者数据约束跨越多节点时，很容易发生不一致。
* 隔离性：我们无法让redis满足隔离性，单节点也不行。
* 持久性：根据配置，redis可能满足持久性。如果打开aof模式，redis的性能会大幅下降，但是此时满足持久性。如果使用dump模式或者干脆用Replication替代，那么显然不满足持久性。

## ACID不完整造成的问题 ##

* redis不支持隔离性，实际上普通数据库中涉及隔离性往往也很晕很绕。因此如果你打算设计一个ORM来完成隔离性，我建议你更换数据库。

	在redis中解决这个问题的唯一方法是引入对象锁，包括全局锁，表锁，或者行级锁。但是这太重了。

* 如果你的所有查询和写入都不冗余，也没有跨越多个对象的约束，那么多节点不会破坏一致性。

	例如，你在user中保存了用户的权限信息。在session中，为了加速访问，你复制了这一信息。那么，user和session中的数据构成冗余。当某个session的user和他不在同一个节点中的时候，我们无法通过pipeline保证对两者的操作同时完成或者同时失败。所以，可能会破坏一致性。
	又例如，你需要限制只能有10个user具备管理员权限。这些user可能分布在多个不同的节点上，同样，我们也无法保证操作时一定不会破坏这个约束。
	WAL（预写式日志Write-Ahead Logging）可以有效的解决这个问题，但是在redis这种轻量级业务系统上使用WAL怎么看都太重了。
	当然，你可能觉得这没什么大不了。那是因为在这个例子中，两个数据有主次关系，即使一致性被破坏也无所谓。

* redis中没有关系，因此你需要重新设计关系系统。然而双边关系系统会造成冗余数据，引发一致性问题。

	例如：我们的user对象有parent和children两个属性，是一个自身的一对多关系。有两个对象，user1和user2，刚好分别分布在node1和node2两个节点上。那么，user1和user2的关系建立过程需要同时修改node1和node2。如果不加以特殊的控制，很难保证node1和node2同步完成或失败。

* redis中没有索引系统，因此无法使用where子句，也做不到unique。不过可以通过一个额外的键追踪数据来做到这点。然而如果你自制了索引系统，那么形成了冗余数据。因此，使用索引会引发一致性问题。

	一个比较好的解决方法是（我没实验过），在服务器端，利用lua来写一些过程，负责数据的查询。

# redisobj #

## redisobj的对象框架 ##

大家应该猜到了，在基于redis的ORM中，我们主要需要使用元类和descriptor两种元编程方法。下面是使用时的样例代码：

	class User(redisobj.Base):
		username = redisobj.String()
		password = redisobj.String()
		priv = redisobj.Integer()
		domain = redisobj.ForeignKey('Domain')
	 
	class Domain(redisobj.Base):
		name = redisobj.String()
	 
	class UserGroup(redisobj.Base):
		name = redisobj.String()

---

	def run(c):
		d1 = Domain(name='domain0')
		c.save(d1)
	 
		u1 = User(username='user1', priv=1, domain=d1)
		u2 = User(username='user2', priv=1, domain=d1)
		ug1 = UserGroup(name='usergroup1')
		ug2 = UserGroup(name='usergroup2')
		c.save(u1, u2, ug1, ug2)
	 
		c.flush()
		u3 = c.load_by_id(User, 1)
		print u3.copy()
	 
		u3.priv = 2
		u3.password = 'abc'
		del u3.username
		c.save(u3)
		c.flush()
		u4 = c.load_by_id(User, 1)
		print u4.copy()
	 
		c.delete(u2)
		try: c.load_by_id(User, 2)
		except LookupError: print 'yes, User1 disappeared.'
		print c.list(User)

---

我们分析一下上述代码。User，Domain，UserGroup三者，都是继承自redisobj.Base，而这个类，则是由元类创建的。因此，元类Meta可以轻易的替换其中的属性。我将所有继承自AttrBase的全部归并到一起。具体的DataType，例如Integer，String，都是派生自这个类。于是，Base的所有继承者，都可以用Class.\_\_attrs\_\_访问属性列表。而使用instance.prarmeter_name的时候，descriptor发生作用，读取Base中的具体数据。这大概构成了redisobj的对象框架。

## redisobj的Manager ##

manager是整个redisobj的核心，所有的保存，加载，都直接和manager打交道。当然，一种更加好看的方法是将manager全局化，然后在Base中添加方法（相应的，子类中需要添加类方法）来进行save/delete等行为。然而这将manager限定为全局只有一个（包括集群）。实际中碰到的很多例子，一个程序需要处理超过一个的redis（或者redis集群）。因此，我们在设计的时候保持了manager和object分离的设计思路。

## 不完整的ForeignKey ##

ForeignKey是所有数据类型中最特殊的一个，因为它重载了预定的descriptor。在我们的数据字典中，他和Integer没有区别（在关系上，ForeignKey也是Integer的一个子类）。然而，由于重载\_\_get\_\_和\_\_set\_\_。因此你可以认为obj.fk是一个对象。

注意，这里为什么重载descriptor，而不是直接将对象load入数字字典。因此被load入的对象也可能具备引用。反复引用之下，我们直接load对象的行为可能引发整个数据库被load入缓存的风险。而通过descriptor，我们可以在需要的时候载入对象，从而实现lazy evaluation。

但是这是不完整的行为！注意到redisobj里面只有FK，从来没有说反向引用，关系之类的说法。也就是说，当你在一个对象中保存另一个对象，可没有反向引用自动生成，当然也没有办法找到到底有多少个对象引用了当前对象。诚然，你可以自己做反向引用，然后自行添加。然而其中的不一致性问题需要自行解决。
