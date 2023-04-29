from services.database import dataBase
from Api_token import *
import asyncio

async def main():
  db = dataBase(bd_user, bd_password, bd_host, bd_database)
  await db.add_user(user_id='1925481166', name="dada")
  # await db.update_label(user_id='1925481166', label="1qawfafa")
  # data = await db.get_payment_status(user_id=1925481166)
  # isPayd = data[-1][0]
  # label = data[-1][1]
  # print(isPayd, label) 
  return await db.update_total_amount(user_id='1925481166', amount=20)

print(asyncio.run(main()))