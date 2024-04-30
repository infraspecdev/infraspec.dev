---
title: "Step-by-Step Guide to Implement Winston Logger in your Node.js Projects"
authorId: "shivani"
date: 2024-04-29
draft: false
featured: true
weight: 1
---
___

"The only thing more satisfying than fixing a bug is reading the frustrated log messages that led you there." This humorous yet insightful quote perfectly encapsulates the importance of logging in software development. In any project, large or small, understanding what's happening under the hood is paramount.

<img src="/images/blog/guide-to-implement-winston-logger/logs-meme.jpeg" width="100%">

**Logging** is used to track errors, exceptions, warnings, and other events that may occur during the execution of an application.

It is crucial for understanding the behavior of an application and for troubleshooting issues that may arise during its operation. It is an important tool for developers, system administrators, and other IT professionals who need to monitor the performance and behavior of complex systems.

### **Logging Practices for Application Development:**

Here's a list of events that your application should log:

1. **Service Executions:** Keep track of the execution of various services within your application, including authentication, authorization, system access, data retrieval, and application usage.
    
2. **Resource Utilization:** Log instances of exhausted resources, exceeded capacities, and connectivity issues to ensure efficient resource management.
    
3. **Availability Monitoring**: Include log statements to monitor the runtime and availability of your application, capturing faults, exceptions, and system stability.
    
4. **Security Threats**: Record any security-related issues, such as invalid API keys, failed authentication attempts, and security verification failures, to mitigate potential threats.
    

### **Logging Libraries in Node.js**

Node.js offers various logging options beyond the default console module, allowing developers to structure, configure, and customize their logs efficiently. While `console.log` and `console.error` serve basic logging needs, they lack advanced features such as log structuring and customizable log levels. Fortunately, the Node ecosystem provides several logging libraries tailored to address these limitations. Let's explore some popular options:

1. [Winston](https://github.com/winstonjs/winston): A versatile logging library with support for multiple transports and customizable log formats.
    
2. [Bunyan](https://github.com/trentm/node-bunyan) : A high-performance logging library with structured logging capabilities.
    
3. [Pino](https://github.com/pinojs/pino): A lightweight and fast logging library optimized for performance.
    
4. [Log4js](https://github.com/log4js-node/log4js-node): A feature-rich logging library inspired by Apache Log4j, offering various configuration options[.](https://github.com/pinojs/pino)
    
5. [Debug](https://github.com/visionmedia/debug) : A tiny debugging utility for Node.js applications.
    

This post will delve into the process of configuring and utilizing the Winston library for logging messages.

## What is Winston Logger?

Winston Logger is a versatile logging library for Node.js applications, offering extensive flexibility and customization options compared to the built-in console module. Whether you're debugging code during development,or logging critical events in production, Winston provides the necessary tools and integrations to meet your logging needs effectively.

It supports logging to the console, files, databases, and third-party services like [Loggly or Papertrail](https://betterstack.com/logs?utm_medium=c&utm_campaign=adwords19703922957&utm_source=adwords&utm_content=648793502849&utm_term=papertrail&gad_source=1&gclid=CjwKCAjwoa2xBhACEiwA1sb1BG9qUjgD2jGosVMhYytL76lWcnaL38LiXWlSxH3z5Hk6FG7YjShL1BoCeU0QAvD_BwE), making it a popular choice for logging in Node.js projects.

## Installation and Setup

To get started with Winston Logger, you can install it via npm using the following command:

```bash
$ npm install winston
```

## Configuration Options

Winston Logger offers a wide range of configuration options to customize its behavior. You can set the log level, specify transports, define custom log formats, and more.

### **What are logging levels in Winston Logger?**

In Winston Logger, logging levels are used to categorize log messages based on their severity or importance. Winston defines several standard logging levels, each corresponding to a specific numeric value and representing different degrees of urgency.For example,

```javascript
levels: {
    error: 0,
    warn: 1,
    info: 2,
    http: 3,
    verbose: 4,
    debug: 5,
    silly: 6
  }
```

### **What are Transports in Winston Logger?**

In Winston Logger , Transports allow developers to specify how and where log messages should be logged, such as to the console, files, databases, http or third-party services. For example,

```javascript
 transports: [
    new winston.transports.Console(), 
    new winston.transports.File({ filename: 'logfile.log' }) 
}
```

Here are some popularly used custom transport to check out:

* [winston-daily-rotate-file](https://github.com/winstonjs/winston-daily-rotate-file)
    
* [winston-s](https://github.com/winstonjs/winston-daily-rotate-file)[yslog](https://www.npmjs.com/package/winston-syslog)
    
* [winst](https://www.npmjs.com/package/winston-syslog)[on-cloudwatch](https://www.npmjs.com/package/winston-cloudwatch)
    
* [wins](https://www.npmjs.com/package/winston-cloudwatch)[ton-mongodb](https://www.npmjs.com/package/winston-mongodb)
    
* [winston-elast](https://github.com/winstonjs/winston-daily-rotate-file)[icsearch](https://www.npmjs.com/package/winston-syslog)
    

### **What are formats** [](https://github.com/winstonjs/winston-daily-rotate-file)**in Winston Logger?**

In Winston Logger , Formats allow developers to customize how log messages are formatted before being outputted by the logger. Formats can include timestamp, log level, message, metadata, and any custom formats to tailor the appearance of log messages to their specific requirements. For example,

```javascript
const customFormat = winston.format.printf(({ level, message, timestamp }) => {
  return `${timestamp} [${level}]: ${message}`;
});
```

Here's an example of configuring Winston :

```javascript
const winston = require('winston');

const customLevels = {
  levels: {
    error: 0,
    warn: 1,
    info: 2,
    debug: 3
  },
  colors: {
    error: 'red',
    warn: 'yellow',
    info: 'green',
    debug: 'blue'
  }
};

const customFormat = winston.format.printf(({ level, message, timestamp }) => {
  return `${timestamp} [${level}]: ${message}`;
});

winston.addColors(customLevels.colors);

const logger = winston.createLogger({
  level: 'info', // Default log level
  levels: customLevels.levels,
  format: winston.format.combine(
    winston.format.timestamp(),
    customFormat
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logfile.log' })
  ]
});

module.exports = logger;
```

> 📝 **Note**: With the default log level set to 'info', messages with a severity level of 'info' or higher (e.g., 'warn', 'error') will be logged. Messages with a lower severity level (e.g., 'debug') will not be logged by default.

### **Logging Middleware for Express.js**

If you're using Express.js for your Node.js application, you can integrate Winston Logger with middleware to log HTTP requests and responses. Here's how you can configure Winston middleware:

```javascript
const expressWinston = require('express-winston');

app.use(expressWinston.logger({
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'requests.log' })
  ]
}));
```

### Usage of Winston Logger in a Sample Blog Posting Application:

```javascript

const logger = require('./logger');

function createPost(userId, title, content) {
  logger.info(`User ${userId} created a new post: ${title}`);
}

function updatePost(userId, postId, updatedContent) {
  logger.info(`User ${userId} updated post ${postId}`);
}

function deletePost(userId, postId) {
  logger.warn(`User ${userId} deleted post ${postId}`);
}

function publishPost(userId, postId) {
  if (!postId) {
    logger.error(`User ${userId} attempted to publish a post without specifying a post ID`);
    return;
  }
  logger.info(`User ${userId} published post ${postId}`);st
}
```

### **Rotating Files in Winston:**

In Winston Logger, rotating files refer to a mechanism where log files are automatically rotated or split into multiple files based on certain criteria such as file size, time intervals, or a combination of both. This ensures that log files do not grow indefinitely and consume excessive disk space, while also facilitating log management and analysis.

> Note: For more advanced options and detailed configuration settings for log rotation, you can refer to the official documentation of the [winston-daily-rotate-file](https://www.npmjs.com/package/winston-daily-rotate-file) package.

Here is an example for retaining logs for 14 days before being deleted:

```javascript
const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');

const dailyRotateTransport = new DailyRotateFile({
  filename: 'app-%DATE%.log',
  datePattern: 'YYYY-MM-DD',
  zippedArchive: true,
  maxFiles: '14d' 
});

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    format.timestamp(),
    format.printf(({ timestamp, level, message }) => {
      return `${timestamp} [${level.toUpperCase()}]: ${message}`;
    })
  ),
  transports: [
    dailyRotateTransport,
    new winston.transports.Console() 
  ]
});

module.exports = logger;
```

> 📝Note: Handling Zipped Log Files in Winston Logger
> 
> When using the `winston-daily-rotate-file` package with zipped log archives, it's important to note that the package doesn't automatically handle unzipping of log files before deletion. As a result, zipped log files may remain in the directory even after they are no longer needed.

### **How implementing logging system using Winston transformed our node.js application**

When our Discord application faced issues with requests failing, it often led to our application crashing. it was executed using PM2 (process manager)with the restart option enabled, we encountered a challenge. Whenever the application failed and restarted, the logs would vanish instantly, leaving us clueless about the cause. To address this, we implemented logging using Winston.

We configured it to log to both the console and a file for persistent storage, utilizing file rotation with filenames containing the date for quick access.

Additionally, we set up the system to delete files after a certain period using daily rotate files, preserving memory usage .

### **Here are some best practices for logging in Node.js :**

1. **Use Log Levels**: Utilize different log levels to categorize log messages based on their severity. Common levels include `error`, `warn`, `info`, and `debug`.
    
2. **Include Contextual Information**: Provide timestamps and additional context in log messages to aid in debugging and troubleshooting.
    
    ```javascript
    const winston = require('winston');
    
    const customFormat = winston.format.printf(({ level, message, timestamp }) => {
      return `${timestamp} [${level}]: ${message}`;
    });
    
    const logger = winston.createLogger({
      level: 'info', 
      format: customFormat, 
      transports: [
        new winston.transports.Console(), 
      ]
    });
    ```
    
3. **Centralized Logging Configuration**: Configure logging settings in a centralized location for consistency across the application.
    
    ```javascript
    const logger = require('winston');
    
    logger.configure({
        level: 'info',
        format: winston.format.json(),
        transports: [
            new winston.transports.Console(),
            new winston.transports.File({ filename: 'app.log' })
        ]
    });
    ```
    
4. **Do not log sensitive information:** it's crucial to ensure that sensitive and confidential user information is never included in your log entries, especially in production environments. Not only does this protect users from potential malicious attacks, but it also helps your application comply with data privacy laws and regulations. Sensitive information encompasses personally identifiable data (PII), health records, financial details, passwords, IP addresses, and similar data.
    

> Note: Have a look at the article dedicated to [structured logging](https://reflectoring.io/structured-logging/) if you want to dive deeper.

### **Conclusion**

In this step-by-step guide, we've explored the implementation of Winston Logger in Node.js projects, enabling us to build robust and reliable applications. With best practices like utilizing log levels, including contextual information, and centralizing logging configuration, we've paved the way for more reliable and usable Node.js applications.

Let's embark on our logging journey to enhance our projects further!!