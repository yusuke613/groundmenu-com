#__init__.pyから設定情報を引き継ぐ
from flaskr import db

# このファイルでで必要なモジュール
from sqlalchemy import create_engine, Column, Integer, String, func

#テーブル定義
class Store(db.Model):
    __tablename__ = 'stores'

    STORE_ID = db.Column(Integer, primary_key=True) # ≒代表者のSTAFF_ID
    STORE_NAME = db.Column(String(255))
    TABLES = db.Column(Integer)

    def __repr__(self):
        return "(STORE_ID='%s', STORE_NAME='%s', TABLES='%s')" % (self.STORE_ID, self.STORE_NAME, self.TABLES)

class Staff(db.Model):
    __tablename__ = 'staffs'

    STAFF_ID = db.Column(Integer, primary_key=True)
    STORE_ID = db.Column(Integer)
    STAFF_NUMBER = db.Column(Integer)   #スタッフ順の並べ替えの際に必要
    STAFF_NAME = db.Column(String(255))
    E_MAIL = db.Column(String(255), unique=True)
    PASSWORD = db.Column(String(255))
    STAFF_CLASS_ID = db.Column(Integer)
    STAFF_CLASS = db.Column(String(32))

    def __repr__(self):
        return "(STAFF_ID='%s', STORE_ID='%s', STAFF_NUMBER='%s', STAFF_NAME='%s', , E_MAIL='%s', PASSWORD='%s', STAFF_CLASS_ID='%s',STAFF_CLASS='%s')" % (self.STAFF_ID, self.STORE_ID, self.STAFF_NUMBER, self.STAFF_NAME, self.E_MAIL, self.PASSWORD, self.STAFF_CLASS_ID, self.STAFF_CLASS)

#Class_Middleテーブル定義
class Menu(db.Model):
    __tablename__ = 'menus'

    MENU_ID = db.Column(Integer, primary_key=True)
    STORE_ID = db.Column(Integer)
    STAFF_ID = db.Column(Integer)   #登録・更新者を把握するのに必要
    CLASS_1_ID = db.Column(Integer) #大分類を示すクラス
    CLASS_1 = db.Column(String(5))
    CLASS_2_ID = db.Column(Integer)    #中分類を示すクラス
    CLASS_2 = db.Column(String(64))
    CLASS_3_ID = db.Column(Integer)    #小分類を示すクラス
    CLASS_3 = db.Column(String(64))
    PRICE = db.Column(Integer)

    def __repr__(self):
        return "(MENU_ID='%s', STORE_ID='%s', STAFF_ID='%s', CLASS_1_ID='%s', CLASS_1='%s', CLASS_2_ID='%s', CLASS_2='%s', CLASS_3_ID='%s', CLASS_3='%s', PRICE='%s')" % (self.MENU_ID, self.STORE_ID, self.STAFF_ID, self.CLASS_1_ID, self.CLASS_1, self.CLASS_2_ID, self.CLASS_2, self.CLASS_3_ID, self.CLASS_3, self.PRICE)

class Table(db.Model):
    __tablename__ = 'tables'

    TABLE_ID = db.Column(Integer, primary_key=True)
    STORE_ID = db.Column(Integer)
    TABLE_NUMBER = db.Column(Integer)
    TABLE_ACTIVATE = db.Column(Integer)

    def __repr__(self):
        return "(TABLE_ID='%s', STORE_ID='%s', TABLE_NUMBER='%s', TABLE_ACTIVATE='%s')" % (self.TABLE_ID, self.STORE_ID, self.TABLE_NUMBER, self.TABLE_ACTIVATE)

class Order(db.Model):
    __tablename__ = 'orders'

    ORDER_ID = db.Column(Integer, primary_key=True)
    ORDER_STATUS = db.Column(Integer)   #0はかごに入ってる,1はオーダーされた,2はかごから削除された,3は決済完了
    STORE_ID = db.Column(Integer)
    TABLE_NUMBER = db.Column(Integer)
    GROUP_ID = db.Column(Integer)   #オーダーをしたグループを特定
    MENU_ID = db.Column(Integer)
    ORDER_QUANTITY = db.Column(Integer)

    def __repr__(self):
        return "(ORDER_ID='%s', ORDER_STATUS='%s', STORE_ID='%s', TABLE_NUMBER='%s', GROUP_ID='%s', MENU_ID='%s', ORDER_QUANTITY='%s')" % (self.ORDER_ID, self.ORDER_STATUS, self.STORE_ID, self.TABLE_NUMBER, self.GROUP_ID, self.MENU_ID, self.ORDER_QUANTITY)

#DBの作成をここで行う。
db.create_all()




























