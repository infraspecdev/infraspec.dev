---
title: "Securing and Rotating Secrets Easily with AWS Secrets Manager"
authorId: "saumitra"
date: 2024-04-21
draft: false
featured: true
weight: 1
---

Automating Secret Rotation with AWS Secrets Manager

Managing secrets has always been a significant aspect when deploying applications. Typically, we set up a pipeline to provide secrets to our application as Environment Variables. For enhanced security, we can also choose to encrypt our secrets and store them as configuration files, which the application can access and decrypt at runtime.

However, using long-lived credentials in our applications is a risky practice. The potential damage in the future could be substantial due to their indefinite validity, leading to risks like data theft, privacy breaches, and unauthorized access. On the other hand, short-lived credentials, while not entirely hack-proof, help reduce unauthorized access by expiring after a set period.

We can utilize services such as AWS Secrets Manager to efficiently manage secrets, automatically rotate them, and use them in our application. In this blog, I will explore setting up AWS Secrets Manager and Lambda functions to accomplish this. Let's begin!

## Before using AWS Secrets Manager

For this example, I will be considering a simple Node.js application that uses the Google Calendar API to get events from a specific calendar. So far, we've been using Service Account keys to easily reach the Google Calendar API. Service Accounts help make Access Tokens for Google API use. Since Service Account keys stay valid for a long time, it's not recommended for the app to directly use them for access. Let's employ AWS Secrets Manager and Lambda functions to:

1. Use the Service Account key to make the Access Token.

2. Save the Access Token in the Secrets Manager.

This method allows the app to get the Access Token from Secrets Manager and remove the need for Service Account keys.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713684534307/5b4af0ac-04e8-4994-8477-a3da850a1702.png" alt="" width="500px" />

This is my starter code. The Google Service Account key being used is a long-lived credential. That's why I aim to remove this dependency by having an external service provide my application with the Access Token, which is a short-lived credential.

Let's start configuring the AWS infrastructure to set up AWS Secrets Manager and Lambda functions.

## Configuring the AWS Secrets Manager and Lambda functions

### Configuring the AWS Secrets Manager

1. Visit the [Secrets Manager](https://us-east-1.console.aws.amazon.com/secretsmanager/home?region=us-east-1) service in the AWS Console.

2. Let's begin by storing a new secret, and let the type of secret be set to "Other type of secret".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713608995307/9ac004d5-b92c-4d5c-a5fe-c28e35d79ee0.png" alt="" width="500px" />

3. As I will be storing the Access Token, let's set the secret key as "*GOOGLE\_ACCESS\_TOKEN*" and leave the value empty.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713609088974/97402a01-e589-4389-82a4-6189de10bc18.png" alt="" width="500px" />

4. For the Encryption key selection, I'll leave it as the default option, which is a key managed by AWS. However, you can choose to take an additional step and utilize customer-managed keys for encrypting secrets if you prefer.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713609212808/64fc2162-1ff8-473e-9efb-8ce20fe0a855.png" alt="" width="500px" />

5. In the "Configure secret" step, let's name our secret "*demo/GoogleAuth/AccessToken*".

6. In the "Configure rotation" step, let's keep the Automatic rotation disabled. We will set up a Lambda function later for Automatic rotation.

And there we have it, we have successfully created our secret in the Secrets Manager. Now, let's proceed to create the Lambda function. This function can be triggered by the Secrets Manager to rotate the secret.

### Configuring the AWS Lambda function

1. Visit the [Lambda](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/begin) service in the AWS Console.

2. Create a new Lambda function and select the "Author from scratch" option.

3. Since the function is meant to refresh the Google Access Token secret, name it "*refreshGoogleAccessTokenSecret*".

4. I will write the Lambda function in JavaScript, so I'll choose the Runtime as "Node.js 20.x" and keep the Architecture as "x86\_64".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713610154824/59076adb-b75c-4afc-af1b-4fffc171d4ca.png" alt="" width="500px" />

5. Create the function.

Now that we have configured the Secrets Manager and the Lambda function, let's link them together.

### Allowing Secrets Manager to invoke our Lambda function by providing permission

We can now set up automatic rotation in the Secrets Manager and connect it to our Lambda function.

Before linking them, we need to grant permissions to our Lambda function so that it can be invoked on a scheduled basis through the Secrets Manager.

1. Go to the Lambda function overview page.

2. Scroll down to locate the "Configuration" tab, and then go to the "Permissions" tab within it.

3. Scroll further down to the "Resource-based policy statements" section. Click on "Add permissions".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713610729973/9424af50-3d95-45b0-80a8-0b0792a9045d.png" alt="" width="500px" />

4. In the "Edit policy statement" section, choose the "AWS service" option.

5. Under the Service dropdown, select "Secrets Manager".

6. For the Statement ID, let's name it "*scheduled-invocation-policy*".

7. Make sure that the principal is set to "*secretsmanager.amazonaws.com*".

8. Finally, select the "lambda:InvokeFunction" action from the Action dropdown, and then click on Save.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611043263/be59f2ed-76b0-498a-88ff-5d66fc8cb6cd.png" alt="" width="500px" />

This permission will enable the Secrets Manager service to refer to our Lambda function and automatically trigger it at a set schedule.

### Configuring automatic rotation in the Secrets Manager

We can now configure automatic rotation in the Secrets Manager and reference our Lambda function.

Since I will be rotating the Google Access Token, I will generate the Access Token with a validity of 12 hours, which is the maximum allowed. This allows me to schedule automatic rotation to refresh the access token every 12 hours.

1. Visit the Secrets Manager service page to check our secret details.

2. Scroll down to locate the "Rotation" tab.

    At first, automatic rotation is turned off. You can activate this by clicking on "Edit rotation".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611445134/88a23906-17ca-459f-b850-ec9bdeb77149.png" alt="" width="500px" />

3. In the "Edit rotation configuration" window, enable "Automatic rotation".

4. In the "Rotation schedule" section, we can set our desired schedule. To refresh the Access Token every 12 hours, I will choose "Hours" as the Time Unit and set it to *12* hours.

    Additionally, we have the option to define our schedule using an expression, similar to a cron schedule expression. This allows us to create more complex schedules effortlessly.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611697737/513d6a77-313a-4558-8155-1b9fcef1923d.png" alt="" width="500px" />

5. Finally, under the "Rotation function" section, select the created Lambda function from the dropdown menu, and click Save.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611755247/f651be0b-431a-4c4d-958c-0957af313f34.png" alt="" width="500px" />

Upon saving, you should now notice that the automatic rotation is now enabled.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713611799096/c2bc590e-f40e-4bf3-87cc-69d044c8363f.png" alt="" width="500px" />

### Allowing our Lambda function to update secrets in the Secret Manager by defining a policy

Before diving into implementing our Lambda function, it will require permission to update secrets in the Secrets Manager. This permission can be granted by creating a new policy in IAM and then attaching it to our Lambda function's role.

Let's start by defining our policy in IAM.

1. Visit the [IAM dashboard](https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-1#/home) in the AWS Console.

2. Under "Access management," click on "Policies."

3. Create a new policy.

4. In the "Specify permissions" section, under "Select a service," choose "Secrets Manager" in the dropdown to see all permissions.

5. In the "Actions allowed" section, under the "Write" Access level, check the "UpdateSecret" box. Also, ensure that the "Effect" is set to "Allow."

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713612384644/2b79381c-f7a4-4058-a3f8-aae573baa660.png" alt="" width="500px" />

6. Next, in the "Resources" section, we have the option to either permit access to all resources (meaning all stored Secrets under the Secrets Manager) or limit access to only chosen Secrets.

    Typically, it's best to grant access to specific Secrets that are needed, according to the policy. Since we are setting up the policy for our Lambda function to access the "*demo/GoogleAuth/AccessToken*" secret, we will restrict access to only that specific Secret.

    We can do this by:

    1. Visit the Secrets Manager page and view the secret details,

    2. Copy the secret's ARN (Amazon Resource Name, which uniquely identifies resources), and

    3. Paste the Secret ARN in the "Specify ARN(s)" window after clicking "Add ARNs".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713612844675/64bfccc8-300b-4ad3-8a3e-d0924b50d23b.png" alt="" width="500px" />

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713686110615/14f8cd33-6d33-401c-b17e-1f4435a1339a.png" alt="" width="500px" />

    Click on "Add ARNs" and then click on "Next".

7. Under "Policy details", let's name our policy "*demo-GoogleAuth-AccessToken-UpdateSecret-policy*" since it is closely linked to our "*demo/GoogleAuth/AccessToken*" Secret.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713613225433/a8f2bbd7-0328-46e2-be74-1a8571bc709a.png" alt="" width="500px" />

8. Create policy.

### Linking the Policy under our Lambda function's role in the IAM

Now that we have created a policy to allow updating our Secret in the Secrets Manager, let's proceed to link this policy under the Lambda function's role. You can find the Lambda function's role in IAM under **Access Management &gt; Roles**.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713613440260/66ba5c84-aee8-41b4-ada0-adb7e6292e09.png" alt="" width="500px" />

1. Click on the role name to view the role's details.

2. Scroll down to "Permissions policies" and click on **Add permissions &gt; Attach policies**. This allows us to link our Policy to this role, granting our Lambda function access to the Secret and enabling it to update the Secret's value.

3. In the "Other permissions policies" section, search for the newly created Policy.

4. Lastly, select the Policy and click on "Add permissions".

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713613912767/e4ed5eb6-4f92-41b9-b948-bd7db58ea5bc.png" alt="" width="500px" />

This action will link our Policy to the role, giving access to the Secret and enabling our Lambda function to securely update the Secret's value.

This completes all the essential configuration needed for our Lambda function to securely update the Secret's value, and we can now move on to implementing the Lambda function.

### Implementing our Lambda function to rotate Access Token

Our Lambda function will use the Google Service Account key and scopes to create an Access Token with a specific validity period. It will then update the value of the Secret in the Secrets Manager.

We can input the Service Account key as a Base64-encoded string and the scopes as Environment Variables. Additionally, the Lambda function will need the Secret's name (in this case, "*demo/GoogleAuth/AccessToken*"). We can choose to read this as an Environment Variable or hard-code it. I recommend reading it as an Environment Variable to avoid tight coupling. Hard coding could complicate future changes, as we would need to find and update all references to the Secret, even within the Lambda function implementations.

Okay, enough blabbering, let's get into the implementation part.

1. Visit the Lambda function overview page.

2. Scroll down to view the template code or the starter code under the "Code" tab.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713616449381/ed7a3b7e-1630-4f4e-b8dd-801481952678.png" alt="" width="500px" />

    In my case, the `handler` function represents the core of our Lambda function and acts as the starting point.

    We can access the Google Service Account key using Environment Variables, specifically through `process.env` in my scenario. Let's promptly configure the necessary Environment Variables for our Lambda function.

3. Under the "Configuration" tab, within the "Environment variables" section, click on "Edit environment variables." Here, we can input our details - Service Account key as Base64, scopes, and the Secret's name.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713686228053/8551b641-58c3-47e4-b7ce-e412e9b8456c.png" alt="" width="500px" />

4. Click on Save.

Next, let's proceed with implementing our Lambda function.

Within the Function overview page, under the "Code" tab, we can edit the source code and implement the Lambda function. Since our Lambda function utilizes Google APIs to create Access Tokens, it will need the [googleapis](https://www.npmjs.com/package/googleapis) dependency from the NPM repository. Moreover, we will need [@aws-sdk/client-secrets-manager](https://www.npmjs.com/package/@aws-sdk/client-secrets-manager) to update the Secret in the Secrets Manager.

We need to include all dependencies in our Lambda function's source code because we can't install NPM modules on the go. Another option is to use NPM modules by setting up an EC2 instance (as recommended in this [blog](https://aws.amazon.com/blogs/compute/nodejs-packages-in-lambda/)). However, the easiest method is to work on the Lambda function's source code locally. We do this by starting an NPM project, installing the necessary dependencies, packaging the whole project into a ZIP file, and then uploading it.

Let's first initialize an empty Node project.

```bash
npm init -y
```

Below is the implementation of the *google\_auth\_init.mjs* file, which defines the `createGoogleAuthFromBase64Credentials` function used to create a GoogleAuth instance.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713684887551/9adc880b-01f0-48d0-a5ed-fb07c837c60f.png" alt="" width="500px" />

Let's now implement the *aws\_secrets\_manager\_init.mjs* file. This file will contain the `createAwsSecretsManagerClient` function, used to create an instance of SecretsManagerClient.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713684941025/3d77dbee-ef47-4068-9b69-d37da7da385b.png" alt="" width="500px" />

Next, we can:

* Use the `createGoogleAuthFromBase64Credentials` function to create a new GoogleAuth instance,

* Generate an access token using the GoogleAuth,

* Create a new instance of SecretsManagerClient using the `createAwsSecretsManagerClient` function,

* Update the secrets using the SecretsManagerClient.

Let's proceed with implementing the source code in *index.mjs*.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713684982497/3a4c2ffc-2ee2-4c0a-979d-bbc67ef4c3f0.png" alt="" width="500px" />

Also, ensure that you install the dependencies before moving on to the uploading step.

```bash
npm install googleapis @aws-sdk/client-secrets-manager
```

Now that we have implemented the Lambda function, we can package all the source files, including their dependencies (node\_modules), into a ZIP file.

Open a terminal in the project's (or implementation's) root directory and execute the command to create a ZIP archive from the project files.

```bash
zip -r code.zip .
```

Next, open the Lambda function overview page, and under the "Code" tab, click on **Upload from &gt; .zip file**.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713619303737/3a95404b-bf36-4181-9113-921f9dc90702.png" alt="" width="500px" />

Select the generated ZIP file (in this case, "code.zip"), and upload it to update the Lambda function's source code.

### Testing out our Lambda function

After uploading the source code, let's test our Lambda function to confirm if it successfully rotates the Access Token in the Secrets Manager.

1. Visit the Lambda function overview page.

2. Scroll down to locate the "Test" tab.

3. In the "Test event" section, you can choose to create an event with details like the event name and the event JSON, which are then passed as parameters to the Lambda handler function. This step is optional and can be skipped in this case.

    Creating and using events can be useful when specific tests need to be defined.

4. Click on Test to trigger the Lambda function.

    <img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713620206250/bf3f361c-af43-4a4a-a41f-620b0509233b.png" alt="" width="500px" />

If the Lambda function successfully rotates the Access Token, we will observe that the Lambda function execution completes without any errors.

By checking the Secret in the Secrets Manager, we can verify that the Secret has indeed been updated.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713620378479/195bc4ee-02f6-447a-9c6a-4e819d4bb6fc.png" alt="" width="500px" />

**Note:** If the execution fails with a Task timed-out error, we can resolve this problem by extending the timeout duration.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713681543865/b0a713aa-93c5-4184-8382-7143a56f1411.png" alt="" width="500px" />

We can accomplish this by going to the Lambda function overview page, navigating to the "Configuration" tab, and then to "General configuration". Click on "Edit" and increase the timeout to a longer duration. In my situation, the timeout duration is currently set to 10 seconds.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713681595217/88bce40c-04f0-4a89-8f59-74030e7ff867.png" alt="" width="500px" />

## After using AWS Secrets Manager

Now that we have set up and configured our Secrets Manager service, we can smoothly integrate the secrets into our application using the AWS SDK.

In my case, I will utilize the [aws-sdk](https://www.npmjs.com/package/aws-sdk) NPM package to interact with AWS.

To access the Secrets Manager service securely, we must create a SecretsManagerClient. This client allows us to fetch secrets securely. Let's create the *aws\_secrets\_manager\_util.mjs* script, which will contain the necessary functions to set up a client and retrieve secrets using it.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713685334711/4e1ea108-500c-456d-bb8d-209082521df5.png" alt="" width="500px" />

We can now use the functions exported from my *aws\_secrets\_manager\_util.mjs* in the start script to effectively utilize the Google Access Token for fetching Calendar events and remove the reliance on Service Account keys in the application.

<img src="https://cdn.hashnode.com/res/hashnode/image/upload/v1713685490779/8cd4732e-ba09-4ed8-9e25-0b7934cd9c0b.png" alt="" width="500px" />

## Conclusion

In conclusion, by using AWS Secrets Manager with Lambda functions, we can automate secret rotation, improve security, and simplify management processes. This ensures smooth and effective handling of sensitive information in our applications. **Until next time, Happy Coding!**
