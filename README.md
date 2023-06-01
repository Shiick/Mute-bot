# Mute-Bot

A Discord bot that unmute users automatically once their punishment ends.

## Commands:
- `/mute <user> <duration>`
- `/unmute <user>`

### How it works:
Every 5 seconds (change this on line 11), the bot will check for all the muted users and remove 5 seconds to their mute duration. Once it hits 0 seconds left, it will unmute the user by itself.

Do not forget to create the muted_list.json file like in the repos otherwise it won't work. (Working on getting a proper way to create it.)

---
*If any help is required, feel free to reach out to [@Shiick](https://twitter.com/Shiick) on Twitter or simply create an issue on the Github page.*