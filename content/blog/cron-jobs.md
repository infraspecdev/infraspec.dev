---
title: "Boost Your Productivity with Cron Jobs: What You Need to Know"
authorId: "shivani"
date: 2024-04-15
draft: false
featured: true
weight: 1
---

___
<img src="/images/blog/cron-jobs/cron-jobs-cover.png" alt="Cron Jobs cover" width="100%">

## **So, what are Cron Jobs?**

Before crons, managing repetitive tasks was like being a chef juggling multiple pans on a hot stove, constantly checking and flipping without any help - exhausting and prone to mishaps!

But then came crons, the kitchen timer of the digital world! Just like how a chef can set a timer and walk away, crons are like your trusty digital sous chef, taking care of business while you sip your coffee. Cron jobs are scheduled tasks that run at predefined intervals on Unix-like operating systems. They are commonly used to automate repetitive tasks such as backups, maintenance, and report generation.

## **What is Crontab File?**

Crontab, short for "cron table," is a text file that outlines the schedule for cron jobs. There are two main types of crontab files: system-wide crontab files and individual user crontab files.

Cron is commonly pre-installed by default in all Linux distributions. Otherwise, run the installation command according to your package manager. Here’s the command for **Ubuntu** with **apt:**`sudo apt install cron`

Individual user crontab files are named after the respective user and their storage location varies based on the operating system. For example, in Red Hat-based distributions like CentOS, these files reside in the `/var/spool/cron` directory while in Debian and Ubuntu systems, they are stored in the `/var/spool/cron/crontabs` directory.

Although it's possible to manually edit user crontab files, it's generally recommended to utilize the crontab command for this purpose.

On the other hand, the `/etc/crontab` file and the scripts within the `/etc/cron.d` directory serve as system-wide crontab files and are typically editable only by system administrators.

## **Crontab Syntax and Operators**

Each line in the user crontab file contains six fields separated by a space followed by the command to be run.

<img src="/images/blog/cron-jobs/cron-expression-syntax.png" alt="Cron Expression syntax" width="100%">

## **Special Characters**

* **Asterisk (\*)**: Represents all possible values for a field.

* **Hyphen (-)**: Specifies a range of values.

* **Comma (,)**: Specifies multiple values.

* **Forward Slash (/)**: Specifies increments.

For example, */10 8-16 * * 1-5 /home/user/scripts/srcipt.sh
This cron expression executes the script `/home/user/scripts/script.sh` every 10 minutes during the hours of 8:00 AM to 4:00 PM, every month, Monday through Friday.

> Note: If you want an easy way to debug cron syntax, there are many online editors such as [crontab.guru](https://crontab.guru/)  that will show you what your schedule expression means in layman terms, i.e. "Every weekday at 3 PM".

## **Predefined Macros**

There are several special Cron schedule macros used to specify common intervals. You can use these shortcuts in place of the five-column date specification.

* `@yearly` (or `@annually`) - Run the specified task once a year at midnight (12:00 am) of the 1st of January. Equivalent to `0 0 1 1 *`.

* `@monthly` - Run the specified task once a month at midnight on the first day of the month. Equivalent to `0 0 1 * *`.

* `@daily` - Run the specified task once a day at midnight. Equivalent to `0 0 * * *`.

* `@weekly` - Run the specified task once a week at midnight on Sunday. Equivalent to `0 0 * * 0`.

* `@reboot` - Run the specified task at the system startup (boot-time).

## **Linux Crontab Command**

The crontab command enables you to manage cron jobs by installing, viewing, or opening a crontab file for editing.

* `crontab -e` - Edit crontab file or create one if it doesn’t already exist.

* `crontab -l` - Display crontab file contents.

* `crontab -r` - Remove your current crontab file.

* `crontab -i` - Remove your current crontab file with a prompt before removal.

* `crontab -u <username>` - Edit other user crontab file. This option requires system administrator privileges.

    For example:

    <img src="/images/blog/cron-jobs/crontab-entry.png" alt="Crontab entry" width="100%">

## **Crontab Variables**

The cron daemon automatically configures several environment variables:

1. The default path is set to `PATH=/usr/bin:/bin`. If your command isn't in this path, you can either use the absolute command path or adjust the cron $PATH variable. Note that you can't implicitly append: $PATH as with regular scripts.

2. The default shell is /bin/sh. To use a different shell, modify the SHELL variable.

3. Cron executes commands from the user's home directory. You can set the HOME variable in the crontab if needed.

4. By default, cron sends email notifications to the crontab owner. However, you can override this behavior by using the MAILTO environment variable, specifying a comma-separated list of email addresses. Setting MAILTO="" will prevent any email notifications from being sent.

    This feature is particularly useful in case a cron job encounters errors; it allows the system to promptly inform the owner or specified recipients about any issues that occurred during the execution of the job.

    For example: Run a script every 5 minutes and redirected the standard output to dev null, only the standard error will be sent to the specified e-mail address:

    `MAILTO=`[`email@example.com`](mailto:email@example.com)

    `*/5 * * * * /path/to/script.sh > /dev/null`

## **Crontab Restrictions**

To control user access to the crontab command, you can utilize the `/etc/cron.deny` and `/etc/cron.allow` files. These files contain lists of usernames, with one username per line.

By default, only the `/etc/cron.deny` file is present and empty, allowing all users to utilize the crontab command. To restrict access for specific users, you can add their usernames to the `/etc/cron.deny` file.

If the `/etc/cron.allow` file exists only the users who are listed in this file can use the `crontab` command.

If neither of the files exists, only the users with administrative privileges can use the `crontab` command.

> Note: For simplifying the process of generating cron job expressions, there's a website called [Crontab Generator](https://crontab-generator.org/).
