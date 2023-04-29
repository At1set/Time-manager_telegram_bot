import mysql.connector
from Api_token import ADMIN_ID

class dataBase:
  def __init__(self, bd_user, bd_password, bd_host, bd_database) -> None:
    self.bd_user = bd_user
    self.bd_password = bd_password
    self.bd_host = bd_host
    self.bd_database = bd_database
  
  async def execute_query(self, query, params=None, isNeedFetch=False):
    try:
      connect = mysql.connector.connect(user=self.bd_user, password=self.bd_password, host=self.bd_host, database=self.bd_database, charset="utf8mb4")
      cursor = connect.cursor()
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

  async def add_user(self, user_id, name):
    query = """INSERT IGNORE INTO donater (user_id, name, role) VALUES (%s, %s, %s)"""
    params = [user_id, name, 'admin' if user_id == ADMIN_ID else "user"]
    return await self.execute_query(query, params)
  
  async def update_label(self, user_id, label):
    query = """UPDATE donater SET label=(%s) WHERE user_id=(%s) ORDER BY id DESC LIMIT 1;"""
    params = [label, user_id]
    return await self.execute_query(query, params)
  
  async def update_payment_status(self, user_id):
    query = """UPDATE donater SET pay_status=(%s) WHERE user_id=(%s) ORDER BY id DESC LIMIT 1;"""
    params = [True, user_id]
    return await self.execute_query(query, params)
  
  async def update_payment_count(self, user_id):
    query = """UPDATE donater SET pay_count=pay_count + 1 WHERE user_id = (%s) ORDER BY id DESC LIMIT 1;"""
    params = [user_id]
    await self.execute_query(query, params)
    query = """SELECT pay_count FROM donater WHERE user_id=(%s);"""
    params = [user_id]
    return await self.execute_query(query, params, True)
  
  async def update_total_amount(self, user_id, amount):
    query = """UPDATE donater SET total_amount=total_amount + (%s) WHERE user_id = (%s) ORDER BY id DESC LIMIT 1;"""
    params = [amount, user_id]
    await self.execute_query(query, params)
    query = """SELECT total_amount FROM donater WHERE user_id=(%s);"""
    params = [user_id]
    return await self.execute_query(query, params, True)

  async def get_payment_status(self, user_id):
    query = """SELECT pay_status, label FROM donater WHERE user_id=(%s);"""
    params = [user_id]
    return await self.execute_query(query, params, True)