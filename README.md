# FBMS

Download your Facebook messages!

# Help, what is this?
Have you ever wanted to download your Facebook messages from a certain thread? Or maybe find out how messages you and your friend have sent each other? Or perhaps who sends the most spam in a group chat? I did, and didn't find any sensible way to do so, so here it is!

# Hmm, do I need a bunch of weird programs to run this?
No! Well... You need some, but they're not weird!

* Python 3
* [Requests](https://pypi.python.org/pypi/requests)

# Ah, cool! So how do I use it?
Right now you need to open the developer tools in your browser och capture one of your browser's requests to thread_info.php on Facebook. Then copy the cookie as well as other details as specified in config.py *into* config.py. 

Then you can run the script in it's most basic form with `python3 fbms.py <conversation id> <amount>`.

Here, *conversation id* is the ID of the conversation you wish to download. This is not the other person's username, but rather their Facebook ID. You can easily find this using the techniques listed when you google something along the lines of "how to find facebook id". You can also see it using the developer tools as mentioned above. The *amount* can be either `-n N` or `--number N`, where N is the number of messages to process, or `--all`, meaning all messages (surprise!).

If you're downloading a group chat, then you also need the `-g` (or `--group`) option, as group messages are handled slightly different than private ones.

# I got the basics. Now give me the advanced stuff!
If you run fbms with the `-h` option, it will print out a help message describing all the available options. But since I'm feeling helpful, I'll describe them here as well.

* `--group` or `-g` Download a group conversation.
* `-n N` or `--number N` Specify the number of messages to process.
* `--all` Process all messages.
* `--hard` Process **exactly** N messages. Wait, what? Due to the way the messages are retrieved from Facebook, more than N messages are usually fetched. The default behavior is to just include these extra messages in the output, but if you really need **exactly** N messages, then `--hard` will not include the superfluous ones.
* `--file FILE` Save the messages to the file FILE instead of just printing them to stdout.
* `--user-message-count` or `--umc` Count and display the number of messages that each user in the conversation has sent.
* `--quiet` or `-q` Don't print messages to stdout. This is most useful when used together with options providing additinal processing such as `--user-message-count`.
