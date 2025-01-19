import boto3
import json
import os



def check_credentials():
    session = boto3.Session()
    credentials = session.get_credentials()
    print(f"################ {credentials} ################")
    if credentials:
        # Print the credentials (do not log sensitive data in production)
        print("################ AWS Access Key:", credentials.access_key)
        print("AWS Secret Key:", credentials.secret_key)
        print("AWS Session Token:", credentials.token)
    else:
        print("No credentials found!")

def lambda_handler(event, context):
    try:
        # Initialize the S3 client
        s3_client = boto3.client('s3')

        # Parse the bucket and object key from the event
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = event['Records'][0]['s3']['object']['key']
        
        # Target bucket and key for saving the processed file
        target_bucket = os.getenv('TARGET_BUCKET', source_bucket)  # Use the same bucket by default
        target_key = f"processed/{source_key}"
        
        # Check AWS credentials
        check_credentials()

        # Fetch the file from S3
        response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
        file_content = response['Body'].read().decode('utf-8')
        
        # Process the content (example: convert to uppercase)
        processed_content = file_content.upper()
        
        # Save the processed file back to S3
        s3_client.put_object(
            Bucket=target_bucket,
            Key=target_key,
            Body=processed_content
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"File processed and saved to {target_bucket}/{target_key}")
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }