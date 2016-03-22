reviewboard部署文档
-----------------------

## 生产环境

nginx + uwsgi

/etc/nginx/sites-available/myview 例子

```
upstream myview {
    server unix:///var/www/myview/myview.sock;
}

server {
    listen      80;
    server_name myview.isoft-linux.org;
    charset     utf-8;

    client_max_body_size 75M;

    location /media  {
        alias /var/www/myview/htdocs/media;
    }

    location /static {
        alias /var/www/myview/htdocs/static;
    }

    location / {
        uwsgi_pass  myview;
        include     uwsgi_params;
    }
}
```

调整 /var/www/myview 目录结构

```
touch /var/www/myview/htdocs/__init__.py 
ln -s /var/www/myview/htdocs/reviewboard.wsgi /var/www/myview/htdocs/wsgi.py 
mkdir /var/www/myview/htdocs/media 
mkdir /var/www/myview/htdocs/static
```

/etc/uwsgi/myview.ini 例子

```
[uwsgi]

chdir           = /var/www/myview
module          = htdocs.wsgi
chown-socket    = http:http
uid             = http
gid             = http
master          = true
processes       = 10
socket          = /var/www/myview/myview.sock
vacuum          = true
```
