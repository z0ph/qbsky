# :speaker: qbsky

Dead simple AWS SQS to Bluesky serverless poster :speaker:.

> Publish message :love_letter: to SQS (FIFO), Lambda function will handle publishing posts to Bluesky. Automagically. :tada:

Honestly, my intention is to automate the sharing of specific information through the use of this queue in several side projects. I'm bringing this to your attention because I couldn't find a comparable solution on Github or in open-source projects. I'm hopeful that it may prove useful to someone else.

## 🚀 Getting started

> Update variables in `Makefile` and `tf/variables.tf` according to your environment.

- type `make` to get started (help)

### Requirements

1. AWS Account
2. Bluesky Account
3. Terraform App

### How to deploy on your AWS Account

- `make all` (all-in-one command)

#### Manual - Under the hood (for Plumbers)

1. `make tf-package` (create the artifact and push to S3)
2. `make tf-init` (to prepare terraform deployment)
3. `make tf-apply` Deploy the infrastructure

_nb: Terraform is using remote state on S3._

#### Setup Bluesky secrets

After you've deployed the Terraform you will need to set Bluesky API credentials manually to AWS Secret Manager using AWS console.

Set the following credentials in AWS Secret Manager: `bluesky_handle` and `bluesky_password`

### 🗯️ How to publish a message

#### Using AWS Console

![Send messages](./assets/send-messages.png)

#### Using AWSCLI

`aws sqs send-message --queue-url https://sqs.us-east-1.amazonaws.com/80398EXAMPLE/MyQueue --message-body "Hello Folks!" --delay-seconds 10 --message-attributes file://send-message.json`

[AWS Documentation](https://docs.aws.amazon.com/cli/latest/reference/sqs/send-message.html)

#### :snake: Using Python (boto3)

```python
import boto3

# Create SQS client
sqs = boto3.client('sqs')

queue_url = 'SQS_QUEUE_URL'

# Send message to SQS queue
response = sqs.send_message(
    QueueUrl=queue_url,
    DelaySeconds=10,
    MessageAttributes={
        'Title': {
            'DataType': 'String',
            'StringValue': 'My Bluesky Post'
        },
        'Author': {
            'DataType': 'String',
            'StringValue': 'John Doe'
        }
    },
    MessageBody=(
        'Hello Bluesky! This is a test post from AWS SQS.'
    )
)

print(response['MessageId'])
```

[AWS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html)

## 📝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 🧘 License

[MIT](./LICENSE)

### 🐒 Credits

- [AWS SQS](https://aws.amazon.com/sqs/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Bluesky Social](https://bsky.app)
