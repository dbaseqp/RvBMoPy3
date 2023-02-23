import discord
from discord import app_commands
import concurrent.futures
from time import sleep

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

MAX_THREADS = 3

######################

@tree.command(name = "createbatch", description = "Create a batch of teams") 
@app_commands.describe(number_of_teams = 'How many teams do I make?')
async def build_batch(interaction, number_of_teams: int):
        global statuses
        statuses = dict()
        for i in range(1, number_of_teams+1):
            statuses[f"Team {i}"] = "Scheduled..."
        embed = discord.Embed(color = 16777215, title = "Batch create", description = status_print(statuses))
        await interaction.response.send_message(embed=embed)
        for team in statuses.keys():
            await build_team(interaction, team)
        await update_embed_table(interaction, 'END', 'ALL DONE')


@tree.command(name = "deleteteams", description = "Delete all teams") 
async def delete_all(interaction):
        categories = interaction.guild.categories
        await interaction.response.send_message('Deleting all teams')
        for category in categories:
            name = str(category.name)
            if name.startswith('Team'):
                for channel in category.channels:
                    await channel.delete()
                await category.delete()
                await discord.utils.get(interaction.guild.roles, name=name).delete()
        await interaction.edit_original_response(content='Deleted all teams')


async def update_embed_table(interaction, team, status):
        statuses[team] = status
        embed = discord.Embed(color = 16777215, title = "Batch create", description = status_print(statuses))
        await interaction.edit_original_response(embed=embed)

######################

@tree.command(name = "ping", description = "call and response")
async def ping(interaction):
        await interaction.response.send_message('pong')

@client.event
async def on_ready():
        await tree.sync()
        print("Ready!")

def status_print(statuses):
    ans = ""
    for i in statuses.keys():
        ans += f"{i}: {statuses[i]}\n"
    return ans

async def build_team(i, team):
    await update_embed_table(i, team, 'Starting...')
    green_team = discord.utils.get(i.guild.roles, name="Green Team")
    blue_team = await i.guild.create_role(name = team, colour = discord.Colour.blue())
    category = await i.guild.create_category(name = team, overwrites = {
        i.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        green_team: discord.PermissionOverwrite(read_messages=True),
        blue_team: discord.PermissionOverwrite(read_messages=True)
        })
    await update_embed_table(i, team, 'Adding channels...')
    await category.create_text_channel(team + '-text')
    await category.create_text_channel(team + '-support-requests')
    await category.create_voice_channel(team + '-voice')
    await update_embed_table(i, team, '**Done.**')

client.run("INSERT TOKEN HERE")
