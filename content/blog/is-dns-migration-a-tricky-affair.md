---
title: "Is DNS migration a tricky affair?"
authorId: "premdeep"
date: 2022-12-15
draft: false
featured: true
weight: 1
---

Never trust a friend who says DNS migration is easy. Your instinct says it's easy, well don't trust your instinct. In this post, I will be sharing my experience with one such encounter with DNS migration from GoDaddy to Route53.

Before starting, if you are here because of the catchy title and have no idea of what DNS is, or you are one of my many (zero) followers or need to brush up your knowledge on DNS, please refer to these resources:

1. [What is DNS - Cloudflare](https://www.cloudflare.com/learning/dns/what-is-dns/)
2. [Deep Dive on DNS - IETF](https://www.youtube.com/watch?v=DV0q9s94RL8)

I won't keep you waiting any longer - I will start my story and explain the reason for my introductory lines.

## Need for DNS migration

One of our clients wanted us to move their workload from Docker Swarm to Amazon ECS. Earlier, they were using HaProxy to load-balance the traffic. This setup also included generation and installation of SSL certificates using in-house scripts, which the client needed to maintain. Since we were moving to ECS, ALB and ACM felt like an obvious choice. In order for ACM to auto-renew expiring SSL certificates, we decided to use Route53 as the DNS service, ditching GoDaddy's DNS service. BTW, if you are curious, the domain was registered with GoDaddy and hence their DNS service.

These decisions landed us onto the supposedly **_EASY_** task of DNS migration. This was my first DNS migration task, and I was equally afraid as I was excited. Just then, I overheard someone (friend/colleague) saying with a very convincing tone that DNS migration is an easy task. Well, I was somewhat convinced. 😅

Still, as a good engineer 🤭, I went ahead and did my research regarding DNS migration and carved out a migration plan.  Looking at the plan for migration, even my instincts were convinced. 

![Instinct calling](/images/blog/is-dns-migration-a-ticky-affair/do_it.gif)

## Migration Plan

Basically I divided the migration plan in three phases along with a rollback strategy:

### Pre-execution phase

In this phase we exported the [zone file](https://en.wikipedia.org/wiki/Zone_file) from GoDaddy DNS service which we will be referring to for the list of domain records to migrate.

Another thing we did was to reduce the [TTL](https://www.cloudflare.com/learning/cdn/glossary/time-to-live-ttl/) of all the records in GoDaddy DNS to the least possible value. These tasks we performed a day before the execution phase. 

Why one day before execution? We looked at the TTL values of all the records and the maximum value we found was 86400 (seconds), which translates to 24 hours. We wanted to let all the clients(browsers) using our application to make the query to the new DNS service as soon we make the switch. For this to happen, it was important to expire the cached results containing information of old DNS service. Since maximum cache duration was 24 hours, we updated TTL to least possible values and waited for old cache to expire.

### Execution Phase

This phase included changes at Route53's end. This included:

1. Addition of hosted zone in Route53 for the [apex domain](https://www.isc.org/blogs/cname-at-the-apex-of-a-zone/)
2. Addition of all the records we have in the zone file to Route53 hosted zone we just created.
3. Update the nameserver records provided by Route53 in the domain registration configuration. This will switch the DNS service to Route53 once the [TTL](https://www.cloudflare.com/learning/cdn/glossary/time-to-live-ttl/) is expired.
We actually used [Terraform](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_record) to add the hosted zone as well as other records, as this would ease up the maintenance of the records.

### Verification Phase

This phase included verification of DNS records of our application and mail servers. One way to verify this is by simply heading to the application domain for verifying the application and sending a mail to the colleague for verifying the working of mail server. This can be considered as a correct way to verify since we have taken care of the TTL but this does not clarify who is serving the records - GoDaddy's DNS service or Route53. To make sure the DNS query result is being served by Route53 nameservers we have to make use of a linux utility called -

![dig](/images/blog/is-dns-migration-a-ticky-affair/dig.gif)

```bash
	$ dig -t NS my-cool-domain.in
```

The output should be similar to this
![dig_ns_output](/images/blog/is-dns-migration-a-ticky-affair/dig_ns_output.png)

The response should have the Route53 nameservers and NOT the GoDaddy DNS nameservers. This validates that all the future queries for our domain/subdomain will be served by Route53.

### Rollback Strategy

There can be scenarios where the migration may go wrong, and it may take time for debugging the issue and the fix may take time. In such cases, we can revert to the old DNS service with a simple change (assuming that the records are not cleaned up from the old service). We only need to replace the Route53 nameservers with the old nameservers in the Domain Registrar.

## D-Day

It was this day (and a few of my colleagues 😝) that compelled me to write this blog.  We proceeded as per our well-thought-out plan (_at-least what we believed it to be_), everything worked well...until the verification phase. We were not able to send/receive emails and the application was down. Furthermore, we verified using **dig** as mentioned in the verification phase, and it was returning the Route53 nameservers as expected. This GIF can express what I was like that day.

![me crying](/images/blog/is-dns-migration-a-ticky-affair/bug.gif)

Others in my team were trying to console me by showing tweets of failed DNS migrations and how common this is. Just kidding!! They were like
![panicing](/images/blog/is-dns-migration-a-ticky-affair/panic.gif)

Well, this is a bit exaggerated.

## Troubleshooting

![troubleshooting](/images/blog/is-dns-migration-a-ticky-affair/troubleshooting.gif)

With the verification using dig, we were sure that migration did happen and DNS had migrated to Route53. This eliminated the chance of issue in nameserver configuration at the domain registrar end. 
Next we moved to Route53 to check the domain records for the email server and application. It was at this point we noticed something unusual.

When we copied the records from the zone file exported from GoDaddy DNS service, we copied the name of the records as it is. In a lot of DNS services "@" is used to represent the apex domain i.e. _my-cool-domain.in_. We assumed it to be the same for Route53 as well and applied the changes. This led to creation of subdomain @.my-cool-domain.in in Route53.

As a result of this, all the record types (A, MX and CNAME) with apex domain my-cool-domain.in were not being returned in DNS query answers by Route53.

Later we figured out that in Route53 to create a record with the apex domain we need to give the full name of the domain i.e. my-cool-domain.in or leave it blank.
Luckily, we identified the issue quickly and the fix was not big, so we fixed the issue instead of reverting. **This is where reducing the TTLs to lower values paid off. The fix was applied within a minute**.

## Further Verification

Since our migration plan failed at the verification phase, we realized that we need to add more verification steps. We realized that we could have verified the records that will be served by Route53 nameservers even before making the switch.  This is made possible by our good old friend - **dig**

```bash

	$ dig @ns1.route53-nameserver.com -t MX my-cool-domain.in
```

This command will return all the MX records for _my-cool-domain.in_ being served by _ns1.route53-nameserver.com_ nameserver. If the record is not present in the response, that would mean that we made some mistake while adding the domain/subdomain in Route53. We can use it to check for other record types as well.

The command below can also be used to get the difference in records returned by two nameservers. This will give us the missing/different records in just a single execution.

```bash

	$ diff <(sort -u <(dig +nocmd +noall +answer +nottlid @ns1.old-nameserver.com example.com ANY)) <(sort -u <(dig +nocmd +noall +answer +nottlid @ns1.new-nameserver.com example.com ANY))

```

Once we are satisfied with this verification, we can comfortably switch the nameserver in domain registrar configuration and continue the verification phase mentioned in the original plan.

With all this successfully completed, we can go ahead and clean up the records from the GoDaddy DNS service.

## What do we learn?

Now, it's time to answer the question - **Is DNS migration a tricky affair?**

Well from my experience, DNS migration seems to be easy if looked from the technical process. All we need to do is follow carefully curated steps and verify the result after every step.

From a business standpoint, DNS migration can prove to be tricky as most of the businesses nowadays use the internet in one form or the other. Losing access to your emails, or your customers unable to access your websites/ applications, can lead to huge financial losses. **So yes, DNS migration can be tricky affairs if executed without careful planning.**

To close this post on a lighter note - I am still looking for that friend/colleague. If you are reading this -

![I_will_find_you](/images/blog/is-dns-migration-a-ticky-affair/i_will_find_you.gif)
