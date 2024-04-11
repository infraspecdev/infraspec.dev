---
title: "Building internal tooling in legacy systems"
authorId: "abhishek"
date: 2024-04-11
draft: false
featured: true
weight: 1
sitemap:
changefreq: 'monthly'
priority: 1
---



This article takes you through what it is like to build an internal tool while dealing with a lot of legacy systems where a lot of tech debts already exist. I have worked on some internal tools during my journey of being a software engineer in companies like Gojek, Swiggy, Vedantu and CRED.
In this article I am going to talk about my experiences in building an internal tool.

## Prelude

### What are internal tools ?

Internal tools are the ones which become a necessity for a tech organization after a period of existence into the business and definitely not needed before the PMF of the product. So the necessity could be dev productivity, pulling up security standards, efficiency in the internal processes etc .

As every organization is a unique combination of different perspectives their systems/patterns also look different from each other at 10000 ft level. Due to these different perspectives they run into unique problems which any off the shelf tools can’t solve.
For e.g you need to build a authorization system for your internal CRM (security enhancement), where you are calling 100s of APIs to get and aggregate the data from multiple backend systems, in this case there will be different contracts, different kind of adoption of HTTP verbs and implementation and trust me you’ll be surprised day on seeing the permutation of variety HTTP that can exist in the system. After considering these ground realities organizations decide to build an internal tool which solves the problem and also fits in the processes.


## Horizontal cutting
These kinds of problems are going to impact a lot of internal users from operations to engineers, there are going to be multiple key stakeholders from impact and collaboration point of view. What you are going to deal with is legacy and a process which is already adopted by the organization.

## Ownership
These are going to be legacy systems/processes and your job is to build a tool to solve it, as this is going to be mostly processes which are leaky and tech debts, it's highly likely you are not going to have shared ownership between product manager/programme manager/engineer.


## Discovery
As I said this is post PMF phase, most organizations miss out that these problems are going to hit you once you scale your product while they are majorly focussing on the growth of the business. So think about the problem which is compounding with time and suddenly gets prioritized while being on the back burner since the org existed. Most likely there would be no single person whom you can interview to understand all the use cases and problem statement. It’s going to be a fuzzy and blurred space which you have to navigate.


## Collaboration
Now that you have identified the problem statement and a solution, there are going to be situations where your solution is dependent on other teams and has some past context and history. Software is already a high collaborative work but in this case it might become a bottleneck for you.

## Execution
From an engineering point of view you are going to deal with a lot of tech debts, where it’s hard to navigate while executing the project, and you might end up breaking the existing systems or add more to the tech debts.

## Adoption
Adoption is going to be the toughest and most frictional part of the whole process where you need to move people from the existing process to the solution which you have built. You're definitely going to uncover something which you missed out in the analysis. As most of your users mostly won’t be having any incentive to move to a new tool, and it is going to take a lot of convincing for them to move.


This is more or less the nature of work and what are some key problems you are going to face while building and rolling out an internal tool. As an engineer you need to operate in a certain way to overcome this problem as the problem space is dynamic and full of constraints which you can’t break.

Every system and process has flaws, and you need to be understanding and be patient while dealing with this as the organization has scaled to a certain level with the current systems and the processes around it. Nobody wants to do bad work but while the focus was on growth leadership was not able to prioritize and fix the gaps. Now that you are owning the problem statement organization has put faith in you to do the right thing. So think from an open mind and understand the constraint and situation of all the people who are using and maintaining those systems. This will help you to be calm as you are going to deal with a lot of unknowns and be comfortable in uncomfortable situations. One time while putting a code patch we encountered a JS file with more than 12k lines of code, we wanted to write tests for the patch we have put in but gave up after days of effort as the code dependency was quite huge and tightly coupled with the system. We had to give up on the discipline which we follow to make progress and such instances are going to be normal.


This is about ownership and there are going to be multiple key touch points it’s hard to build these systems in silos and show outcome one fine day. To get you unblocked, figure out the key sponsor of the project in the leadership team who has vested interest in getting this product shipped. This will help you put some weight in the places where you are struggling to prioritize your requirements and get yourself unblocked.

Make sure you keep producing artifacts during your journey of discovery, execution and roll out of the product. This encompasses the current state of the system and how it is getting used, use cases and the persona of the colleagues who are using the system in the discovery phase. While we were building a tool for enhanced security on an internal CRM portal this is definitely going to mask/abstract information from the users(operations) as there is going to be some personal information of the customer which is visible on that portal that is not needed to be accessed by everyone. What we did was identify the persona on what kind of role (customer-support/payment-operations etc) needs what kind of access and from here we started building up requirements. This stands true for design documents, rollout plan, rollback plans too. You are going to interview a lot of people during the whole process, document everything as carrying and sharing this much context without documents is not possible.


You need to have a collaborative first mindset to tackle execution, you will end up picking changes in the systems which are outside your purview, understand the codebase and introduce the changes. You’ll have to collaborate very closely with the teams who own the current systems. Hacky mindset is something this space will demand as you are going to migrate from the current systems to the new ones. You might end up building some custom router/gateway plugins etc to achieve what you want. As the scale and impact is high, always keep in mind to have a rollback even for the slightest change.

Adoption is the biggest beast in this whole journey which is very hard to tame and you are going to face a lot of problems in adoption and onboarding as it needs change in the mindset and people have to work with constraints of the new systems. You need to think like a sales person here and sell the outcome and benefits of the new system. Take the ownership of onboarding and  can you automate the onboarding process which will bring down the entry barrier significantly. Take some sessions for the users of the new systems on how to use the new systems and what is supported and what is in the roadmap, make them believe in your vision and what the future looks like. Like when we migrated from VMs to kubernetes for all the deployments in Gojek, we took multiple sessions on how the new deployment platform works, how do you debug the failures, how logs are getting shipped etc. This is the place where you show off the capabilities of the new systems over the legacy and how easy it is for users to leverage the new system. Share documentation, demo videos and try to evangelize the adoption as much as you can.



## Conclusion
This problem space is quite exciting and lets you wear a different hat at different points in the journey like product, programme manager, engineer, sales etc. It’s quite important for the success of the project that the system is forward looking and will work for the organization for at least next 2-3 years. Understanding the needs of your stakeholders, sponsor of the project and what’s the right product to solve for the current issues is very crucial for success of the project. There might be situations where every stakeholder has different needs but it’s your job as an engineer to do the right thing.


