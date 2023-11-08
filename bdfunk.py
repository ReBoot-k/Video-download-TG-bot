import sqlite3 as sq
import random
from datetime import datetime
import time


class DataBase:

    def __init__(self, database_file):
        self.connection = sq.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_for_presence_in_the_list(self, id_):
        self.cursor.execute('SELECT free_work FROM user WHERE id_telegram = ?', (id_, ))
        result = self.cursor.fetchall()

        if len(result) == 0:
            return False
        else:
            return True

    def check_for_user_in_the_list(self, name):
        self.cursor.execute('''SELECT id_telegram FROM user WHERE user_name = ?''', (name, ))
        result = self.cursor.fetchall()

        if len(result) == 0:
            return False
        else:
            return True

    def get_subscription(self, id_):
        self.cursor.execute('''SELECT subscription FROM user WHERE id_telegram = ?''', (id_,))
        result = self.cursor.fetchall()
        if len(result) == 0:
            return False
        return result[0][0]

    def get_free_update_time(self, id_):
        self.cursor.execute('''SELECT free_update_time FROM user WHERE id_telegram = ?''', (id_,))
        result = self.cursor.fetchall()
        if len(result) == 0:
            return False
        return result[0][0]

    def get_username(self, id):
        self.cursor.execute('''SELECT user_name FROM user WHERE id_telegram = ?''', (id, ))
        result = self.cursor.fetchall()
        return result[0][0]

    def update_date(self, id):
        today = datetime.today()
        self.cursor.execute('''UPDATE user SET free_update_time = ? WHERE id_telegram = ?''', (today.strftime("%Y/%m/%d"), id))
        self.connection.commit()
        self.add_work_limit(id, 5)

    def get_id_by_username(self, name):
        self.cursor.execute('''SELECT id_telegram FROM user WHERE user_name = ?''', (name, ))
        result = self.cursor.fetchall()
        return result[0][0]

    def work_limit(self, id):
        self.cursor.execute('''SELECT free_work FROM user WHERE id_telegram = ?''', (id, ))
        result = self.cursor.fetchall()
        return result[0][0]

    def get_channel_list(self):
        self.cursor.execute('''SELECT * FROM tg_channels''')
        result = self.cursor.fetchall()
        return result

    def need_update_limit(self, id):
        limit = self.get_free_update_time(id)
        limit = [int(i) for i in limit.split('/')]

        now = datetime.now()
        then = datetime(*limit)

        delta = now - then

        return int(delta.days) > 0

    def get_statistic(self):
        user_id_list = self.get_all_user_id()
        user_id_sub = 0
        for user_id in user_id_list:
            if self.user_have_sub(user_id):
                user_id_sub += 1

        return {
            'all_user_len': str(len(user_id_list)),
            'all_user_sub': str(user_id_sub)
        }

    def get_all_user_id(self):
        self.cursor.execute('''SELECT id_telegram FROM user''')
        result = self.cursor.fetchall()
        result = [user_id[0] for user_id in result]
        return result

    def user_have_sub(self, id):
        user_sub = self.get_subscription(id)
        if user_sub is None:
            return False
        elif int(time.time()) < user_sub:
            return True
        else:
            return False

    def add_work_limit(self, id, count):
        self.cursor.execute('''UPDATE user SET free_work = ? WHERE id_telegram = ?''', (count, id))
        self.connection.commit()

    def del_channel(self, channel_id):
        self.cursor.execute('''DELETE FROM tg_channels WHERE channels_id = ?''', (channel_id,))
        self.connection.commit()

    def use_work(self, id):
        work = int(self.work_limit(id)) - 1
        self.cursor.execute('''UPDATE user SET free_work = ? WHERE id_telegram = ?''', (work, id))
        self.connection.commit()

    def subscribe_user(self, id, sub_time):
        self.cursor.execute('''UPDATE user SET subscription = ? WHERE id_telegram = ?''', (sub_time, id))
        self.connection.commit()

    def unsubscribe_user(self, id):
        self.cursor.execute('''UPDATE user SET subscription = null WHERE id_telegram = ?''', (id,))
        self.connection.commit()

    def get_user_id_by_order_id(self, order_id):
        self.cursor.execute('''SELECT id_user FROM order_foto WHERE order_id = ?''', (order_id,))
        result = self.cursor.fetchall()
        return result[0][0]

    def add_channel_tg(self, channel_id, channel_link):
        self.cursor.execute(
            '''INSERT INTO tg_channels(channels_id, channels_link) VALUES(?, ?)''',
            (channel_id, channel_link)
        )
        self.connection.commit()

    def add_guests(self, id, name):
        self.cursor.execute('''INSERT INTO user(id_telegram, user_name) VALUES(?, ?)''', (id, name))
        self.connection.commit()

    def close(self):
        self.connection.close()

