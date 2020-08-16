# A Discord bot for Women in Gaming

This bot handles functions within the WiG Discord server. The `master` branch of this repo autodeploys to Heroku, which hosts the bot for free.

## Files
- package.json = Heroku file describing the bot and its dependencies
- Procfile = Specific file for Heroku for deployment
- requirements.txt = All current dependencies used during runtime
- runtime.txt = Specifies the current version of Python

- wig.py = File that currently holds all bot code
- Roles.py = File that holds all commands pertaining to roles

## Deployment
As stated above, any push to the `master` branch will automatically deploy to Heroku and update the bot live. If something goes wrong, the error will be in the Heroku client.

## Commands
The current prefix is "!w "

- setchannel = Currently sets the channel that invite messages will be sent to
- test = Returns wigwigwig, mainly just to check if the bot is online and functional
- helpme = Returns a list of commands and their uses

# Features
- Invite Manager = Automatically detects when someone joins the server and will send a message saying which invite they used and who created said invite
