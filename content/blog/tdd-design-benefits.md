---
title: "How TDD helps design and build better software?"
authorId: "chetan"
date: 2023-01-18
draft: false
featured: true
weight: 1
---

Most of us think of TDD as a tool for software testing and verification. But if used effectively it is more than that.

Since Test Drive Development (TDD) was introduced by Kent Beck it has always been a bit of a controversial topic. Today we are going to explore what TDD has to offer apart from being a way to test and verify software. Before we dig deeper, let's take a look back at what is TDD, in the first place.

> TDD is a process used to build software in which unit tests are written even before writing any code.

As defined above, we write unit tests even before we write the code. This might sound counterintuitive as to how can we test something before it even exists.
To make this easier to understand, try to think of it like this. It is not testing but stating what you expect the code to do. With this, you are trying to put your expectation before writing the code.
This shift in mindset, helps you be very clear and concise about what you want and how you want your software to behave.

Since we don't have any code to test, this inversion of thought process and development style now poses a few interesting questions:

1. What do we expect from the function and how do we want it to behave?
1. What should be the function/method name? What would make sense from the caller's perspective?
1. What would be the Class name in the case of Object Oriented language?
1. What does the function need as dependencies for it to perform its task?

Let's see how these questions help us one by one

### Q1: What do we expect from the function and how do we want it to behave?

Answering this question helps us to focus on the exact intended outcome before implementing the code. 
This enables us to break the problem statement into smaller chunks as we need to test for each expectation separately. 
This helps us build the software incrementally, and discover edge cases by asking how should it work for weird input values.

### Q2: What should be the function name? What would make sense from the consumer perspective?

Since we would be having the consumer of the function even before it is implemented, it forces us to think of a good function name.
This helps us in understanding how different pieces of code will use this new function.
This significantly improves readability and guides us to arrive at meaningful names.

### Q3: What would be the Class name in case of Object Oriented language?

Naming as we all know is one of the hardest things for software engineers.
One thing I have realised over the years is naming in a meaningful manner only takes iterations.
But one easy way to get started in the right direction is to name things from the consumer's point of view.
What this means is when we start to think from the consumer's point of view, it starts becoming clear as to how it could be used.
And test cases are the first consumers of the code.
This like the previous one helps us improve readability ad arrive at meaningful class names.

### Q4: What does the function/class need as dependencies for it to perform the task?

When we write code, we sometimes expect certain things to be present or need to be passed in for the new code to work.
This helps us understand how complicated the code setup could be if it needs a lot of things.
This acts as an indicator and surfaces tight coupling if any early on in the development lifecycle.
We could consider this as a tool which would prevent the design of the system from having high coupling and reduce complexity.

> TDD is not just about having tests but a lot more than that. It not only helps us verify the correctness of the software but if practised well, helps us design the software well. This is why I sometimes think of TDD as **Test Driven Design**

All of this sounds too good, but it's easier said than done.
Here is one of the many reasons why people are not able to successfully adopt this practice into their development lifecycle.

Not treating this as any other skill and not giving it enough time.
Like any other skill, TDD is also a skill which needs some learning.
But what I have observed is people don't give it enough time or practice it enough to be able to master this skill.
This leads to some of the most obvious pushback of it taking longer than just writing code.
We are going to be slow in anything we don't know, not just TDD.
Only spending enough time with any skill will make us move faster.
Be it learning a new programming language, playing a new musical instrument or learning to drive.

> To conclude, TDD could be used to improve the overall design of the system instead of just using it to increase code coverage.
