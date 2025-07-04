---
title: "I Got Destructively Hotdogged"
authorId: "aleric"
date: 2025-04-21
draft: false
featured: true
weight: 1
---

### 1. Pranks We All Know

Pranks among software engineers aren't new, people often leave their machines unlocked, inviting playful hijinks. Some host a party on the company group chat, and some remap aliases. Mostly done for people to understand the risks and to propagate good security practices. But recently, when I returned from grabbing tea and saw this command executing in my home directory:

```
rm -Rf .*
```

I managed to hit Ctrl+C in time, but the damage was done. Most of my dotfiles were gone, fortunately, I still had my `.zshrc` and some others. 

I knew it was going to be a pain to recover from, but I underestimated the pain.

### 2. The Domino Effect

Getting back to work, came my first hurdle.

My terminal did not look and feel the same, thanks to `.oh-my-zsh` directory no longer existing.

After fixing that, new hurdles started showing up:

- My IDE was missing plugins and configuration.
    
- My virtual environments were gone.
    
- Random errors popped up in tools I was using.
    

Each fix revealed another hurdle, making me think **“I hope I don’t find any more surprises…"**.

### 3. Sparking Interesting Conversations

Working in a startup, the news spread fast.

And what began as dotfiles mourning evolved into discussions and planning on how we could harden not just the personal machines but the services and servers in the office.

- Automating server setups with configuration management tools like Ansible.
    
- Scheduling regular syncs to the cloud or local NAS
    
- Hardening the network redundancy we had and a notification system for it.
    

By the end, teammates who had not thought of these things walked out learning something new.

### 4. Lessons Learned

The pain got worse. Ironically, I had been wanting to version control my dotfiles on GitHub for months, but other priorities kept getting in the way. However, this incident made me look back and think about:

1. **Not procrastinating on solutions for known pain points.**
    
2. **Documenting every setup step**, even when it feels tedious.
    
3. **Investing small efforts upfront to save hours later.**
    

### 5. Hope for the Best, Plan for the Worst

Unexpected failures are part of software development (and life). When things go sideways or systems break, the difference between chaos and control is preparation. By building redundancy and easy recovery, the disruptions turn into a short detour rather than a full stop.

Now let me get back to building that redundancy, so the next time someone tries to hotdog my machine, the joke's on them.
