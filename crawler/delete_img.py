import pymysql,os

dbhost={
        "host":"127.0.0.1",
        "dbname":"silumz",
        "user":"root",
        "password":"root"
    }


db = pymysql.connect(dbhost.get("host"), dbhost.get("user"), dbhost.get("password"), dbhost.get("dbname"))
cursor = db.cursor()

def del_page(id):
    cursor.execute("Delete FROM images_page WHERE id=" + "'" + id + "'")
    cursor.execute("SELECT imageurl FROM images_image WHERE pageid =" + "'" + id + "'")
    for img in cursor.fetchall():
        try:
            os.remove(img[0])
        except FileNotFoundError:
            pass
        except Exception as e:
            print("图片删除失败，错误信息：",e)
    cursor.execute("Delete FROM images_image WHERE pageid=" + "'" + id + "'")
    print("删除成功")
    try:
        os.system("sh ../restart.sh")
        print("缓存更新成功")
    except Exception as e:
        print("缓存更新失败，错误信息：",e)

if __name__=="__main__":
    print("请输入要删除的图集ID")
    id=input()
    del_page(id)