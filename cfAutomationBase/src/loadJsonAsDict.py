import json

with open('input/input.json', 'r') as JSON: 
    inputData = json.load(JSON)

for cluster in inputData['clusters']:
    print cluster['cluster']['stack_name']
    print cluster['cluster']['template_name']
    print cluster['cluster']['params_name']

for service in inputData['services']:
    print service['service']['stack_name']
    print service['service']['template_name']
    print service['service']['params_name']

