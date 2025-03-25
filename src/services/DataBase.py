import mysql.connector
from Api_token import ADMIN_ID

class DataBase:
  def __init__(self, bd_user, bd_password, bd_host, bd_database) -> None:
    self.bd_user = bd_user
    self.bd_password = bd_password
    self.bd_host = bd_host
    self.bd_database = bd_database
  
  async def execute_query(self, query, params=None, isNeedFetch=False):
    connect = mysql.connector.connect(user=self.bd_user, password=self.bd_password, host=self.bd_host, database=self.bd_database, charset="utf8mb4")
    cursor = connect.cursor()
    try:
      cursor.execute(query, params)
      result = None
      if isNeedFetch:
        result = cursor.fetchall()
      connect.commit()
    except mysql.connector.Error as error:
      print(f"Error: {error}")
      if connect.is_connected():
        connect.rollback()
      result = "Error"
    finally:
      cursor.close()
      connect.close()
      return result

class UserDatabase(DataBase):
  def __init__(self, bd_user, bd_password, bd_host, bd_database):
    super().__init__(bd_user, bd_password, bd_host, bd_database)
    self.table = "users"
  
  async def add_user(self, user_id, name):
    query = f"""INSERT IGNORE INTO {self.table} (user_id, name, role) VALUES (%s, %s, %s)"""
    params = [user_id, name, 'admin' if user_id == ADMIN_ID else "user"]
    return await self.execute_query(query, params)
  
  async def update_label(self, user_id, label):
    query = f"""UPDATE {self.table} SET label=(%s) WHERE user_id=(%s) ORDER BY id DESC LIMIT 1;"""
    params = [label, user_id]
    return await self.execute_query(query, params)
  
  async def update_payment_status(self, user_id):
    query = f"""UPDATE {self.table} SET pay_status=(%s) WHERE user_id=(%s) ORDER BY id DESC LIMIT 1;"""
    params = [True, user_id]
    return await self.execute_query(query, params)
  
  async def update_payment_count(self, user_id):
    query = f"""UPDATE {self.table} SET pay_count=pay_count + 1 WHERE user_id = (%s) ORDER BY id DESC LIMIT 1;"""
    params = [user_id]
    await self.execute_query(query, params)
    query = f"""SELECT pay_count FROM {self.table} WHERE user_id=(%s);"""
    params = [user_id]
    return await self.execute_query(query, params, True)
  
  async def update_total_amount(self, user_id, amount):
    query = f"""UPDATE {self.table} SET total_amount=total_amount + (%s) WHERE user_id = (%s) ORDER BY id DESC LIMIT 1;"""
    params = [amount, user_id]
    await self.execute_query(query, params)
    query = f"""SELECT total_amount FROM {self.table} WHERE user_id=(%s);"""
    params = [user_id]
    return await self.execute_query(query, params, True)

  async def get_payment_status(self, user_id):
    query = f"""SELECT pay_status, label FROM {self.table} WHERE user_id=(%s);"""
    params = [user_id]
    return await self.execute_query(query, params, True)


class UserActivitiesDatabase(DataBase):
  def __init__(self, bd_user, bd_password, bd_host, bd_database):
    super().__init__(bd_user, bd_password, bd_host, bd_database)
    self.table = "user_activities"
  
  async def getAll(self):
    query = f"""SELECT * FROM {self.table}"""
    return await self.execute_query(query, isNeedFetch=True)