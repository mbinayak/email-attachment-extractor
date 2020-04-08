### SES Email Receiver Attachment

###### v` 0.0.1 `

Simple python script for AWS lambda which act on a S3:Put event to extract files attached in email uploaded from Amazon SES

- React to S3 event 
- Pull the email file from the SES uploaded bucket
- Extract the files of extension type env variable FILE_EXT (eg: pdf)
- upload file or files to the bucket specified as BUCKET_STORE (default) otherwise upload to the SES configured bucket

** Trigger event sample attached **
