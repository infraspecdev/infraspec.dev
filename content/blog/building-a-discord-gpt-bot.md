---
title: "Building a Discord GPT Bot"
authorId: "nandhitha"
date: 2024-05-31
draft: false
featured: true
weight: 1
sitemap:
changefreq: "monthly"
priority: 1
---

Amidst the excitement surrounding AI, we were eager to delve into this field ourselves. As engineers, we wanted more than just a casual conversation with ChatGPT—we aimed to understand the intricacies of building AI applications.
From the beginning, our goal was clear: to build muscle in this space while creating something practical for daily use that could provide real-world feedback.

We envisioned integrating a ChatGPT-like experience within our messaging platform. Internally, we rely heavily on Discord, which holds a vast amount of information about our daily activities - the mundane, the exciting and everything in between. Incorporating ChatGPT into Discord would allow us to centralize our conversations and potentially develop operational tools around it. Unlike Slack, which has a ready-to-use solution, we couldn't find a seemless Discord ChatGPT integration. This challenge seemed like the perfect project for us.

Thus, our first project was born: building a ChatGPT bot for Discord from scratch.

## Step 1 -Setting up a python virtual environment (optional, but recommended):

- Setup a python virtual environment - why should you this? This warrants a whole conversation by itself. But the tl;dr is that it helps you manage different python versions and project dependencies in a cleaner way.
- I use `conda`. `venv` is a good alternative; regardless of whichever tool you use, remember to install dependencies only inside the virtual environment.

## Step 2 - Create a simple discord bot

- Goto https://www.discord.com/developers
- Click on New Application; provide a name for it (e.g. - infraspec-gpt-bot)
- Navigate to Settings -> Bot and
  - disable `Public Bot` - this restricts the bot from being publicly discovered
  - enable `Message Content Intent`. This allows the bot to read the `message_content` field of a message object
    ![bot-settings](/images/blog/building-a-discord-gpt-bot/bot-settings.png)

### Add bot to your discord server

- Under Scopes, choose `Bot`
  ![oauth2-app-scope](/images/blog/building-a-discord-gpt-bot/oauth2-app-scope.png)
- In the ensuing checklist that opens up, select the necessary bot permissions
  ![oauth2-bot-permissions](/images/blog/building-a-discord-gpt-bot/oauth2-bot-permission.png)
- Open the generated URL in your browser and add the bot to your discord server
  ![add-to-server.png](/images/blog/building-a-discord-gpt-bot/add-to-server.png)

### Coding a Python script to respond

- Install python dependency discord.py with `conda install discord.py`
- Create `main.py` with the following code - this responds only to messages beginning with `$hello` only

```python
import discord
import os

discord_client = discord.Client()

@discord_client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discord_client))

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

discord_client.run(os.getenv('DISCORD_BOT_TOKEN'))
```

- Run the bot

```bash
export DISCORD_BOT_TOKEN=<your-bot-token>
python main.py
```

## Step 3 - Setup OpenAI API keys

Now that we have a basic discord bot placeholder out of the way, let's get onto making it work like chatgpt - for this we use the openAI APIs that have been made available. Before we get onto that though, let us pause here for a minute to understand the difference between chatgpt and openAI. OpenAI is the company that created ChatGPT. ChatGPT is an end user application that is powered by the underlying GPT models (gpt-3.5-turbo, gpt-4, gpt-4o, etc.); whereas the OpenAI APIs allow for us to directly use these models for our usecase. I suspect that ChatGPT might also have been fed some tailored prompts to make it slightly more end user amenable, the open AI APIs allow us to access the models in their more uncensored, raw forms.

Let us create project API keys on platform.openai.com/api-keys. Make a note of the key somewhere secure as it won't be possible to be view it later.
To ensure that the API keys work as expected

```bash
export OPENAI_API_KEY=<your-api-key-here>
```

```bash
curl https://api.openai.com/v1/chat/completions   -H "Content-Type: application/json"   -H "Authorization: Bearer $OPENAI_API_KEY"   -d '{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
    },
    {
      "role": "user",
      "content": "Compose a poem that explains the concept of recursion in programming."
    }
  ]
}'
```

You should see a valid response like below.

```json
{
  "id": "chatcmpl-9UajPtC932k5XPjIelFg6Z2U4jV8g",
  "object": "chat.completion",
  "created": 1717078063,
  "model": "gpt-3.5-turbo-0125",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "In the realm of code, a concept profound,\nLies the technique of recursion, so truly renowned.\nA function calls itself, like echoes in the night,\nUnraveling mysteries, layer by layer, in its sight.\n\nLike a dance of shadows, recursive steps unfold,\nRepeating patterns, a story retold.\nEach iteration a journey, a loop in disguise,\nUnraveling problems, reaching for the skies.\n\nThrough the looking glass of recursive delight,\nWe traverse the depths of code, shining bright.\nA self-referential loop, a loop within a loop,\nA powerful tool, a programmer's scoop.\n\nOh recursion, elegant and grand,\nA concept so beautiful, at our command.\nInfinite possibilities, a journey unknown,\nIn the world of programming, a concept firmly honed."
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 39,
    "completion_tokens": 162,
    "total_tokens": 201
  },
  "system_fingerprint": null
}
```

## Step 4 - Tying it all together

Let's now put it all together. We now have a discord bot and we have openAI API keys working as expected. Let's now build our very own chatgpt, but on discord. At the simplest level, we want to pass on the message from the user to the model and return the API response to the user.

Let's modify the event handler for this - upon receiving a message, we will forward it to the [chat completion](https://platform.openai.com/docs/api-reference/chat) API and relay the API response back on the bot

Install the python openai dependency with `conda install openai`

Your modified event handler should look something like this

```python
import discord
import os

from openai import OpenAI

discord_client = discord.Client()
openAI_client = OpenAI()

GPT_MODEL = 'gpt-3.5-turbo'

@discord_client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discord_client))

@discord_client.event
async def on_message(user_message):
    if user_message.author == discord_client.user:
        return

    completion_response = openAI_client.chat.completions.create(
        model=GPT_MODEL,
        messages=user_message.content
    )
    assistant_message = completion_response.choices[0].message.content
    await user_message.channel.send(assistant_message)

discord_client.run(os.getenv('DISCORD_BOT_TOKEN'))
```

And... voila! A simple discord bot that lets you talk to GPT. The models do not have memory of the past requests and so at present, it just works as a relay layer. But we want more from it. We want to have a conversation with it, and not just use it for one-off fact checking. And to have a conversation, both parties need to be able to retain earlier parts of the conversation (at least within reasonable limits). We humans can do that naturally, but how would GPT do that? For this, we would need to do a little extra to make it 'remember'.

GPT's chat completion API works by treating whatever you pass in the `messages` field of the request as context. It is, by design, allowed to pass (an optional) system message and a series of exchanges between the user and the GPT(assistant). You can use this either for few-shot prompting, or you could also use this to pass relevant bits of the conversation history so that GPT has access to past conversation and can reference that information as needed. Below is a sample of what the `messages` field would look like.

```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "When did the first world war start?"},
    {"role": "assistant", "content": "The First World War, also known as World War I, began on July 28, 1914, and lasted until November 11, 1918. It was a global conflict primarily centered in Europe involving many of the world's great powers at the time."},
    {"role": "user", "content": "Why did it start?"}
    ]
)
```

To help the model remember, add every turn of the conversation to the `messages` list field.

Something to be cognisant of here is that the request has a limit of 4096 token. If the request is larger than 4096 tokens, it would be rejected. Ensure that your request is always under 4096 tokens. The API response also typically tells you how many tokens were used for the prompt and the completion. However, relying only on that to understand your token usage can be expensive. It's recommended to calculate the number of tokens in your request before you send it out. You can use the [tiktoken](https://github.com/openai/tiktoken) library for this.

And what do we do when we exceed the token limit? There are multiple ways you could approach this

- drop off the earliest messages in the conversation - the caveat is that you never know if you might need it
- summarize the conversation to reduce it to one conversational turn - this would incur an additional API call, but it would still retain important information, even if in a condensed form.

Another discord specific challenge we faced was that discord has a character limit of 2000 characters. This meant that we had to check that our user message and API response were within limit and we had to handle for scenarios when they were beyond 2000 characters.

So there you have it! This should hopefully be enough to give you an idea of how to get started. We hope to add more information and guides as we come across them.
