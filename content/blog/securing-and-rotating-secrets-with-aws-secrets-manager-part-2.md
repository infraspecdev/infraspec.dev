---
title: "Securing and Rotating Secrets Easily with AWS Secrets Manager - Part 2"
authorIds: ["saumitra"]
date: 2024-04-22
draft: false
featured: true
weight: 1
---

In [Part 1](/blog/securing-and-rotating-secrets-with-aws-secrets-manager-part-1/), we discussed upon configuring AWS Secrets Manager, AWS Lambda, and Automatic Rotation for our Secret. We also defined permissions for our Lambda function, which enabled the Secrets Manager to invoke it on a scheduled basis. In Part 2, we will focus on setting up the Lambda function, including the required permissions and implementation.

## Allowing our Lambda function to update secrets in the Secret Manager

Before diving into implementing our Lambda function, it will require permission to update secrets in the Secrets Manager. This permission can be granted by creating a new policy in IAM and then attaching it to our Lambda function's role.

Let's start by defining our policy in IAM.

### **Using AWS CLI**

```bash
# Create a policy.json (make sure to replace the "REGION" and "YOUR_ACCOUNT_ID" with the appropriate region name, and your Account ID, respectively)
echo '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:UpdateSecret",
      "Resource": "arn:aws:secretsmanager:[REGION]:[YOUR_ACCOUNT_ID]:secret:demo/GoogleAuth/AccessToken-*"
    }
  ]
}' > policy.json
```

```bash
# Create the IAM policy
aws iam create-policy --policy-name "demo-GoogleAuth-AccessToken-UpdateSecret-policy" --policy-document file://policy.json
```

### **Using AWS Console**

1. Visit the [IAM dashboard](https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-1#/home) in the AWS Console.

2. Under "Access management," click on "Policies."

3. Create a new policy.

4. In the "Specify permissions" section, under "Select a service," choose "Secrets Manager" in the dropdown to see all permissions.

5. In the "Actions allowed" section, under the "Write" Access level, check the "UpdateSecret" box. Also, ensure that the "Effect" is set to "Allow."

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713612384644/2b79381c-f7a4-4058-a3f8-aae573baa660.png" alt="" width="600px" />

6. Next, in the "Resources" section, we have the option to either permit access to all resources (meaning all stored Secrets under the Secrets Manager) or limit access to only chosen Secrets.

    Typically, it's best to grant access to specific Secrets that are needed, according to the policy. Since we are setting up the policy for our Lambda function to access the "*demo/GoogleAuth/AccessToken*" secret, we will restrict access to only that specific Secret.

    We can do this by:

    1. Visit the Secrets Manager page and view the secret details,

    2. Copy the secret's ARN (Amazon Resource Name, which uniquely identifies resources), and

    3. Paste the Secret ARN in the "Specify ARN(s)" window after clicking "Add ARNs".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713612844675/64bfccc8-300b-4ad3-8a3e-d0924b50d23b.png" alt="" width="600px" />

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713686110615/14f8cd33-6d33-401c-b17e-1f4435a1339a.png" alt="" width="600px" />

    Click on "Add ARNs" and then click on "Next".

7. Under "Policy details", let's name our policy "*demo-GoogleAuth-AccessToken-UpdateSecret-policy*" since it is closely linked to our "*demo/GoogleAuth/AccessToken*" Secret.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713613225433/a8f2bbd7-0328-46e2-be74-1a8571bc709a.png" alt="" width="600px" />

8. Create policy.

## Linking the Policy under our Lambda function's role in the IAM

Now that we have created a policy to allow updating our Secret in the Secrets Manager, let's proceed to link this policy under the Lambda function's role. You can find the Lambda function's role in IAM under **Access Management &gt; Roles**.

### **Using AWS CLI**

```bash
# Attach the IAM policy to the Lambda function's Execution Role (make sure to replace the "YOUR_ACCOUNT_ID" with your Account ID)
aws iam attach-role-policy --role-name "lambda_ex" --policy-arn "arn:aws:iam::[YOUR_ACCOUNT_ID]:policy/demo-GoogleAuth-AccessToken-UpdateSecret-policy"
```

### **Using AWS Console**

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713613440260/66ba5c84-aee8-41b4-ada0-adb7e6292e09.png" alt="" width="600px" />

1. Click on the role name to view the role's details.

2. Scroll down to "Permissions policies" and click on **Add permissions &gt; Attach policies**. This allows us to link our Policy to this role, granting our Lambda function access to the Secret and enabling it to update the Secret's value.

3. In the "Other permissions policies" section, search for the newly created Policy.

4. Lastly, select the Policy and click on "Add permissions".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713613912767/e4ed5eb6-4f92-41b9-b948-bd7db58ea5bc.png" alt="" width="600px" />

This action will link our Policy to the role, giving access to the Secret and enabling our Lambda function to securely update the Secret's value.

This completes all the essential configuration needed for our Lambda function to securely update the Secret's value, and we can now move on to implementing the Lambda function.

## Implementing our Lambda function

Our Lambda function will use the Google Service Account key and scopes to create an Access Token with a specific validity period. It will then update the value of the Secret in the Secrets Manager.

We can input the Service Account key as a Base64-encoded string and the scopes as Environment Variables. Additionally, the Lambda function will need the Secret's name (in this case, "*demo/GoogleAuth/AccessToken*"). We can choose to read this as an Environment Variable or hard-code it. I recommend reading it as an Environment Variable to avoid tight coupling. Hard coding could complicate future changes, as we would need to find and update all references to the Secret, even within the Lambda function implementations.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1714815374400/1248f5af-a1bf-4c58-8ad4-fef2f55ef815.png" alt="" width="600px" />

The above flowchart outlines a Lambda function's operation for rotating an access token. The function begins by extracting necessary Environment Variables, initializes Google Auth for access token generation, and then sets up the AWS Secrets Manager client. Once the token is generated, the function prepares and sends an update command to Secrets Manager to update the secret. It concludes by returning a successful response upon the successful updating of the secret in AWS.

Okay, enough blabbering, let's set up the necessary Environment Variables, and get into the implementation part.

### **Using AWS CLI**

```bash
# Set the Environment Variables in the Lambda Function
aws lambda update-function-configuration --function-name "refreshGoogleAccessTokenSecret" --environment "Variables={GOOGLE_SERVICE_ACCOUNT_KEY_BASE64='* * *',GOOGLE_APIS_SCOPES='https://www.googleapis.com/auth/calendar.events.readonly,https://www.googleapis.com/auth/calendar.readonly',SECRET_ID='demo/GoogleAuth/AccessToken'}"
```

### **Using AWS Console**

1. Visit the Lambda function overview page.

2. Scroll down to view the template code or the starter code under the "Code" tab.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713616449381/ed7a3b7e-1630-4f4e-b8dd-801481952678.png" alt="" width="600px" />

    In my case, the `handler` function represents the core of our Lambda function and acts as the starting point.

    We can access the Google Service Account key using Environment Variables, specifically through `process.env` in my scenario. Let's promptly configure the necessary Environment Variables for our Lambda function.

3. Under the "Configuration" tab, within the "Environment variables" section, click on "Edit environment variables." Here, we can input our details - Service Account key as Base64, scopes, and the Secret's name.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713686228053/8551b641-58c3-47e4-b7ce-e412e9b8456c.png" alt="" width="600px" />

    Click on Save.

Next, let's proceed with implementing our Lambda function.

Within the Function overview page, under the "Code" tab, we can edit the source code and implement the Lambda function. Since our Lambda function utilizes Google APIs to create Access Tokens, it will need the [googleapis](https://www.npmjs.com/package/googleapis) dependency from the NPM repository. Moreover, we will need [@aws-sdk/client-secrets-manager](https://www.npmjs.com/package/@aws-sdk/client-secrets-manager) to update the Secret in the Secrets Manager.

We need to include all dependencies in our Lambda function's source code because we can't install NPM modules on the go. Another option is to use NPM modules by setting up an EC2 instance (as recommended in this [blog](https://aws.amazon.com/blogs/compute/nodejs-packages-in-lambda/)). However, the easiest method is to work on the Lambda function's source code locally. We do this by starting an NPM project, installing the necessary dependencies, packaging the whole project into a ZIP file, and then uploading it.

Let's first initialize an empty Node project.

```bash
npm init -y
```

Below is the implementation of the *google\_auth\_init.mjs* file, which defines the `createGoogleAuthFromBase64Credentials` function used to create a GoogleAuth instance.

```javascript
// google_auth_init.mjs
import { google } from "googleapis";

/**
 * Initializes a new GoogleAuth from the specified credentials
 * and scopes.
 */
export function createGoogleAuthFromBase64Credentials(
    credentialsInBase64,
    scopes
) {
    // Decode the Base64 string using `atob` function
    const decodedCredentials = atob(credentialsInBase64);
    const decodedCredentialsInJson = JSON.parse(decodedCredentials);

    return new google.auth.GoogleAuth({
        credentials: decodedCredentialsInJson,
        scopes,
    });
}
```

Let's now implement the *aws\_secrets\_manager\_init.mjs* file. This file will contain the `createAwsSecretsManagerClient` function, used to create an instance of SecretsManagerClient.

```javascript
// aws_secrets_manager_init.mjs
import { SecretsManagerClient } from "@aws-sdk/client-secrets-manager";

/**
 * Initializes a new SecretsManagerClient instance
 */
export function createAwsSecretsManagerClient() {
    const client = new SecretsManagerClient({
        region: "us-east-1"
    });
    return client;
}
```

Next, we can:

* Use the `createGoogleAuthFromBase64Credentials` function to create a new GoogleAuth instance,

* Generate an access token using the GoogleAuth,

* Create a new instance of SecretsManagerClient using the `createAwsSecretsManagerClient` function,

* Update the secrets using the SecretsManagerClient.

Let's proceed with implementing the source code in *index.mjs*.

```javascript
// index.mjs
import { UpdateSecretCommand } from "@aws-sdk/client-secrets-manager";

import { createGoogleAuthFromBase64Credentials } from "./google_auth_init.mjs";
import { createAwsSecretsManagerClient } from "./aws_secrets_manager_init.mjs";

const { GOOGLE_SERVICE_ACCOUNT_KEY_BASE64, GOOGLE_APIS_SCOPES, SECRET_ID } = process.env;

// Entry point
export const handler = async (event) => {
    const googleAuthScopes = GOOGLE_APIS_SCOPES.split(",");
    const googleAuth = createGoogleAuthFromBase64Credentials(
        GOOGLE_SERVICE_ACCOUNT_KEY_BASE64,
        googleAuthScopes
    );

    // Generate a new Access Token, and prepare
    // an object with updated secrets.
    const accessToken = await googleAuth.getAccessToken();
    const updatedSecrets = {
        GOOGLE_ACCESS_TOKEN: accessToken,
    };

    const secretsManagerClient = createAwsSecretsManagerClient();

    // Prepare the update secret command with
    // secret id (name of the Secret), and
    // secret string which is the updated secrets
    // stringified.
    const updateSecretCommand = new UpdateSecretCommand({
        SecretId: SECRET_ID,
        SecretString: JSON.stringify(updatedSecrets),
    });

    // Commit the changes to Secrets Manager
    await secretsManagerClient.send(updateSecretCommand);

    // Return a response with the status code
    const response = {
        statusCode: 200,
        body: "Access Token was rotated",
    };
    return response;
};
```

Also, ensure that you install the dependencies before moving on to the uploading step.

```bash
npm install googleapis @aws-sdk/client-secrets-manager
```

Now that we have implemented the Lambda function, we can package all the source files, including their dependencies (node\_modules), into a ZIP file.

Open a terminal in the project's (or implementation's) root directory and execute the command to create a ZIP archive from the project files.

```bash
zip -r code.zip .
```

#### Uploading the ZIP file using AWS CLI

```bash
# Upload the ZIP file containing the Lambda function implementation
aws lambda update-function-code --function-name "refreshGoogleAccessTokenSecret" --zip-file fileb://code.zip
```

#### Uploading the ZIP file using AWS Console

Next, open the Lambda function overview page, and under the "Code" tab, click on **Upload from &gt; .zip file**.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713619303737/3a95404b-bf36-4181-9113-921f9dc90702.png" alt="" width="600px" />

Select the generated ZIP file (in this case, "*code.zip*"), and upload it to update the Lambda function's source code.

## Testing out the Lambda function

After uploading the source code, let's test our Lambda function to confirm if it successfully rotates the Access Token in the Secrets Manager.

### **Using AWS CLI**

```bash
# Invoke the Lambda function and store the result to "output.txt"
aws lambda invoke --function-name "refreshGoogleAccessTokenSecret" --payload '{}' output.txt
```

```bash
# View the result
cat output.txt
```

### **Using AWS Console**

1. Visit the Lambda function overview page.

2. Scroll down to locate the "Test" tab.

3. In the "Test event" section, you can choose to create an event with details like the event name and the event JSON, which are then passed as parameters to the Lambda handler function. This step is optional and can be skipped in this case.

    Creating and using events can be useful when specific tests need to be defined.

4. Click on Test to trigger the Lambda function.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713620206250/bf3f361c-af43-4a4a-a41f-620b0509233b.png" alt="" width="600px" />

If the Lambda function successfully rotates the Access Token, we will observe that the Lambda function execution completes without any errors.

By checking the Secret in the Secrets Manager, we can verify that the Secret has indeed been updated.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713620378479/195bc4ee-02f6-447a-9c6a-4e819d4bb6fc.png" alt="" width="600px" />

**Note:** If the execution fails with a Task timed-out error, we can resolve this problem by extending the timeout duration.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713681543865/b0a713aa-93c5-4184-8382-7143a56f1411.png" alt="" width="600px" />

We can accomplish this by going to the Lambda function overview page, navigating to the "Configuration" tab, and then to "General configuration". Click on "Edit" and increase the timeout to a longer duration. In my situation, the timeout duration is currently set to 10 seconds.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713681595217/88bce40c-04f0-4a89-8f59-74030e7ff867.png" alt="" width="600px" />

## After using AWS Secrets Manager

Now that we have set up and configured our Secrets Manager service, we can smoothly integrate the secrets into our application using the AWS SDK.

In my case, I will utilize the [aws-sdk](https://www.npmjs.com/package/aws-sdk) NPM package to interact with AWS.

To access the Secrets Manager service securely, we must create a SecretsManagerClient. This client allows us to fetch secrets securely. Let's create the *aws\_secrets\_manager\_util.mjs* script, which will contain the necessary functions to set up a client and retrieve secrets using it.

```javascript
// aws_secrets_manager_util.mjs
import AWS from "aws-sdk";

const { SecretsManager } = AWS;

/**
 * Initializes a new SecretsManager instance
 */
export function createSecretsManagerClient(region) {
    const client = new SecretsManager({ region });
    return client;
}

/**
 * Fetches secrets from a Secret Manager using the client and the secret Id
 * @returns {Promise<{ GOOGLE_ACCESS_TOKEN: string }>} Secrets
 */
export async function getSecretsFromSecretsManagerClient(client, secretId) {
    const secretsResult = await client
        .getSecretValue({
            SecretId: secretId,
        })
        .promise();

    const secrets = JSON.parse(secretsResult.SecretString);
    return secrets;
}
```

We can now use the functions exported from my *aws\_secrets\_manager\_util.mjs* in the start script to effectively utilize the Google Access Token for fetching Calendar events and remove the reliance on Service Account keys in the application.

```javascript
import { config } from "dotenv";
config();

import {
    createSecretsManagerClient,
    getSecretsFromSecretsManagerClient,
} from "./aws_secrets_manager_util.mjs";
import {
    createCalendarClient,
    getEventsByCalendarId,
} from "./google_calendar_service.mjs";

/**
 * AWS_SECRET_MANAGER_REGION -> AWS Secrets Manager Region (us-east-1)
 * AWS_SECRET_MANAGER_SECRET_ID -> AWS Secrets Manager Secret Id
 * (demo/GoogleAuth/AccessToken)
 */
const {
    AWS_SECRET_MANAGER_REGION,
    AWS_SECRET_MANAGER_SECRET_ID,
    GOOGLE_CALENDAR_ID,
} = process.env;

// Fetch Google Access Token from the AWS Secrets Manager
const secretsManagerClient = createSecretsManagerClient(
    AWS_SECRET_MANAGER_REGION
);
const { GOOGLE_ACCESS_TOKEN } = await getSecretsFromSecretsManagerClient(
    secretsManagerClient,
    AWS_SECRET_MANAGER_SECRET_ID
);

const calendarClient = createCalendarClient(GOOGLE_ACCESS_TOKEN);

// Fetch all Calendar events
getEventsByCalendarId(calendarClient, GOOGLE_CALENDAR_ID)
    .then(console.log)
    .catch(console.error);
```

## Conclusion

In conclusion, by using AWS Secrets Manager with Lambda functions, we can automate secret rotation, improve security, and simplify management processes. This ensures smooth and effective handling of sensitive information in our applications. **Until next time, Happy Coding!**
