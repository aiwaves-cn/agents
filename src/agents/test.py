import types
def f():
  for i in range(3):
    yield 3*i
  return 10

def  main_gen():
  i = yield from [1,2,3]
  print(i)

def main():
  for message in main_gen():
      print(message)



main()