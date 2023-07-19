import json
 
with open("/home/aiwaves/longli/agents/examples/customer_service.json") as file:
    sop = json.load(file)
    print(sop)