#__init__.pyから設定情報を引き継ぐ
from flaskr import app

#パスワードハッシュ関連
from werkzeug.security import generate_password_hash, check_password_hash

#QRコード関連
import qrcode as qr
from PIL import Image, ImageDraw, ImageFont

# メニュー操作関連(秋吉使用)
from flask import session
from flaskr.models import Store, Staff, Menu, Table, Order
from flask_sqlalchemy import SQLAlchemy
from flaskr import db
from sqlalchemy import func


#ハッシュパスワードを作成する関数
def hash_password(original_pass):
    return generate_password_hash(original_pass)

#ハッシュパスワードと元のパスワードを比較する関数
def verify_password(hash_pass, original_pass):
    return check_password_hash(hash_pass, original_pass)

def login_check():
    if 'login' not in session:
        return
    else:
        return redirect('/logout')

# 商品数を求める関数、oder_statusの値によって、カートの中身や、注文済み、決済済みなどの値を求められる
def total_quantity(store_id, table_number, group_id, order_status):
    total_quantity = db.session.query(func.sum(Order.ORDER_QUANTITY)).\
        filter_by(STORE_ID=store_id, TABLE_NUMBER=table_number, GROUP_ID=group_id, ORDER_STATUS=order_status).\
        scalar()

    # 該当情報が1つもない場合、返り値がNoneになるので、その場合は0を代入する
    if total_quantity is None:
        total_quantity = 0

    return total_quantity

# テーブル単位の商品情報を求める関数、oder_statusの値によって、カートの中身や、注文済み、決済済みなどの値を求められる
def order_list(store_id, table_number, group_id, order_status):
    order_list = db.session.query(Order.ORDER_ID, Menu.CLASS_1, Menu.CLASS_2, Menu.CLASS_3, Menu.PRICE, Order.ORDER_QUANTITY).\
    join(Order, Order.MENU_ID==Menu.MENU_ID).\
    filter_by(STORE_ID=store_id, TABLE_NUMBER=table_number, GROUP_ID= group_id, ORDER_STATUS=order_status).\
    all()
    return order_list

# 単一の商品を求める関数
def order_item(store_id, table_number, group_id, order_status, menu_id):
    order_item = db.session.query(Order.ORDER_ID, Menu.CLASS_1, Menu.CLASS_2, Menu.CLASS_3, Menu.PRICE, Order.ORDER_QUANTITY).\
    join(Order, Order.MENU_ID==Menu.MENU_ID).\
    filter_by(STORE_ID=store_id, TABLE_NUMBER=table_number, GROUP_ID= group_id, ORDER_STATUS=order_status, MENU_ID=menu_id).\
    one()
    return order_item

def order_list_all(store_id, order_status):
    order_list = db.session.query(Order.ORDER_ID, Menu.CLASS_1, Menu.CLASS_2, Menu.CLASS_3, Order.ORDER_QUANTITY, Order.TABLE_NUMBER).\
    join(Order, Order.MENU_ID==Menu.MENU_ID).\
    filter_by(STORE_ID=store_id, ORDER_STATUS=order_status).\
    all()
    return order_list

# QRコードを生成する関数
# <T.B.D>QR付帯情報の検討，暗号化等

def qrmaker(code, store_id, store_name):

    qr_img = qr.QRCode(
    version=10,
    error_correction=qr.constants.ERROR_CORRECT_H,
    box_size=5,
    border=4    #デフォルト
    )
    #QRをコードから生成
    qr_img = qr.make(str(code))

    #リサイズ(250×250)
    width,height=250,250
    qr_img = qr_img.resize((width,height))

    #bufへimage保存
    qr_save_path = app.config['BUF_DIR'] +  "/" + str(store_id) + "/" + code + ".png"   #...buf/配下への保存
    qr_img.save(qr_save_path)

    #QRコードを加工
    qrfix(app.config['IMG_DIR'] + "/QR_base.png", qr_save_path, store_name)

    return qr_save_path

#   QRコード単体では簡素なので加工する関数
def qrfix(baseimg_path, qrimg_path, store_name):
    baseimg = Image.open(baseimg_path)
    qrimg = Image.open(qrimg_path)

    #背景画像の横幅の中心を取得
    w = ((baseimg.size[0] - qrimg.size[0]) / 2)
    #背景画像の縦幅の中心を取得し，さらに中心から4分の1に貼り付け
    h = ((baseimg.size[1] - qrimg.size[1]) / 8)

    #テキストの入力
    text_msg = store_name
    #文字を書きこむ為のオブジェクトが用意されているので取得する
    draw = ImageDraw.Draw(baseimg)

    #フォントを指定する
    font = ImageFont.truetype(app.config['FONTS_DIR'] + "/NotoSansCJKjp-Regular.otf", size=16)
    #テキストペースト位置の調整
    text_width = ((baseimg.size[0] - draw.textsize(text_msg, font)[0]) / 2)
    text_hight = baseimg.size[1] - ((baseimg.size[1] - draw.textsize(text_msg, font)[1]) / 2.5)

    #テキスト描画
    draw.text((text_width, text_hight), text_msg, font=font, fill=(255,255,255))   #   #xxxxxxとかでも指定可能

    #Baseを元にQRを埋め込む
    baseimg_backup = baseimg.copy()
    baseimg_backup.paste(qrimg, (int(w), int(h)))

    baseimg_backup.save(qrimg_path)
