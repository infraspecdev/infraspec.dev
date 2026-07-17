---
title: "Everything in Linux Is a File... Except When It Isn't"
authorIds: ["venkidesh"]
date: 2024-06-21
draft: false
featured: true
weight: 1
---
This is a simple story about a famous Linux saying — and where it stops being true.

## The Famous Saying

If you've used Linux for more than five minutes, you've probably heard this line:

**"In Linux, everything is a file."**

It sounds like a magic rule. Your hard disk? A file. Your keyboard? A file. A running program? Also a file, somehow.

Here's what it actually means: Linux lets you use the same four simple actions — **open, read, write, close** — on almost anything. You don't need to learn a new set of commands for your disk, and a different set for your printer, and another for your network card. Learn those four actions once, and you can talk to a huge part of the computer.

That idea is old — it comes from the very first version of Unix, the operating system Linux is based on. The people who built it made a smart choice: instead of giving every device its own special controls, give everything a name (like a file name) and let you open, read, write, and close it, just like a text file.

![Linux File Abstraction](/static/images/blog/everything-in-linux-is-a-file-except-when-it-isnt/unified-file-interface.jpeg)

## Where the Trick Really Works

Let's look at `/dev`, a folder full of "files" that are actually devices in disguise.

```bash
$ ls -la /dev/null /dev/sda
crw-rw-rw- 1 root root 1, 3   /dev/null
brw-rw---- 1 root disk 8, 0   /dev/sda
```

`/dev/null` looks like a file, but it's really a doorway into the kernel — anything you send there just disappears.

```bash
echo "bye bye" > /dev/null      # gone forever
```

`/dev/sda` looks like a file too, but it's actually your entire hard disk. You can copy your whole disk with one command, because to Linux, a disk is just another "file" you can read from.

```bash
dd if=/dev/sda of=backup.img bs=4M   # copies the whole disk
```

Now here's where it gets fun. Linux also has folders that aren't real files at all — they're more like windows into the running system, created fresh every time you look.

![VFS Directory Overview](/static/images/blog/everything-in-linux-is-a-file-except-when-it-isnt/vfs-directory-overview.jpeg)

For example, `/proc` shows you live information about every running program:

```bash
$ cat /proc/1234/status | head -3
Name:   nginx
State:  S (sleeping)
```

Nothing here is saved on disk. The moment you look, Linux quickly builds the answer and shows it to you. Close it, and it's gone — because there was nothing really "there" to begin with. It just *looks* like a file.

Pipes work the same trick in a different way. A pipe lets two programs talk to each other:

```bash
$ mkfifo /tmp/mypipe
$ echo "hello" > /tmp/mypipe &
$ cat /tmp/mypipe
hello
```

No data is stored anywhere. It's just a meeting point with a filename, so two programs can find each other easily.

Even some network connections show up as files. Look at this:

```bash
$ ls -la /run/docker.sock
srwxr-xr-x 1 root docker 0 /run/docker.sock
```

That's a socket — a live connection point — but it has a name, sits in a folder, and shows up in `ls`, just like a file.

At this point, the saying feels true. Disks, trash bins, running programs, connections between apps — they all pretend to be files.

## Where the Saying Breaks Down

Now here's the twist nobody tells you: **a lot of Linux is NOT actually a file.**

**Network connections (like visiting a website) don't use files at all.** To connect to a website, a program doesn't "open" a file. It uses totally different commands: `socket()`, `connect()`. A network connection is described by four numbers — your address, your port, their address, their port — not a file name.

```bash
$ ss -tn
State    Local Address:Port    Peer Address:Port
ESTAB    10.0.0.5:22            10.0.0.9:51422
```

No file path anywhere in sight.

**Your network card is only half pretending.** You can look at info about it under `/sys`, like a file:

```bash
$ ls /sys/class/net/eth0/
address  mtu  operstate  speed
```

But to actually *change* something — like giving it a new IP address — you don't write to a file. You use a separate tool (`ip addr add`) that talks to the kernel a completely different way.

**Sending a signal to stop a program isn't done with files either.** Even though each running program shows up in `/proc`, stopping it uses a command called `kill()` — not writing "stop" into some file.

**A program's own memory isn't accessed like a file, from the inside.** There's a way to *peek* at another program's memory from outside (mostly used by debugging tools), but the program itself just uses regular memory, no files involved.

**The settings a program starts with also skip files completely.** They're just handed to the program directly when it starts — never written to or read from a file, by anyone, ever.

![VFS Directory Overview](/static/images/blog/everything-in-linux-is-a-file-except-when-it-isnt/not-everything-is-file.jpeg)

## So What's Actually True?

The real rule is simpler than the saying makes it sound:

**Linux uses the "everything is a file" trick whenever it makes life easier. And it drops the trick the moment it would make things harder instead.**

That's not Linux breaking a promise. It's just good engineering. Some things — disks, settings, running programs — fit nicely into the file idea, so Linux uses it. Other things — like network connections or sending signals — don't fit well, so Linux built separate, better tools for those instead of forcing a bad fit.

```bash
# Where the "file" trick works great:
cat /proc/cpuinfo
dd if=/dev/zero of=swapfile bs=1M count=512

# Where Linux uses something else instead:
socket(AF_INET, SOCK_STREAM, 0)   # for network connections
kill(pid, SIGTERM)                # for stopping a program
```

## The Takeaway

"Everything is a file" isn't a strict rule — it's more like a favorite trick that Linux uses a lot, but not everywhere. The real skill of Linux's designers wasn't making the trick work everywhere. It was knowing exactly when to use it, and when to build something new instead.
