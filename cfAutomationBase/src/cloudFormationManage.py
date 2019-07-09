from __future__ import division, print_function, unicode_literals

from datetime import datetime
import logging
import json
import argparse

import boto3
import botocore

cf = boto3.client('cloudformation',region_name='us-east-1')  
log = logging.getLogger('deploy.cf.create_or_update') 
parser = argparse.ArgumentParser()
############################################################################################################################################
# Based on GIST - https://gist.github.com/svrist/73e2d6175104f7ab4d201280acba049c                                                          #
# @author - Kiran M                                                                                                                        #
# Extended to 2 Enry Points                                                                                                                #
#   * Lamda Hook                                                                                                                           #
#   * Direct Execution                                                                                                                     #
#       ex: /usr/local/bin/python /Users/kiran/Documents/python/test/src/cloudFormationManage.py -a prod -v                                #
#           (In Production account with verbose output)                                                                                    #
#       ex: /usr/local/bin/python /Users/kiran/Documents/python/test/src/cloudFormationManage.py -a prod                                   #
#           (In Production account without verbose output)                                                                                 #
############################################################################################################################################

# For Direct Execution
def main():
    
    requiredArgs = parser.add_argument_group('mandatory arguments')

    requiredArgs.add_argument("-a", "--account",
                    help="Specify the Profile to operate on ex: \"dev\" for Development, \"qa\" for Test and \"prod\" for Production Account",
                    choices=["dev", "qa","prod"], required=True)
    requiredArgs.add_argument("-t", "--target",
                    help="Specify the Target to operate on ex: \"clusters\" for Clusters, \"services\" for Services and \"all\" for Both Clusters and Services",
                    choices=["clusters", "services","all"], required=True)
    parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")

    args = parser.parse_args()

    if args.account == "dev":
        print ("using {} profile and operating on {}".format(args.account, args.target))
    elif args.account == "qa":
        print ("using {} profile and operating on {}".format(args.account, args.target))
    elif args.account == "prod":
        print ("using {} profile and operating on {}".format(args.account, args.target))

    with open('input/input.json', 'r') as JSON: 
        inputData = json.load(JSON)
        #print (inputData)

    #########################################################################################################
    # Creation of Clusters                                                                                  #
    # Input:                                                                                                #
    #   $HOMEDIR/input/input.json                                                                           #
    #    {                                                                                                  #
    #        "name": "CF Automation Base",                                                                  #
    #        "clusters": [                                                                                  #
    #        {                                                                                              #
    #            "cluster": {                                                                               #
    #               "stack_name": "fargate-cluster",                                                        #
    #               "template_name": "fargateClusterTemplates/fargateCluster.json",                         #
    #               "params_name": "fargateClusterParams/fargateClusterParams.json"                         #
    #            }                                                                                          #
    #        }                                                                                              #      
    #        ]                                                                                              #
    #    }                                                                                                  #  
    #########################################################################################################
    for cluster in inputData['clusters']:
        clusterTemplateName = args.account + "/" + cluster['cluster']['template_name']
        clusterParamTemplateName = args.account + "/" + cluster['cluster']['params_name']

        tempFile = open(clusterTemplateName, "rb")
        clusterTemplateContent = tempFile.read()
        tempFile.close()

        with open(clusterParamTemplateName, 'r') as JSON: 
            clusterParamTemplateJSON = json.load(JSON)

        if args.verbose:
            print (clusterTemplateContent)

        cfExecute(cluster['cluster']['stack_name'], clusterTemplateContent, clusterParamTemplateJSON)


    #########################################################################################################
    # Creation of Services                                                                                  #
    # Input:                                                                                                #
    #   $HOMEDIR/input/input.json                                                                           #
    #    {                                                                                                  #
    #        "name": "CF Automation Base",                                                                  #
    #        "services": [                                                                                  #
    #        {                                                                                              #
    #            "service": {                                                                               #
    #               "stack_name": "tracker-domain-cargo",                                                   #
    #               "template_name": "fargateServiceTemplates/privateSubnetPublicService.json",             #
    #               "params_name": "fargateServiceParams/tracker-domain-cargo-parameters.json"              #
    #            }                                                                                          #
    #        }                                                                                              #      
    #        ]                                                                                              #
    #    }                                                                                                  #  
    #########################################################################################################
    for service in inputData['services']:
        serviceTemplateName = args.account + "/" + service['service']['template_name']
        serviceParamTemplateName = args.account + "/" + service['service']['params_name']

        tempFile = open(serviceTemplateName, "rb")
        serviceTemplateContent = tempFile.read()
        tempFile.close()

        if args.verbose:
            print (serviceTemplateContent)

        with open(serviceParamTemplateName, 'r') as JSON: 
            serviceParamTemplateJSON = json.load(JSON)

        cfExecute(service['service']['stack_name'], serviceTemplateContent, serviceParamTemplateJSON)


# Lamda Hook for execution
def lambda_handler(event, context):    
    s3_client = boto3.client('s3')
    templateData = s3_client.get_object(Bucket=event['template_bucket'],Key=event['template_key'])
    parameterData = s3_client.get_object(Bucket=event['template_bucket'],Key=event['Parameters'])
    templateContent = templateData['Body'].read(templateData['ContentLength'])
    parameterContent = parameterData['Body'].read(parameterData['ContentLength'])
    parameterContentJSON = json.loads(str(parameterContent))

    cfExecute(event['stack_name'], templateContent, parameterContentJSON)


def cfExecute(stack_name, templateContent, parameterContentJSON):
    #print (templateContent)
    #print(parameterContentJSON)

    params = {
        'StackName': stack_name,
        'TemplateBody':templateContent,
        'Parameters': parameterContentJSON,
        'Capabilities': ['CAPABILITY_NAMED_IAM']
    }
    try:
        if _stack_exists(stack_name):
            print('Updating {}'.format(stack_name))
            stack_result = cf.update_stack(**params)
            waiter = cf.get_waiter('stack_update_complete')
        else:
            print('Creating {}'.format(stack_name))
            stack_result = cf.create_stack(**params)
            waiter = cf.get_waiter('stack_create_complete')
            print("...waiting for stack to be ready...")
            waiter.wait(StackName=stack_name)
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("No changes")
        else:
            raise
    else:
        print(json.dumps(
            cf.describe_stacks(StackName=stack_result['StackId']),
            indent=2,
            default=json_serial
        ))


def _parse_template(templatePath):
    response = cf.validate_template(
        TemplateBody=templatePath,
    )
    print(response)
    return response


def _parse_parameters(Parameters):
    with open(Parameters) as parameter_fileobj:
        parameter_data = json.load(parameter_fileobj)
        return parameter_data


def _stack_exists(stack_name):
    paginator = cf.get_paginator('list_stacks')
    for page in paginator.paginate():
        for stack in page['StackSummaries']:
            if stack['StackStatus'] == 'DELETE_COMPLETE':
                continue
            if stack['StackName'] == stack_name:
                return True
    return False


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


if __name__ == '__main__':
    main()
