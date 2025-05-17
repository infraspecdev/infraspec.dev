---
title: "Pragmatism Over Perfection"
authorId: "aleric"
date: 2025-04-21
draft: false
featured: true
weight: 1
---

We as Engineers often chase perfection.
It fuels our curiosity, sharpens our skills, and makes us feel good about the things we build. But at the same time, it can be a double-edged sword, sometimes slowing us down or distracting us from what actually matters: **delivering business value**.
That’s where pragmatism comes in.

This is a story about me getting that lesson reinforced with a simple task I was working on: KYC Image Tagging.

## The Problem

We had developed two models to classify KYC signature images as **valid** or **invalid** — one based on a CNN, the other on a Decision Tree.
Once trained, I inferenced both the models on a dataset of around **1.2 lakh images**, they disagreed on about **17%** of them — and the only way to figure out which model was better was to manually tag those conflicting images.
The ops team was ready to help. All we needed now was a simple interface for them to actually do the tagging.

So I got to work exploring image tagging tools.

## Exploring the Right Tools for the Job

We had a couple of requirements for this process:

1. **Security and Access Control:** The signature images were PII, so we needed secure login, proper access control, and audit logs.

2. **Speed over Longevity:** This was going to be mostly a one time activity, and there was some pressure to get this done as soon as possible.

I quickly found a couple of open-source tagging tools available and started evaluating each one so that I could present viable options to the stakeholders. For each, I looked into pros, cons and how to get them up and running securely and so that only the Ops team could access them.

However there were some constraints:

1. **Missing Security Features:** Most open-source tools lacked the security and access controls we needed, at least in their free versions. And buying licenses didn’t make sense for a one-off task, this meant that I would need to somehow implement security and access control.

2. **Time pressure:** The images were ready to be tagged. The stakeholders were waiting. And the Ops team was blocked on me to provide them with an interface. Setting up the infrastructure, securing it, and onboarding users would take time we did not have.

These constraints made the "right" tools impractical for our needs.

## A Hack that Worked

This is when the shift happened. I stepped back and looked at what we already had, and an idea struck.

We were already using Databricks internally to ingest product data and run analytics and modeling jobs. What if it could be turned into a tagging tool?
I pitched the idea to my manager. It was hacky, no doubt, but it was great.
It ticked all our boxes:

1. **Access control was sorted**: Databricks had SSO and RBAC baked in.

2. **Onboarding was simple**: The process was documented and quick.

3. **The KYC images were already available** inside Databricks to people with the right access.

4. **No new infrastructure was needed**: We already had it running, hence saving time, setup overhead, and additional infrastructure costs.

5. **Time to go live was minimal**: I could get the Ops team started almost immediately, contributing to the time saved on the larger goal, model deployment.

My manager signed off, and we presented the options to the stakeholders. They were happy that we could use an existing system to get the job done.
So, we used Databricks as a tagging tool.
It was in no way the "right" tool for the job, but it worked, and that made it the best one.
And now it was time to implement this pragmatic solution.

> What is Databricks?
>
> Databricks is an-all-in one platform for analysts, and engineers to manipulate, process and use data, read more [here](https://www.databricks.com/data-intelligence?scid=7018Y000001f8FIQAY&utm_medium=paid+search&utm_source=google&utm_campaign=20782149301&utm_adgroup=152953302702&utm_content=microsite&utm_offer=data-intelligence&utm_ad=724408738477&utm_term=what%20is%20databricks&gad_source=1&gclid=Cj0KCQjw2ZfABhDBARIsAHFTxGwAa41AMcCUzaTbsL60svmAaD4LReAsmqlwm_SMoJYbKgzcDWwEoGAaAi4wEALw_wcB).

## Getting it up and Running

I onboarded the Ops team onto Databricks and assigned them the right roles, which was quick and easy since I already had admin access.
Then, I created a simple notebook for them.

Here is what the notebook did:

1. Fetched an image path at random from the table we had where the manual tag field was Null.
2. Displayed the image to the user.
3. Asked the user for input.
4. Updated the manual tag field in the table for the image, with the user input, tagging it valid or invalid.

Here are some screenshots of the notebook, it contains some more information:
<img src="/images/blog/pragmatism-over-perfection/Image_tagging_1.png" alt="Databricks Notebook Image 1" />
<img src="/images/blog/pragmatism-over-perfection/Image_tagging_2.png" alt="Databricks Notebook Image 2" />
<img src="/images/blog/pragmatism-over-perfection/Image_tagging_3.png" alt="Databricks Notebook Image 3" />

And after a short walkthrough, the Ops team was off tagging the images.

## The Outcome

Using existing tools enabled us to get started quickly.
It did introduce a few extra steps for the ops team, like running the notebook cells repeatedly, as compared to the right tools. However, the overhead was minimal, within acceptable limits, and the Ops team found the process simple.

The tagging was completed within **3 weeks**, which gave us the clarity we needed on the model performances.
If I had used the “right” tools, the setup alone would have taken about a week.
In the end, this approach saved us **time, effort, complexity and additional costs** while keeping the stakeholders happy.

P.S. The CNN model won.

## The Takeaway

The right tools for the job are great, and I now know which ones to use for tagging images, videos, audio, etc., and what their limitations are. This is valuable knowledge to have, for the future, when a similar problem statement comes along.

But what matters more is **driving business value**.
My solution was pragmatic, and it let us do exactly that, within the constraints we had.
And that is the mindset we, as engineers, need to prioritize.

This doesn’t mean we shouldn’t explore new or better tools; we absolutely should.
But when solving a problem under real-world constraints, you have to ask:
**What kind of solution does this situation really need?**

More often than not, **simple is better**.
