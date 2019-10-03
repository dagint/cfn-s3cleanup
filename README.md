# cfn-s3cleanup


## Description
A cloudformation template which includes a custom resource that calls a lambda to delete all objects in the bucket when a the cloudformation stack deletes.  It has support for s3 bucket versioning if it's enabled.  All the code needed is stored in the function/s3cleanup.zip + the cloudformation template s3cleanup.yaml.  This lambda, s3cleanup, code uses the AWS [crhelper](https://github.com/awslabs/aws-cloudformation-templates/tree/master/community/custom_resources/python_custom_resource_helper) code.  It also includes the requests module and all of it's requirements.  Everything in the function directory is included in the zip file.


## Requirements
Upload the zip file to a s3 bucket of your choosing.  You may need to make the object public.  Then update the mappings section in the the cloudformation template to reflect the bucket and the object path.  Update 'protectwithwaf', S3Bucket, with appropriate bucket name and update 'ProtectWithWAF', KeyPrefix, with the appropriate object folder or leave blank if it can be found in the root of the bucket.
```
Mappings:
  SourceCode:
    General:
      S3Bucket: 'protectwithwaf'
      KeyPrefix: 'ProtectWithWAF'
```
If you change the name of the zip file you will need to update the file name defined in the LambdaS3CleanupFunction block, specifically the S3Key section.  Update s3cleanup.zip with the appropriate file name.
```
S3Key: !Join ['/', [!FindInMap ["SourceCode", "General", "KeyPrefix"], 's3cleanup.zip']]
```


## Setup
Once you have completed the requirements above (zip file in a bucket with the correct permissions) you can deploy the s3cleanup.yaml cloudformation template.


## TODO
