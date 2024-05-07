---
title: "Securing and Rotating Secrets Easily with AWS Secrets Manager - Part 1"
authorId: "saumitra"
date: 2024-04-21
draft: false
featured: true
weight: 1
---

Automating Secret Rotation with AWS Secrets Manager

Managing secrets has always been a significant aspect when deploying applications. Typically, we set up a pipeline to provide secrets to our application as Environment Variables. For enhanced security, we can also choose to encrypt our secrets and store them as configuration files, which the application can access and decrypt at runtime.

However, [using long-lived credentials in our applications is a risky practice](https://www.chainguard.dev/unchained/the-principle-of-ephemerality). The potential damage in the future could be substantial due to their indefinite validity, leading to risks like data theft, privacy breaches, and unauthorized access. On the other hand, short-lived credentials, while not entirely hack-proof, help reduce unauthorized access by expiring after a set period.

We can utilize services such as AWS Secrets Manager to efficiently manage secrets, automatically rotate them, and use them in our application. In this blog, I will explore setting up AWS Secrets Manager and Lambda functions to accomplish this. Let's begin!

## Before using AWS Secrets Manager

For this example, I will be considering a simple Node.js application that uses the Google Calendar API to get events from a specific calendar. So far, we've been using Service Account keys to easily reach the Google Calendar API. Service Accounts help make Access Tokens for Google API use. Since Service Account keys stay valid for a long time, it's not recommended for the app to directly use them for access. Let's employ AWS Secrets Manager and Lambda functions to:

1. Use the Service Account key to make the Access Token.

2. Save the Access Token in the Secrets Manager.

This method allows the app to get the Access Token from Secrets Manager and remove the need for Service Account keys.

```javascript
import { config } from "dotenv";
config();

import { createGoogleAuthFromBase64Credentials } from "./google_auth_service";
import {
    createCalendarClient,
    getEventsByCalendarId,
} from "./google_calendar_service";

/**
 * `GOOGLE_AUTH_CREDENTIALS_BASE64` -> Google Service Account Key Encoded as Base64 String
 */
const {
    GOOGLE_AUTH_CREDENTIALS_BASE64,
    GOOGLE_AUTH_SCOPES,
    GOOGLE_CALENDAR_ID,
} = process.env;

// Split the `GOOGLE_AUTH_SCOPES` string by commas to retrieve a list of scopes
const googleAuthScopes = GOOGLE_AUTH_SCOPES.split(",");
const googleAuth = createGoogleAuthFromBase64Credentials(
    GOOGLE_AUTH_CREDENTIALS_BASE64,
    googleAuthScopes,
);

const calendarClient = createCalendarClient(googleAuth);

// Fetch all Calendar events
getEventsByCalendarId(calendarClient, GOOGLE_CALENDAR_ID)
    .then(console.log)
    .catch(console.error);
```

This is my starter code. The Google Service Account key being used is a long-lived credential. That's why I aim to remove this dependency by having an external service provide my application with the Access Token, which is a short-lived credential.

Let's start configuring the AWS infrastructure to set up AWS Secrets Manager and Lambda functions.

## Configuring the AWS Secrets Manager

### **Using AWS CLI**

```bash
# Create a new Secret under the Secrets Manager
aws secretsmanager create-secret --name "demo/GoogleAuth/AccessToken" --secret-string '{"GOOGLE_ACCESS_TOKEN":""}' --description "Storing Google Access Token" --kms-key-id "alias/aws/secretsmanager"
```

### **Using AWS Console**

1. Visit the [Secrets Manager](https://us-east-1.console.aws.amazon.com/secretsmanager/home?region=us-east-1) service in the AWS Console.

2. Let's begin by storing a new secret, and let the type of secret be set to "Other type of secret".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713608995307/9ac004d5-b92c-4d5c-a5fe-c28e35d79ee0.png" alt="" width="600px" />

3. As I will be storing the Access Token, let's set the secret key as "*GOOGLE\_ACCESS\_TOKEN*" and leave the value empty.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713609088974/97402a01-e589-4389-82a4-6189de10bc18.png" alt="" width="600px" />

4. For the Encryption key selection, I'll leave it as the default option, which is a key managed by AWS. However, you can choose to take an additional step and utilize customer-managed keys for encrypting secrets if you prefer.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713609212808/64fc2162-1ff8-473e-9efb-8ce20fe0a855.png" alt="" width="600px" />

5. In the "Configure secret" step, let's name our secret "*demo/GoogleAuth/AccessToken*".

6. In the "Configure rotation" step, let's keep the Automatic rotation disabled. We will set up a Lambda function later for Automatic rotation.

And there we have it, we have successfully created our secret in the Secrets Manager. Now, let's proceed to create the Lambda function. This function can be triggered by the Secrets Manager to rotate the secret.

## Configuring the AWS Lambda function

### **Using AWS CLI**

```bash
# Create a "trust-policy.json" to use while creating the Lambda Execution Role
echo '{
  "Statement": [ 
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}' > trust-policy.json
```

```bash
# Create an Execution Role for the Lambda function
aws iam create-role --role-name lambda_ex --assume-role-policy-document file://trust-policy.json
```

```bash
# Create an empty script file for the Lambda function, and create a Zip archive out of it
echo "" > index.js && zip function.zip index.js
```

```bash
# Create the Lambda function (make sure to replace the "YOUR_ACCOUNT_ID" with your Account ID)
aws lambda create-function --function-name "refreshGoogleAccessTokenSecret" --runtime "nodejs20.x" --role "arn:aws:iam::[YOUR_ACCOUNT_ID]:role/lambda_ex" --handler "index.handler" --architecture "x86_64" --zip-file fileb://function.zip
```

### **Using AWS Console**

1. Visit the [Lambda](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/begin) service in the AWS Console.

2. Create a new Lambda function and select the "Author from scratch" option.

3. Since the function is meant to refresh the Google Access Token secret, name it "*refreshGoogleAccessTokenSecret*".

4. I will write the Lambda function in JavaScript, so I'll choose the Runtime as "Node.js 20.x" and keep the Architecture as "x86\_64".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713610154824/59076adb-b75c-4afc-af1b-4fffc171d4ca.png" alt="" width="600px" />

5. Create the function.

Now that we have configured the Secrets Manager and the Lambda function, let's link them together.

## Allowing Secrets Manager to invoke our Lambda function

We can now set up automatic rotation in the Secrets Manager and connect it to our Lambda function.

Before linking them, we need to grant permissions to our Lambda function so that it can be invoked on a scheduled basis through the Secrets Manager.

### **Using AWS CLI**

```bash
# Create a new permission under the Lambda function (make sure to replace the `REGION` and `YOUR_ACCOUNT_ID` with the appropriate region name, and your Account ID, respectively)
aws lambda add-permission --function-name "refreshGoogleAccessTokenSecret" --statement-id "scheduled-invocation-policy" --action "lambda:InvokeFunction" --principal "secretsmanager.amazonaws.com" --source-arn "arn:aws:secretsmanager:[REGION]:[YOUR_ACCOUNT_ID]:secret:demo/GoogleAuth/AccessToken-*"
```

### **Using AWS Console**

1. Go to the Lambda function overview page.

2. Scroll down to locate the "Configuration" tab, and then go to the "Permissions" tab within it.

3. Scroll further down to the "Resource-based policy statements" section. Click on "Add permissions".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713610729973/9424af50-3d95-45b0-80a8-0b0792a9045d.png" alt="" width="600px" />

4. In the "Edit policy statement" section, choose the "AWS service" option.

5. Under the Service dropdown, select "Secrets Manager".

6. For the Statement ID, let's name it "*scheduled-invocation-policy*".

7. Make sure that the principal is set to "*secretsmanager.amazonaws.com*".

8. Finally, select the "lambda:InvokeFunction" action from the Action dropdown, and then click on Save.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611043263/be59f2ed-76b0-498a-88ff-5d66fc8cb6cd.png" alt="" width="600px" />

This permission will enable the Secrets Manager service to refer to our Lambda function and automatically trigger it at a set schedule.

## Configuring automatic rotation in the Secrets Manager

We can now configure automatic rotation in the Secrets Manager and reference our Lambda function.

Since I will be rotating the Google Access Token, I will generate the Access Token with a validity of 12 hours, which is the maximum allowed. This allows me to schedule automatic rotation to refresh the access token every 12 hours, instead of every 1 hour.

### **Using AWS CLI**

```bash
# Setup automatic rotation in the Secrets Manager (make sure to replace the "REGION", "YOUR_ACCOUNT_ID" and "SECRET_TRAILING_HASH", with the appropriate region name, your Account ID, and the Secret's ARN's trailing hash sequence, respectively)
aws secretsmanager rotate-secret --secret-id "arn:aws:secretsmanager:[REGION]:[YOUR_ACCOUNT_ID]:secret:demo/GoogleAuth/AccessToken-[SECRET_TRAILING_HASH]" --rotation-lambda-arn "arn:aws:lambda:[REGION]:[YOUR_ACCOUNT_ID]:function:refreshGoogleAccessTokenSecret" --rotation-rules '{"AutomaticallyAfterDays":12}'
```

### **Using AWS Console**

1. Visit the Secrets Manager service page to check our secret details.

2. Scroll down to locate the "Rotation" tab.

    At first, automatic rotation is turned off. You can activate this by clicking on "Edit rotation".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611445134/88a23906-17ca-459f-b850-ec9bdeb77149.png" alt="" width="600px" />

3. In the "Edit rotation configuration" window, enable "Automatic rotation".

4. In the "Rotation schedule" section, we can set our desired schedule. To refresh the Access Token every 12 hours, I will choose "Hours" as the Time Unit and set it to *12* hours.

    Additionally, we have the option to define our schedule using an expression, similar to a cron schedule expression. This allows us to create more complex schedules effortlessly.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611697737/513d6a77-313a-4558-8155-1b9fcef1923d.png" alt="" width="600px" />

5. Finally, under the "Rotation function" section, select the created Lambda function from the dropdown menu, and click Save.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611755247/f651be0b-431a-4c4d-958c-0957af313f34.png" alt="" width="600px" />

Upon saving, you should now notice that the automatic rotation is now enabled.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611799096/c2bc590e-f40e-4bf3-87cc-69d044c8363f.png" alt="" width="600px" />

## Continuation

In this blog, we covered the steps for configuring AWS Secrets Manager and AWS Lambda, as well as setting up Automatic Rotation for our Secret. In Part 2, we will further explore creating and utilizing the IAM policy for our Lambda function and implementing the Lambda function. You can find Part 2 [here](/blog/securing-and-rotating-secrets-with-aws-secrets-manager-part-2/).
