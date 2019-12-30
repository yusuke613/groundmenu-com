#Flask関連のモジュール
from flask import render_template, session, redirect, url_for, flash, request, jsonify

#__init__.pyから設定情報を引き継ぐ
from flaskr import app
from flaskr import db

#modelの読み込み
from flaskr.models import Store, Staff, Menu, Table, Order

#関数群ファイルの読み込み
from flaskr import FlaskAPI

# このファイルで必要なモジュール
from sqlalchemy.orm.exc import NoResultFound
import os
# websocketに関するモジュール
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect, send

#sqlalchemyでfuncを使う(maxやminなどが使えるようになる)
from sqlalchemy import func

#会員情報を登録
@app.route('/create_account', methods = ['POST'])
def create_account():
    #エラーのセッションなどを持っている可能性があるので、クリアしている
    session.clear()
    e_mail = request.form['e_mail']
    password = FlaskAPI.hash_password(request.form['password'])
    # メールアドレスとパスワードが両方ある場合既に登録されているので、.one()がエラーを吐きexceptに飛ぶ。(.first()だとエラーにならないので注意)
    try:
        double_create_check = db.session.query(Staff).filter(Staff.E_MAIL==e_mail, Staff.PASSWORD!="").one()
        print(double_create_check.E_MAIL + "は既に存在しています")
        session['error'] = "そのメールアドレスは使用できません"
        return render_template('login.html')
    except NoResultFound as ex:
        print(ex)
# メールアドレスは存在するが、パスワードが存在しない場合、招待されているので、tryで処理する。(STAFF_CLASSは招待時に付与される想定)
        try:
            staff = db.session.query(Staff).filter(Staff.E_MAIL==e_mail, Staff.PASSWORD=="").one()
            staff.update({PASSWORD: password})
            db.session.commit()
            db.session.close()
            # 今の所、招待機能は追加していないので、エラーに飛ぶようにしている
            return render_template('error_1.html')
# 上記2パターン以外の場合、純粋な新規登録なので下記で処理
        except:
            db.session.add(Staff(E_MAIL=e_mail, PASSWORD=password, STAFF_CLASS_ID=1, STAFF_CLASS="Representative")) #代表者として登録。その際のIDは1とする。
            store_create=db.session.query(Staff).filter(Staff.E_MAIL==e_mail).one() #登録した代表者のレコードを抽出
            store_create.STORE_ID = store_create.STAFF_ID
            store_id=store_create.STAFF_ID  #登録した代表者のSTAFF_IDを取得
            db.session.add(Store(STORE_ID=store_id))    #代表者が登録された場合、新しいお店としてstoresテーブルに登録
            db.session.commit()
            db.session.close()
        return redirect("/login")



# ログイン
@app.route("/login", methods = ['POST'])
def login():
    session.clear()     #エラーのセッションなどを持っている可能性があるので、クリアしている
    e_mail = request.form['e_mail']
    password = request.form['password']
# メールアドレスが合致しているかで、アカウントがあるかを確認
    try:
        login_user = db.session.query(Staff).filter(Staff.E_MAIL==e_mail).one()
        login_password = FlaskAPI.verify_password(login_user.PASSWORD, password)
        if login_password == True:
            #パスワードOKの処理
            session['loggin'] = True
            session['store_id'] = login_user.STORE_ID
            session['staff_id'] = login_user.STAFF_ID
            store_info = db.session.query(Store).filter(Store.STORE_ID==login_user.STORE_ID).one()
            session['store_name'] = store_info.STORE_NAME
            session['table_number'] = 0
            session['tables'] = store_info.TABLES
            username_session = login_user.STORE_ID#デバック用

            #bufへ店舗専用のディレクトリを作成する(初回ログインのみ)
            store_dir_path = app.config['BUF_DIR'] + "/" + str(login_user.STORE_ID)
            if (os.path.isdir(store_dir_path) == False):
                os.makedirs(store_dir_path)
                print("{} is CREATE".format(store_dir_path))

            return redirect('/')
        else:
            #パスワードNGの処理
            session['error'] = "メールアドレスもしくはパスワードが間違っています"
            return render_template('login.html')
    except:
        session['error'] = "メールアドレスもしくはパスワードが間違っています"   #この処理はアカウントが存在しない場合に起こるが、エラー文を変えるとリスクがあるので、パスワードエラーと同一の文章にしている
        return render_template('login.html')

# /に飛んだ時
@app.route('/')
def index():
    # sessionに'login'がなければlogout処理
    login_check = FlaskAPI.login_check()
    # 店舗名が登録されてなければ、store_settingに飛ばす
    try:
        store_id = session['store_id']
        store_name = db.session.query(Store.STORE_NAME).filter(Store.STORE_ID==store_id, Store.STORE_NAME != "", Store.TABLES != None).one()
        return render_template('index.html',store_name=store_name)
    except:
        return redirect('/store_setting')



# 店舗名登録
@app.route('/store_information_add', methods = ['POST', 'GET'])
def store_information_add():
    if request.method == 'POST':
        store_id = session['store_id'] #セッションで登録する店舗を確認する
        store_name = request.form['store_name']
        tables = request.form['tables']
        try:
            store_information = db.session.query(Store).filter(Store.STORE_ID==store_id).one() #存在しない場合はログアウトの処理
            store_information.STORE_NAME = store_name
            store_information.TABLES = tables
            db.session.query(Table).filter(Table.STORE_ID==store_id).delete()
            for i in range(1,int(tables)+1):
                db.session.add(Table(STORE_ID=store_id, TABLE_NUMBER=i, TABLE_ACTIVATE="0"))
            db.session.commit()
            db.session.close()
            return redirect('/')
        except:
            return redirect('/logout')
    else:
        return "rendering 「/store_information_add」 error!"



# メニューリスト表示
@app.route('/show_menu' , methods = ['POST', 'GET'])
def show_menu():
    if 'store_id' not in session:
        return redirect("/logtout")
    else:
        store_id = session['store_id']
        class_2 = db.session.query(Menu.CLASS_1_ID, Menu.CLASS_2_ID, Menu.CLASS_2).filter(Menu.STORE_ID==store_id).\
            group_by(Menu.CLASS_1_ID, Menu.CLASS_2_ID, Menu.CLASS_2).\
            order_by(Menu.CLASS_2_ID).\
            all()
        print(class_2)
        class_3 = db.session.query(Menu.MENU_ID, Menu.CLASS_1_ID, Menu.CLASS_2_ID, Menu.CLASS_3_ID, Menu.CLASS_3, Menu.PRICE).filter(Menu.STORE_ID==store_id).\
            order_by(Menu.CLASS_3_ID).\
            all()
        print(class_3)
        return render_template('show_menu.html',class_2=class_2, class_3=class_3)



# メニュー登録
@app.route('/create_menu', methods = ['POST', 'GET'])
def create_menu():
    if request.method == 'POST':
        store_id = session['store_id']
        staff_id = session['staff_id']
        class_1 = request.form['class_1']
        class_2 = request.form['class_2']
        class_3 = request.form['class_3']
        price = request.form['price']
# 大分類の判定
        if class_1 == "food":
            class_1_id = 0
        else:
            class_1_id = 1

# 中分類が重複しているか判定し、IDを決定
        class_2_id_max = db.session.query(Menu.CLASS_2_ID).filter(Menu.STORE_ID==store_id, Menu.CLASS_1_ID==class_1_id).order_by(Menu.CLASS_2_ID.desc()).first()    #初めての中分類だった場合のCLASS_2_IDを取得するために必要な処理で、既存のCLASS_2_IDが何番まで振られているかを取得する(なければNoneが返り値)
        class_2_id_check = db.session.query(Menu.CLASS_2_ID).filter(Menu.STORE_ID==store_id, Menu.CLASS_1_ID==class_1_id, Menu.CLASS_2==class_2).first()    #登録内容と同一の中分類があれば、そのCLASS_2_IDを取得(なければNoneが返り値)
# 値がない場合は「None」を使う。その際の比較は「==」ではなく「is」のほうが良い
        if class_2_id_max is None and class_2_id_check is None:
            print("初めてのメニュー登録です")
            class_2_id = 1
            print("class_2_idは")
            print(class_2_id)
            print("です")
        elif class_2_id_check is None:
            print("同じ中分類はありませんでした")
            print("class_2_idは")
            class_2_id = class_2_id_max[0] +1
            print(class_2_id)
            print("です")
        else:
            print("同じ中分類がありました")
            class_2_id = class_2_id_check
            print("class_2_idは")
            print(class_2_id)
            print("です")
# 小分類のID決定
        class_3_id_max = db.session.query(Menu.CLASS_3_ID).filter(Menu.STORE_ID==store_id, Menu.CLASS_1_ID==class_1_id, Menu.CLASS_2_ID==class_2_id).order_by(Menu.CLASS_3_ID.desc()).first()
        class_3_id_check = db.session.query(Menu.CLASS_3_ID).filter(Menu.STORE_ID==store_id, Menu.CLASS_1_ID==class_1_id, Menu.CLASS_2_ID==class_2_id, Menu.CLASS_3==class_3).first()
        if class_3_id_max is None and class_3_id_check is None:
            print("初めての中分類のメニューです")
            class_3_id = 1
        elif class_3_id_check is None:
            print("同じメニューはありませんでした")
            class_3_id = class_3_id_max[0] +1
            print("class_3_idは")
            print(class_3_id)
            print("です")
        else:
            print("同じメニューがありました")
            return redirect('/show_menu')
        db.session.add(Menu(STORE_ID=store_id, STAFF_ID=staff_id, CLASS_1_ID=class_1_id, CLASS_1=class_1, CLASS_2_ID=class_2_id, CLASS_2=class_2, CLASS_3_ID=class_3_id, CLASS_3=class_3, PRICE=price))
        db.session.commit()
        db.session.close()
    return redirect("/show_menu")



# メニュー削除
@app.route('/delete_menu' , methods = ['POST', 'GET'])
def delete_menu():
    if request.method == 'POST':
        store_id = session['store_id']
        menu_ids = request.form.getlist("menu_id")
        print("消すmenu_idsは")
        print(menu_ids)
        print(len(menu_ids))
        try:
            for i in range(len(menu_ids)):
                db.session.query(Menu).filter(Menu.STORE_ID==store_id, Menu.MENU_ID==menu_ids[i]).delete()  #store_idでもフィルターをかける事により、他人のメニューを削除することを阻止
                db.session.commit()
                db.session.close()
            return redirect("/show_menu")
        except:
            return redirect("/logout")

    return redirect("/show_menu")


@app.route('/sort_menu' , methods = ['POST', 'GET'])
def sort_menu():
    if request.method == 'POST':
        store_id = session['store_id']
        staff_id = session['staff_id']
        class_2_sort_result_food = request.form.getlist("class_2_sort_result_food")     #CLASS_1_ID,CLASS_2_ID,CLASS_2の順番で並んだ文字列を受け取る
        class_2_sort_result_drink = request.form.getlist("class_2_sort_result_drink")   #CLASS_1_ID,CLASS_2_ID,CLASS_2の順番で並んだ文字列を受け取る
        class_3_sort_result = request.form.getlist("class_3_sort_result")               #MENU_ID,CLASS_1_ID,CLASS_2_ID,CLASS_3_IDの順番で並んだ文字列を受け取る

        try:
            #受け取った文字列からリストを作成
            class_3_sort_result_list = class_3_sort_result[0].split(",")
            #CLASS_3から書き換え。理由は、クラス2を先に書き換えるとメニューの追跡が煩雑になるから
            #CLASS_3_IDを一旦全て0にする
            class_3_ids = db.session.query(Menu)
            class_3_ids = db.session.query(Menu).filter(Menu.STORE_ID==store_id).update({Menu.CLASS_3_ID: 0})
            for i in range(0, len(class_3_sort_result_list), 4):
                class_3_change_menu_id = class_3_sort_result_list[i]
                class_3_change_class_1_id = class_3_sort_result_list[i+1]
                class_3_change_class_2_id = class_3_sort_result_list[i+2]
                class_3_change_record = db.session.query(Menu).filter(Menu.STORE_ID==store_id, Menu.MENU_ID==class_3_change_menu_id).one()  #store_idが合致していない場合は弾く

                class_3_change_class_3_id = db.session.query(Menu.CLASS_3_ID).filter(Menu.STORE_ID==store_id, Menu.CLASS_1_ID==class_3_change_class_1_id, Menu.CLASS_2_ID==class_3_change_class_2_id).order_by(Menu.CLASS_3_ID.desc()).first()
                class_3_change_record.CLASS_3_ID = class_3_change_class_3_id[0] + 1
                class_3_change_record.STAFF_ID = staff_id

            # foodかdrink片方だけ登録されている場合、ソートするとエラーが出るのをifで回避
            if(class_2_sort_result_food[0]!=""):
                #受け取った文字列からリストを作成
                class_2_sort_result_food_list = class_2_sort_result_food[0].split(",")
                # 一旦foodのCLASS_2_IDを0にする
                class_2_food_ids = db.session.query(Menu)
                class_2_food_ids = db.session.query(Menu).filter(Menu.STORE_ID==store_id, Menu.CLASS_1_ID==0).update({Menu.CLASS_2_ID: 0})
                #foodのCLASS_2_IDを書き換え(forが0から始まるのはlistが0から始まるから)
                for i in range(0, len(class_2_sort_result_food_list), 3):
                    class_2_id_change = db.session.query(Menu)
                    class_2_id_change = db.session.query(Menu).filter(Menu.STORE_ID==store_id, Menu.CLASS_1_ID==class_2_sort_result_food_list[i], Menu.CLASS_2==class_2_sort_result_food_list[i+2]).update({Menu.CLASS_2_ID: i/3+1})

            # foodかdrink片方だけ登録されている場合、ソートするとエラーが出るのをifで回避
            if(class_2_sort_result_drink[0]!=""):
                #受け取った文字列からリストを作成
                class_2_sort_result_drink_list = class_2_sort_result_drink[0].split(",")
                # 一旦drinkのCLASS_2_IDを0にする
                class_2_drink_ids = db.session.query(Menu)
                class_2_drink_ids = db.session.query(Menu).filter(Menu.STORE_ID==store_id, Menu.CLASS_1_ID==1).update({Menu.CLASS_2_ID: 0})
                #drinkのCLASS_2_IDを書き換え(forが0から始まるのはlistが0から始まるから)
                for i in range(0, len(class_2_sort_result_drink_list), 3):
                    class_2_id_change = db.session.query(Menu)
                    class_2_id_change = db.session.query(Menu).filter(Menu.STORE_ID==store_id, Menu.CLASS_1_ID==class_2_sort_result_drink_list[i], Menu.CLASS_2==class_2_sort_result_drink_list[i+2]).update({Menu.CLASS_2_ID: i/3+1})

            db.session.commit()
            db.session.close()

        except:
            return redirect("/logout")
    return redirect("/show_menu")

# テーブルのアクティベートと、注文メニューの表示
@app.route('/activate')
def activate():
    store_id = session['store_id']
    tables = db.session.query(Table.TABLE_NUMBER, Table.TABLE_ACTIVATE).filter(Table.STORE_ID == store_id).order_by(Table.TABLE_NUMBER).all()
    print(tables)
    return render_template('activate.html', tables=tables)


@app.route('/activate_json', methods = ['POST'])
def activate_json():
    try:
        store_id = session['store_id']
        table_status = request.get_json()
        table_number = table_status["table_number"]
        activate_status = table_status["activate_status"]
        db.session.query(Table).filter(Table.STORE_ID==store_id, Table.TABLE_NUMBER==table_number).update({Table.TABLE_ACTIVATE: activate_status})
        db.session.commit()
        db.session.close()
        result="true"
        return result
    except:
        result="false"
        return result

@app.route('/store_setting')
def store_setting():
    if 'store_id' not in session:
        return redirect('/logout')
    else:
        try:
            store_id = session['store_id']
            store_name = db.session.query(Store.STORE_NAME, Store.TABLES).filter(Store.STORE_ID==store_id, Store.STORE_NAME !="").one()
            return render_template('store_setting.html',store_name=store_name)
        except:
            return render_template('store_setting.html', store_name="")

@app.route("/logout")
def logout():
    # session['logged_in'] = False
    session.clear()
    return render_template('login.html')


# QRコードから復元する際のテスト
@app.route("/test/<int:store_id>/<int:table_number>")
def test(store_id,table_number):
    print(store_id)
    print(table_number)
    session.clear()
    session['store_id'] = store_id
    session['table_number'] = table_number
    return redirect("/order")
# ここまで

