# 安装 #

## windows ##

去[python.org](http://python.org/getit)下载对应的安装包。注意：

* python.org，不是com！！！
* gitit，不要download，会被墙

最后，注意一点。python在windows下有相当多的兼容问题，例如编码（混帐windows）。

## deb ##

    aptitude install python

## rpm ##

我也不知道，大概是`yum install python`。

## mac ##

自带。

## python shell ##

* python
* ipython
* bpython
* DreamPie

## IDE ##

* ulipad
* pydev
* emacs

# program #

## hello, world ##

	print 'hello, world'

## varable ##

	a = 1
	b = '2'
	c = a + b # BooBoo, error
	c = str(a) + b
	d = '12'
	id(c) == id(d) # True

## control ##

	if a < b:
		do somethin
	for i in range(10):
		print i
	while True:
		died loop
	with the_people_you_love():
		die

## function ##

	def mul(a, b):
		return a * b
	def mulmul(*p):
		s = 1
		for i in p: s = mul(s, i)
		return s
	def yamm(*p):
		return reduce(mul, p)

	def f(a, b, c):
		return a + c
	f(1, None, 2)
	f(1, c=2, b=0)
	def g(a, b=0, c=0):
		return a + c
	f(1)
	f(1, c=2)

## class ##

	class A(object):
		b = 1
		def __init__(self):
			self.c = 2
	a = A()

注意a.b和a.c的区别。

## yield ##

	for i in fib(n): print i
	 
	def fib1(n):
		a, b, r = 1, 0, []
		for i in xrange(n):
			a, b = a+b, a
			r.appand(a)
		return r
	 
	def fib2(n):
		a, b = 1, 0
		for i in xrange(n):
			a, b = a+b, a
			yield a
	 
	def fib3(n):
		def inner(i, a, b):
			if i == n: return None, None
			return lambda : inner(i+1, a+b, a), a+b
		return inner(1, 1, 0)
	 
	l, a = fib3(10)
	while l:
		print a
		l, a = l()

# package management #

## pip ##

	pip install virtualenv
	pip install -r requirements.txt

## virtualenv ##

	virtualenv env

## 常用包 ##

* chardet
* numpy
* scipy
* sympy
* matplotlib
* pygments
* virtualenv
* mako
* sqlalchemy
* gevent
* Scapy
* pyzmq
* twisted
* werkzeug
* celery
* beautifulsoap
* lxml
* pyqt
* pyside
* pygame
* PIL

# web deploy #

## nginx ##

	location /static {
			 index  index.html index.htm;
			 gzip   on;
	}
	 
	location ~ ^/(api|sys)/ {
			 include        uwsgi_params;
			 uwsgi_pass     unix:/run/uwsgi/app/app1/socket;
	}

## apache ##

	<Location />
    	SetHandler uwsgi-handler
	    uWSGISocket 127.0.0.1:3031
	</Location>

## uwsgi ##

	[uwsgi]
	uid             = web
	gid             = web
	chmod-socket    = 666
	 
	plugins         = python
	workers         = 1
	reload-on-as    = 196
	touch-reload    = /home/web/app1/RELEASE
	chdir           = /home/web/app1
	pythonpath      = /usr
	module          = main

## web.py ##

	app = web.application(urls)
	 
	if web.config.get('sesssion') is None:
		web.config.session = web.session.Session(
			app, web.session.DBStore(web.config.db, 'sessions'))
	 
	if __name__ == '__main__':
		if len(sys.argv) > 1:
			cmd = sys.argv.pop(1)
			if cmd == 'profile':
				app.run(web.profiler)
			elif cmd == 'test':
				from test import tester
				tester.testall(app)
		else: app.run()
	else: application = app.wsgifunc()

## django ##

	uwsgi --chdir=/path/to/your/project \
		--module=mysite.wsgi:application \
		--env DJANGO_SETTINGS_MODULE=mysite.settings \
		--master --pidfile=/tmp/project-master.pid \
		--socket=127.0.0.1:49152 \      # can also be a file
		--processes=5 \                 # number of worker processes
		--uid=1000 --gid=2000 \         # if root, uwsgi can drop privileges
		--harakiri=20 \                 # respawn processes taking more than 20 seconds
		--limit-as=128 \                # limit the project to 128 MB
		--max-requests=5000 \           # respawn processes after serving 5000 requests
		--vacuum \                      # clear environment on exit
		--home=/path/to/virtual/env \   # optional path to a virtualenv
		--daemonize=/var/log/uwsgi/yourproject.log      # background the process

## dispatcher ##

* Quixote

* django

	urlpatterns = patterns('',
		# Examples:
		# url(r'^$', '{{ project_name }}.views.home', name='home'),
		# url(r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),
	 
		# Uncomment the admin/doc line below to enable admin documentation:
		# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	 
		# Uncomment the next line to enable the admin:
		url(r'^admin/', include(admin.site.urls)),
	)

* web.py

	urls = (
		'/openid/', 'actions.webgid.host',
		'/ticket/', 'actions.ticket.ticket',
		'/timezone/', 'actions.timezone.timezone',
		'/segment/', 'actions.segtxt.segtxt',
		'/txtimg', txtimg.app,
		'/pycode', pycode.app,
	)

* bottle

	from bottle import route, run, template
	 
	@route('/hello/:name')
	def index(name='World'):
		return template('<b>Hello {{name}}</b>!', name=name)
	 
	run(host='localhost', port=8080)

* flask

	from flask import Flask
	app = Flask(__name__)
	 
	@app.route("/")
	def hello():
		return "Hello World!"
	 
	if __name__ == "__main__":
		app.run()

## ORM ##

ORM有用么？

## template ##

* mako

	<%inherit file="base.html"/>
	<%
		rows = [[v for v in range(0,10)] for row in range(0,10)]
	%>
	<table>
		% for row in rows:
			${makerow(row)}
		% endfor
	</table>
	 
	<%def name="makerow(row)">
		<tr>
		% for name in row:
			<td>${name}</td>\
		% endfor
		</tr>
	</%def>

	from mako.template import Template
	print Template("hello ${data}!").render(data="world")

* jinja2

{% raw %}
	{% extends "layout.html" %}
	{% block body %}
	  <ul>
	  {% for user in users %}
		<li><a href="{{ user.url }}">{{ user.username }}</a></li>
	  {% endfor %}
	  </ul>
	{% endblock %}
	 
	from jinja2 import Template
	template = Template(...)
	template.render(name='John Doe')
{% endraw %}

## session ##
