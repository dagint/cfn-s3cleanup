#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####################################################################################################################
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.                                           #
#                                                                                                                   #
# Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance        #
# with the License. A copy of the License is located at                                                             #
#                                                                                                                   #
#     http://aws.amazon.com/asl/                                                                                    #
#                                                                                                                   #
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES #
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    #
# and limitations under the License.                                                                                #
#####################################################################################################################
import crhelper
import json
import boto3
import requests

# initialise logger
logger = crhelper.log_config({"RequestId": "CONTAINER_INIT"})
logger.info('Logging configured')
# set global to track init failures
init_failed = False

try:
    # Place initialization code here
    logger.info("Container initialization completed")
except Exception as e:
    logger.error(e, exc_info=True)
    init_failed = e


def create(event, context):
    """
    Place your code to handle Create events here.

    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    print("event: {}".format(event))

    physical_resource_id = event['ResourceProperties']['BucketName']
    response_data = {}
    return physical_resource_id, response_data


def update(event, context):
    """
    Place your code to handle Update events here

    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    print("event: {}".format(event))
    physical_resource_id = event['ResourceProperties']['BucketName']
    response_data = {}
    return physical_resource_id, response_data


def delete(event, context):
    """
    global logger
    logger = crhelper.log_config(event)
    """
    
    print("event: {}".format(event))

    bucket = event['ResourceProperties']['BucketName']
    response_data = empty_delete_buckets(bucket)

    physical_resource_id = event['PhysicalResourceId']
    return physical_resource_id, response_data

def handler(event, context):
    """
    Main handler function, passes off it's work to crhelper's cfn_handler
    """
    # update the logger with event info
    print("event: {}".format(event))
    global logger
    logger = crhelper.log_config(event)
    return crhelper.cfn_handler(event, context, create, update, delete, logger,
                                init_failed)

def empty_delete_buckets(bucket_name):
    global logger
    logger = crhelper.log_config(event)
    logger.info("trying to delete the bucket {0}".format(bucket_name))
    # s3_client = SESSION.client('s3', region_name=region)
    s3_client = boto3.client('s3')
    # s3 = SESSION.resource('s3', region_name=region)
    s3 = boto3.resource('s3')
    try:
        bucket = s3.Bucket(bucket_name).load()
    except ClientError as e:
        logger.error(e, exc_info=True)
        logger.error("bucket {0} does not exist".format(bucket_name))
        return
    # Check if versioning is enabled
    response = s3_client.get_bucket_versioning(Bucket=bucket_name)
    status = response.get('Status','')
    if status == 'Enabled':
         response = s3_client.put_bucket_versioning(Bucket=bucket_name,
                                                    VersioningConfiguration={'Status': 'Suspended'})
    paginator = s3_client.get_paginator('list_object_versions')
    page_iterator = paginator.paginate(
        Bucket=bucket_name
    )
    for page in page_iterator:
        logger.info(page)
        if 'DeleteMarkers' in page:
            delete_markers = page['DeleteMarkers']
            if delete_markers is not None:
                for delete_marker in delete_markers:
                    key = delete_marker['Key']
                    versionId = delete_marker['VersionId']
                    s3_client.delete_object(Bucket=bucket_name, Key=key, VersionId=versionId)
        if 'Versions' in page and page['Versions'] is not None:
            versions = page['Versions']
            for version in versions:
                logger.info(version)
                key = version['Key']
                versionId = version['VersionId']
                s3_client.delete_object(Bucket=bucket_name, Key=key, VersionId=versionId)
    object_paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = object_paginator.paginate(
        Bucket=bucket_name
    )
    for page in page_iterator:
        if 'Contents' in page:
            for content in page['Contents']:
                key = content['Key']
                s3_client.delete_object(Bucket=bucket_name, Key=content['Key'])
    #UNCOMMENT THE LINE BELOW TO MAKE LAMBDA DELETE THE BUCKET.
    # THIS WILL CAUSE AN FAILURE SINCE CLOUDFORMATION ALSO TRIES TO DELETE THE BUCKET
    #s3_client.delete_bucket(Bucket=bucket_name)
    #print "Successfully deleted the bucket {0}".format(bucket_name)
    logger.info("Successfully emptied the bucket {0}".format(bucket_name))
