---
title: "DNS Migration"
date: 2022-12-15
draft: false
featured: true
weight: 1
---

DNS plays a crucial role in making the internet easily accessible to us, as it allows us to use domain names instead of having to remember complex IP addresses. Although we as individuals may never need to maintain a highly distributed system like DNS, we may sometimes need to interact with portions of it like the domain management. In this blogpost I will be sharing my experience of one such encounter with DNS - migration of DNS service from GoDaddy to Route53.

Before embarking on the journey of DNS migration, I recommend taking some time to learn more about DNS by exploring the following resources:
1. [What is DNS - Cloudflare](https://www.cloudflare.com/learning/dns/what-is-dns/)
2. [Deep Dive on DNS - IETF](https://www.youtube.com/watch?v=DV0q9s94RL8)
   
Now that you have a basic understanding of DNS, let's examine the reasons for needing to perform a DNS migration.

# Need for DNS migration
>
>  #### NOTE
>  _For the reasons of obscurity, I will be using the domain _**example.com**_ in this blog._
> 
GoDaddy is the registrar for our domain **example.com**. We need this domain for hosting our web application which was served by Nginx on EC2 instances in AWS. The application was load balanced by haproxy setup on another instance in AWS. SSL certificate management was done using some in-house scripts. This setup was quiet simple and we didn't feel a need to look for a dedicated DNS service, so we chose the standard DNS service provided by GoDaddy.

Recently we decided to move to a fully orcestrated environment for our web application using Amazon ECS. With this setup we took decision to let go of Haproxy and use Application load balancer provided by AWS. SSL certificate management is done using Amazon Certificate Manager. With all these decisions and looking at the cost benefits & ease of integration of AWS services with Amazon's own DNS service - Route53, we decided to migrate from GoDaddy's DNS service to Route53.

To summarize, we realised the following benefits of Route53 over GoDaddy DNS service:
1. As we are using AWS for our infrastructure, it is easier for us to integrate Route53 with aother AWS services we are using like integration with application load balancer, automatic SSL certificate renewal by ACM.
2. Route53 provides multiple routing policies based on the percentage of traffic, failover policies etc.
3. Route53 is more reliable and faster DNS service than GoDaddy's without any additional cost.

# Terminology
### Time to live (TTL)
It determines the duration for which each DNS record is valid and therefore how long it takes for updated record to be reflected for users.

### Zonefile
The zone file is a simple txt file that contains mappings between domain names and IP addresses and other resources, organized in the form of text representations of resource records (RR). A sample zonefile can be seen below (source: Wikipedia)
![Sample Zonefile](/images/blog/dns-migration/zonefile_snapshot.jpg)

# Migration Plan
We know that proper DNS setup is important for discovery of any businesses on the internet. So we decided to carve out a migration plan with a rollback plan in case if anything goes wrong with the migration. We identifies few prerequisites before we start with migration.

## Prerequisites
1. Export the zone file from GoDaddy DNS service. Most of the DNS services provide the ability to export the zone file. This will be used for migrating the domain records to Route53. This zone file will also act as the backup in case we need it for reverting the changes. We basically need a list of all the domains/ subdomains to be migrated and zonefile is the easiest way to get it.

2. Reduce the TTL for all the domain records to the least possible value in the GoDaddy DNS service. This will help in reflecting the DNS change at the client side quickly. Also in case of failure during migration this will help in quickly reverting the changes.
>
> #### TIP
> _It was a good opportunity for us to review and remove any unused subdomain records, as this will save us time and avoid potential issues with orphan records in the future._
> 

### Migration Steps
1. The first step in DNS migration is to create the domain entry in the new DNS service. In Route53 this is called Hosted zone.
2. Get all the subdomains from the zone file except the NS and SOA records specific to [example.com](http://example.com). NS and SOA records are created by the DNS service when the domain entry is created. Route53 will create new NS and SOA records for example.com automatically.
3. Add all the subdomains fetched from the zone file in the hosted zone in Route53. This can be done manually using the AWS Console or it can be managed using IaC. 
4. Until this point, we have had our subdomains in both the old and new DNS services, but the old service is still handling queries for example.com. In order to use Route53 as our active DNS service, we need to switch from the old DNS service. 
5. To make the switch we need to replace old nameserver entries in the Domain registrar with the new entries provided by Route53. This is where reducing the TTL will pay off as the switch will not take much time. Keep the old nameservers handy as we may need those in case we need to revert to the old DNS service.

6. To verify if the DNS queries are being resolved by Route53 nameservers, we will use the dig command as follows:

```bash

dig -t NS example.com

```

The response should be a list of Route53 nameservers in the ANSWER section of the response.

7. Also try sending some dummy email to see if MX records have been configured properly.
8. Also try to open up the web application in web browser to check if A records are configured properly.

Post verifying, we can cleanup the records from the GoDaddy DNS service.

# The moment of truth
With the migration plan in place we were pretty confident that the migration will go through smoothly. We were ready with the prerequisites on the D-Day and stated the migration plan.

The Migration plan was going smoothly until **step 6**, but when we attempted to send dummy emails as part of step 7, we were unsuccessful as the recipient was not receiving them. 

# Troubleshooting
The first thing that came to our mind was to check if the MX records in Route53 were configured properly. We could find the MX record needed for the mail server.

Just when we were looking at the records in Route53, we noticed something strange. 
When we copied the records from zone file exported from GoDaddy DNS service, we copied the name of the records as it is. In a lot of DNS services "@" is used to represent apex domain i.e. example.com. We assumed it to be same for Route53 as well and applied the changes. This led to creation of subdomain @.example.com in Route53.

As a result of this all the records types (A, MX and CNAME) with apex domain example.com were not being returned in DNS query answer by Route53.

Later we figured out that in Route53 to create a record with apex domain we need to give the full name of the domain i.e. example.com in the subdomain field or leave it empty.

# Learnings and revised migration plan
Could this issue be prevented? Yes, we could have added additional verification steps to get all the records returned by Route53 using dig and compare those with the records returned by GoDaddy DNS service.

So, we revised our migration plan to include this verification step. The prerequisites remains the same. The complete revised migration steps are mentioned below:
### Revised Migration Steps
1. The first step in DNS migration is to create the domain entry in the new DNS service. In Route53 this is called Hosted zone.
2. Get all the subdomains from the zone file except the NS and SOA records specific to [example.com](http://example.com). NS and SOA records are created by the DNS service when the domain entry is created. Route53 will create new NS and SOA records for example.com automatically.
3. Add all the subdomains fetched from the zone file in the hosted zone in Route53. This can be done manually using the AWS Console or it can be managed using IaC. 
4. <mark>Next, we need to confirm that Route53 will serve all the records that were previously served by the old DNS service. To do that, we need the nameservers for Route53, which are added by default under the [example.com](http://example.com/) hosted zone. Choose one of the nameservers and use the following command to check if all the subdomains are returned. Use this for all record types. The results should match the records in the zone file.</mark>

```bash

dig @ns1.route53-nameserver.com -t MX example.com

```

5. <mark>The command below can also be used to get the difference in records returned by two nameservers. If there is any difference, add/update the records so that there is no difference in response from old and new DNS service.</mark>

```bash

diff <(sort -u <(dig +nocmd +noall +answer +nottlid @ns1.old-nameserver.com example.com ANY)) <(sort -u <(dig +nocmd +noall +answer +nottlid @ns1.new-nameserver.com example.com ANY))

```

6. Until this point, we have had our subdomains in both the old and new DNS services, but the old service is still handling queries for example.com. In order to use Route53 as our active DNS service, we need to switch from the old DNS service. Once we are sure that all the records are being returned by the new DNS service, we are ready to make the switch from the old service to Route53.
7. To make the switch we need to replace old nameserver entries in the Domain registrar with the new entries provided by Route53. This is where reducing the TTL will pay off as the switch will not take much time. Keep the old nameservers handy as we may need those in case we need to revert to the old DNS service.
8. To verify if the DNS queries are being resolved by Route53 nameservers, we will use the dig command as follows:
	
	```bash
	
	dig -t NS example.com
	
	```
	
	The response should be a list of Route53 nameservers in the ANSWER section of the response.
9. Also try sending some dummy email to see if MX records have been configured properly.
10. Also try to open up the web application in web browser to check if A records are configured properly.
11. Post verifying, we can cleanup the records from the GoDaddy DNS service.

### Reverting to old DNS service
Luckily we identified the issue quickly and the fix was not big, so we didn't feel to revert the migration changes. There can be scenarios where it may take time for debugging the issue and the fix may take time. In such cases we can revert to the old DNS service with a simple change, assuming that the records are not cleaned up from old DNS service, we only need to replace the Route53 nameservers with the old service nameservers in the Domain Registrar. This is another place where reducing the TTL values will pay off.

# Conclusion
This post provides an overview of the Domain Name Service (DNS) and its role in keeping us connected. It explains the DNS migration process, including the reasons why it may be needed and the prerequisites for completing the migration. It also includes a detailed step-by-step guide to migrating a domain from GoDaddy DNS service to Route53 and the challanges and learnings during the migration journey.