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
    now_node_name = mongoengine.StringField()  # 当前节点的名字


def add_date(user_id,memory,now_node_name):
  new_task = TaskConfig(user_id = user_id,memory = memory,now_node_name = now_node_name)
  new_task.save()

def find_data(user_id):
  return TaskConfig.objects(user_id=user_id).first()

def delete_data(user_id):
  task = TaskConfig.objects(user_id=user_id).first()
  task.delete()
  
all_tasks = TaskConfig.objects.all()
for task in all_tasks:
  task.delete()