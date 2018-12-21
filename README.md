1.环境需求Python3.6.5、mysql5.7、nginx(可选)。系统版本推荐centos7 64位
2.环境搭建
  python3.6.5参考 http://blog.51cto.com/wenguonideshou/2083301，软链地址有问题，注意看回复
  mysql5.7安装，参考https://blog.csdn.net/qq_38663729/article/details/79327305
  python-dev安装，参考https://blog.csdn.net/default7/article/details/73368665
  安装程序依赖，进入程序目录，输入：pip3 install -r requirements.txt
3.程序安装
  修改silumz下settings.py文件中数据库的配置
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'xxxx',
          'USER': 'root',
          'PASSWORD': 'xxxx',
          'HOST': '127.0.0.1',
          'PORT': '3306',
      }
  }
  创建相应数据库，导入程序目录下的sql文件
  修改nginx配置文件（centos7  /etc/nginx/nginx.conf）
  配置文件的server中的location字段如下修改
  location / {
            proxy_pass   http://127.0.0.1:8000;
            index  index.html index.htm;
        }
  重启nginx，访问网站即可
4.修改爬虫中的数据库地址
  db = pymysql.connect("127.0.0.1", "root", "xxxx", "xxxx")
5.启动程序
  进入程序目录，uwsgi --ini uwsgi.ini
6.模板修改
  修改silumz下settings文件中的模板配置
  TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'+"/"+"94imm")]
  94imm为模板名
  模板文件位于templates文件夹下，修改相应页面
7.其他配置
  将程序目录下的pagination.html文件放入python安装目录的/site-packages/dj_pagination/templates/pagination/下
  （centos7  /usr/lib/python3.6/site-packages/dj_pagination/templates/pagination）
8.备注说明
  其他系统请自行百度mysql python3.6.5 nginx的安装方法，程序安装方法相同