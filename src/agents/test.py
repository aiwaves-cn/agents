# memory = {"name":"lli","num":0}
# add_date(0,memory,"0")


# a = find_data(0)
# print(a.memory)
# a.delete()



# # 创建一个新的任务配置文档
# new_task = TaskConfig(task_name="任务1", task_point=100, task_code="T001", task_count="1次", task_period="每天")
# new_task.save()  # 保存到数据库

# 查询所有任务配置文档
# all_tasks = TaskConfig.objects(task_name = "任务2")
# for task in all_tasks:
#   task.delete()

# all_tasks = TaskConfig.objects.all()
# for task in all_tasks:
#   print(task.task_name)




# # 创建一个新的任务配置文档
# new_task = TaskConfig(task_name="任务1", task_point=100, task_code="T001", task_count="1次", task_period="每天")
# new_task.save()  # 保存到数据库

# 查询所有任务配置文档
# all_tasks = TaskConfig.objects(task_name = "任务2")
# for task in all_tasks:
#   task.delete()

# all_tasks = TaskConfig.objects.all()
# for task in all_tasks:
#   print(task.task_name)


# # 连接MongoDB数据库
# client = MongoClient('mongodb://aiwaves:bxzn2023@47.96.122.196:27017')

# # 列出所有数据库
# database_names = client.list_database_names()
# print("所有数据库：", database_names)

# # 切换到指定数据库
# db = client['shopping_assistant']

# # 列出该数据库中的所有集合
# collection_names = db.list_collection_names()
# print("该数据库中的所有集合：", collection_names)

# # 关闭连接
# client.close()


