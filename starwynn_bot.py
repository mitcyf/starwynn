import discord
import starwynn_tracker as tracker

verbose = True
tracker.verbose = False

file = open('bot_token.txt','r')
BOT_TOKEN = file.read()
file.close()

print(BOT_TOKEN)

intents = discord.Intents.default()

client = discord.Client(intents = intents)

@client.event
async def on_ready():
    if verbose:
        print(f'{client.user} has connected to discord')

client.run(BOT_TOKEN)


if __name__ == "__main__":
    esi_tracker = tracker.Tracker("sky", "ESI")