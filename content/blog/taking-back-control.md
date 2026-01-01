---
title: "Taking Back Control: Observability as Reclaiming Agency"
authorIds: ["nimisha"]
date: 2026-01-01
draft: false
featured: false
weight: 1
---

The story of every growing system is fundamentally a story about losing and
regaining control.

## Act I: The Illusion of Control

When the product is still in its inception and the team consists of a couple of engineers,
If there is a CTO (at that point in the product's journey) who is programming and
contributing to building systems.The team is in tight control of what is happening,
The context is small enough that everyone knows every endpoint, every query and
integration that exists.

Most likely, everything that is getting shipped and there is no environment
segregation and code moves from the engineer's development machine to production
directly. If something breaks, engineers are aware where and what is breaking, and
the team can reproduce them locally quickly and fix. Everyone knows what's changed,
who changed it and breaking production and quickly fixing it has become the way
team works. This is what control is, and it's natural because the system is still
in the engineer's cognitive capacity.

This creates a dangerous illusion: you believe control comes from your knowledge
of the code. But it doesn't. Control is coming from the context being small and tight communications.

## Act II: The Gradual Loss

Control doesn't disappear suddenly. It erodes gradually, almost imperceptibly:

### Week 1

It'sla 2-person engineering team. You have to optimise some API response
time, and as a default strategy for faster read operations teams add a
caching layer. There is a new thing you have to worry about when the
request is being served from cache and which one from the database.
The team has to figure out what's the right cache eviction strategy and
when to update it.

### Month 2

The product is doing well, and there is good traction in the market
and now your response time is critical for you. Immediately you figure
out there is an operation happening in the customer facing flow which can be
moved async, team jumped on this action and slashed your response time by
30 percent. Team is happy, and the engineering team is getting good recognition
with so less turn around time. It was a big win. But we can't trace the
end-to-end request easily but that concern is pushed for later.

### Month 4

The product team wants to take data based decisions and the roadmap is evolving
towards experimentations, AB testing and more mature data-driven product
decisions. For now engineering team adds a second database to unblocks the
analytics team and data is in two places and consistency is questionable, but
this question goes under the carpet until it breaks

### Month 9

Your team has grown and the engineering team has around 20 people now.A single codebase
is getting hard to manage, and as the codebase grows, architecture choices are becoming
a bottle neck now. There are incidents every now and then but the product has
good traction and customers really love it. This keeps fuelling the team energy
and everyone is very close to the customer and trying to solve for them.
CTO takes a call of reachitecting the systems while it is easy to change
to enable the next phase of growth. Tech team decides to go towards the microservices
route and identifies 5 services, 3 databases, and messages queues with multiple
deployment regions.

### Month 12

Team jumps in this, product development is halted because of this overhaul, and
achieves this goal within 8 weeks as the team ends up copy pasting most of the things
as timeline is tight. This goes to staging and is put under test. A lot of bugs and
issues are reported but engineers figure it out and pushes the fix quickly by
reading mostly logs on a single machine on staging.

This goes to production but the reality is completely different from what the
leadership has imagined. Uptime is a complex metric to come up with with so
many systems in place. It's a distributed environment now. There are lot of
issues coming up, while the team wants to maintain the delivery speed.
No engineer has all the context which was normal 6 months back. Their deployment
breaks, contracts breaks often because the task which was simple sometime back
now involves dependency of the context with other teams and availability.

Incidents have become scarier, because you have grown on the business
front and your customers expects more maturity from you. But every incident
is like running in the dark as most of the time you are getting this information
as an escalation from your operations or customers. Team is all reactive, running
on manual checks of hitting production APIs to figure out whether the systems
are working fine. More customers also means more escalations, your engineering
bandwidth goes into fixing these issues most of the time. Engineers are pulling
all-nighters and still things just looks out of control.

## Act III: The False Solutions

Teams try different approaches to regain control:

**Let's document everything** : You write architecture diagrams, API specs,
and deployment runbooks. They're outdated within weeks. Documentation describes
what the system should be, not what it is.

**Let's hire tech operations**: There will be a dedicated team who will keep
an extra eye on your systems manually from cloud to customer tickets and report
the issues back to the engineering team. This creates a false illusion that
we'll figure out the issue before our customer.

**Let's be more careful**: You add approval gates, slow down deployments, review
every change. You've gained caution, not control. You're still operating blind
just more slowly.

**Let's assign experts**: You designate "the person who understands the auth service"
and "the person who knows the database." You've created knowledge silos. When
they're unavailable, you're stuck.

None of these are bad practices. But none of them restores your ability to
understand what the system is actually doing right now.

## Act IV: Understanding Control

Here's the realization: you can't control what you can't see.
Control isn't about preventing all problems that's impossible in complex systems.
Control means:

1. Knowing what's happening: When something goes wrong, you can see what actually
failed, not a guess
2. Understanding why: You can trace cause and effect across the system
3. Predicting what's next: You can see trends before they become crises
4. Acting with confidence: You can make changes knowing you'll see their actual
impact.
5. Reduced bus factor: You are not dependent on just a couple of engineers to really
understand what's going wrong.

## Act V: Observability as Agency

Observability is about taking back control. But it's not about returning to the
simplicity you had, it's about scaling your understanding to match your system's
complexity.

![Complexity vs Control](/images/blog/taking-back-control/complexity-control-image.png)

### Scenario: Regaining Control of Deployment

With observability: You deploy a change. You immediately see:

- Request latency for the affected endpoints: no change
- Error rates: flat at baseline
- Database query times: unchanged
- Resource utilization: normal
- User-facing metrics: stable

You know it's working. You're in control.

### Scenario: Regaining Control of Incidents

User reports checkout is broken. You check the checkout service, It's running.
You check logs, no errors. You check the database, it's up. You're 20 minutes in
and still don't know what's wrong. User is waiting. Pressure mounts.

With observability: User reports checkout is broken. You pull up their trace.
You see:

- Checkout service called payment gateway
- Payment gateway response time: 30 seconds (normally 200ms)
- Gateway returned 503
- This started 15 minutes ago, affecting 12% of checkouts
- Only affecting users in the EU region

  You understand the problem in 60 seconds. You're in control of the investigation.

### Scenario: Regaining Control of Growth

Without observability: Your system has been running fine for months. Suddenly,
during a peak traffic event, everything falls apart. Database maxes out. Services
crash. You spend hours firefighting. Post-mortem question: "How did we not see
this coming?"

With observability: You see database connection usage trending upward over 8 weeks:
40% → 55% → 70% → 85%. Traffic projections suggest you'll hit 100% in two
weeks during your product launch. You proactively optimize connection usage and
plan for scaling. Launch goes smoothly.

## The Empowerment

Here's what makes this powerful: observability doesn't just help you react it
changes what you can do.

With proper observability, you can:

**Deploy with confidence**: You're not hoping changes work, you're measuring
their actual impact and can roll back immediately if needed.

**Debug efficiently**: Investigation time drops from hours to minutes because
you have the data to understand what happened.

**Optimize strategically**: You're not guessing which optimizations matter;
You're measuring actual bottlenecks and their impact.

**Scale proactively**: You're not reacting to outages; you're seeing capacity
limits before you hit them.

**Experiment safely**: You can try new approaches and measure their real-world
impact, not theoretical benefits.

This is an agency. You're not at the mercy of your system's complexity.
You've built the visibility to understand it, predict it, and shape it.

Observability is the ability to maintain agency over increasingly complex systems.
It's how you ensure that growth doesn't mean loss of understanding.
It's how you prove to yourself, your team, your users that you're in control.
