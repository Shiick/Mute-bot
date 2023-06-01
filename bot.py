import discord, json, time, os
from discord import app_commands
from discord.ext import tasks

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

GUILD_ID = 0000 # Discord server id, right click on the server / "Copy Server ID"
MUTED_ROLE_ID = 0000 # muted role id, right click on the role / "Copy Role ID"
CHECK_TIMING = 5 # how often the bot checks for users, set it low to avoid too much error on the length of the mute.

TOKEN = "DISCORD-BOT-TOKEN" # Discord bot token

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    if not os.path.exists("muted_list.json"): # make sure the storage file exists
        data = {}
        with open("muted_list.json", "w") as f:
            json.dump(data, f)
    print("Bot is running.")
    check_mutes.start() # start checking

@tasks.loop(seconds = CHECK_TIMING)
async def check_mutes(): 
    with open("muted_list.json", "r+") as f:
        data = json.load(f)
        for user in data: # for each muted users in muted_list.json
            reduce_user_time_left(user, CHECK_TIMING)

@tree.command(name="mute", description="Mute specified user", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="The user to mute", duration="The length of the mute (in hours)")
@app_commands.rename(user="user", duration="duration")
@app_commands.checks.has_permissions(manage_roles=True)
async def mute_command(interaction, user: discord.Member, duration: int):
    muted_role = client.get_guild(GUILD_ID).get_role(MUTED_ROLE_ID) # get role
    user = await client.get_guild(GUILD_ID).fetch_member(user.id)  # get target user
    if (muted_role not in user.roles): # if is not muted
        await user.add_roles(muted_role) # add role
        duration_in_seconds = duration*60*60
        expiration = int(time.time()) + duration_in_seconds
        add_user_to_muted_list(user.id, duration_in_seconds)
        await interaction.response.send_message("<@" + str(user.id) + "> is muted until <t:" + str(expiration) + ">.")
    else:
        await interaction.response.send_message("<@" + str(user.id) + "> is already muted.")

@tree.command(name="unmute", description="Unmute specified user", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="The user to unmute")
@app_commands.rename(user="user")
@app_commands.checks.has_permissions(manage_roles=True)
async def unmute_command(interaction, user: discord.Member):
    muted_role = client.get_guild(GUILD_ID).get_role(MUTED_ROLE_ID) # get role
    if (muted_role in user.roles):
        await unmute_user(user.id)
        await interaction.response.send_message("<@" + str(user.id) + "> is now unmuted.")
    else:
        await interaction.response.send_message("<@" + str(user.id) + "> is not muted.")

async def unmute_user(user_id):
    muted_role = client.get_guild(GUILD_ID).get_role(MUTED_ROLE_ID) # get role
    user = await client.get_guild(GUILD_ID).fetch_member(user_id)  # get user
    await user.remove_roles(muted_role)  # remove role
    remove_user_from_muted_list(user_id)

def add_user_to_muted_list(user, duration):
    dict = {
        "time_left": duration
    }
    with open("muted_list.json", "r+") as f: # write the user at the end of the json file
        data = json.load(f)
        data[user] = dict
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=4)

def remove_user_from_muted_list(user): 
    with open("muted_list.json", "r+") as f: # load data, remove the user, set the file content to the update data
        data = json.load(f)
        del data[str(user)]
        f.close()
    json_data = json.dumps(data, indent=4)
    with open("muted_list.json", "w") as f:
        f.write(json_data)

def reduce_user_time_left(user, amount):
    with open("muted_list.json", "r+") as f: # load data, change time_left, then set the file content back
        data = json.load(f)
        data[user]["time_left"] = data[user]["time_left"] - amount
        f.close()
    json_data = json.dumps(data, indent=4)
    with open("muted_list.json", "w") as f:
        f.write(json_data)
    if (data[user]["time_left"] <= 0): # if the time has reached 0, or below, unmute the user
        client.loop.create_task(unmute_user(user))

client.run(TOKEN)