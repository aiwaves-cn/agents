'''
Author: lilong 2504702369@qq.com
Date: 2023-07-28 10:12:15
LastEditors: lilong 2504702369@qq.com
LastEditTime: 2023-08-09 15:27:58
FilePath: /longli/agents/src/agents/datebase.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from mongoengine import connect
import mongoengine
from pymongo import MongoClient

connect(
    db='shopping_assistant',
    host='47.96.122.196',
    port=27017,
    username='aiwaves',
    password='bxzn2023',
    authentication_source='admin')

# 任务配置
class TaskConfig(mongoengine.Document):
    user_id = mongoengine.IntField()  # 用户ID
    memory = mongoengine.DictField()  # 长期记忆
    current_node_name = mongoengine.StringField()  # 当前节点的名字


def add_date(user_id,memory,current_node_name):
  new_task = TaskConfig(user_id = user_id,memory = memory,current_node_name = current_node_name)
  new_task.save()

def find_data(user_id):
  return TaskConfig.objects(user_id=user_id).first()

def delete_data(user_id):
  task = TaskConfig.objects(user_id=user_id).first()
  task.delete()
  
all_tasks = TaskConfig.objects.all()
for task in all_tasks:
  task.delete()