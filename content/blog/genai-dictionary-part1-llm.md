---
title: "GenAI Dictionary - Part 1"
authorId: "nandhitha"
date: 2024-06-21
draft: false
featured: true
weight: 1
sitemap:
changefreq: "monthly"
priority: 1
---

We bring to you this weekly series of articles to help understand and demystify the lexicon in the GenAI space.
Here is part 1 - Large Language Model

## Large Language Model

A Large Language Model(LLM) is a deep learning model that has been trained on a massive amount of textual data, hence the name 'large'. Amongst other capabilities, they can understand and generate text. To put it very very simply - an LLM has been fed enough examples as part of the training to be able to recognise and interpret human languages.

LLM is specifically trained on language data. It's inherent strength is that it has an enhanced 'understanding' of human languages. To be fair, LLMs are incapable of understanding and comprehending language the way humans do. But... what an LLM knows is this - given a stream of text, which word should follow such that it makes the most sense in this context. This it knows by virtue of the vast patterns and contexts it has seen in the training data.

To summarise, LLMs work by predicting the next token based on the patterns it has seen in it's training data. This is what makes up for its conversational abilities.

LLMs are trained on vast amounts of data collected (typically) from the Internet. GPT-3.5 for example has been trained on 17 gigabytes of data from the following sources.

![Screenshot 2024-06-21 at 10.04.30.png](../assets/Screenshot_2024-06-21_at_10.04.30_1718944477521_0.png)

### Tokenization

LLMs break down words into tokens when processing and generating text. A 'token' is the smallest unit of text in the LLM world. A word is made up of 1 or more tokens. A simple rule of thumb - a token can be considered to be approximately 4 characters in length (this is not true all the time, but on average it works out to be this number). Larger words are composed of many small tokens; punctuation marks are separate tokens by themselves.

As an example, consider the following sentence - "Hello! I am a bot". Using the [OpenAI tokenizer](https://platform.openai.com/tokenizer), this text can be broken down into 7 tokens as follows - "Hello", "!", " I", " am", " a ", " bot", "."

![Drawings (1).svg](<../assets/Drawings_(1)_1718950772977_0.svg>)

Now consider a sentence with more complex words - "Renaissance faires are all the rage these days". Using the same [OpenAI tokenizer](https://platform.openai.com/tokenizer), this can be broken down into tokens as "R", "ena", "issance", " f", "aires", " are", " all", " the", " rage", " these", " days", "."

![Drawings (2).svg](<../assets/Drawings_(2)_1718950784608_0.svg>)

Notice how the words "Renaissance" and "faires" are split into multiple tokens?

_But why tokenize?_ Tokenizing helps to represent the original text in a form that the model can process. Every token is mapped to a unique integer ID based on the model's vocabulary. This allows the model to use the tokens to process and generate text.

The exact logic of tokenizing varies across the different tokenizers. So it's important to use the right tokenizer for the chosen LLM. To programatically count the number of tokens, use the [tiktoken](https://github.com/openai/tiktoken) OpenAI tokenizer.
