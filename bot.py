import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BLIZZARD_CLIENT_ID = os.getenv('BLIZZARD_CLIENT_ID')
BLIZZARD_CLIENT_SECRET = os.getenv('BLIZZARD_CLIENT_SECRET')
REGION = 'us'
intents = discord.Intents.default()
intents.message_content = True
# Discord bot setup
bot = commands.Bot(command_prefix='!', intents=intents)

import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG to capture all types of log messages
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',  # Define the log message format
    datefmt='%Y-%m-%d %H:%M:%S',  # Define the date format
    filename='bot.log',  # Specify the log file name
    filemode='w'  # Use 'w' to overwrite the log file each time the program runs; use 'a' to append
)


# Function to fetch access token from Blizzard API
def get_access_token():
    url = f'https://{REGION}.battle.net/oauth/token'
    data = {'grant_type': 'client_credentials'}
    try:
        response = requests.post(url, data=data, auth=(BLIZZARD_CLIENT_ID, BLIZZARD_CLIENT_SECRET))
        response.raise_for_status()  # Raise an HTTPError for bad responses
        logging.info('Successfully obtained access token.')
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        logging.error(f'Error obtaining access token: {e}')
        raise  # Re-raise the exception after logging

# Function to fetch character data from Blizzard API
def fetch_character_data(realm, character_name, access_token):
    url = f'https://{REGION}.api.blizzard.com/profile/wow/character/{realm}/{character_name}'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'namespace': 'profile-us', 'locale': 'en_US', 'access_token': access_token}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        logging.info(f'Successfully fetched data for character {character_name} on realm {realm}.')
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching character data: {e}')
        raise  # Re-raise the exception after logging

def fetch_character_professions(realm, character_name, access_token):
    url = f'https://{REGION}.api.blizzard.com/profile/wow/character/{realm}/{character_name}/professions'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'namespace': 'profile-us', 'locale': 'en_US', 'access_token': access_token}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        logging.info(f'Successfully fetched data for character {character_name} on realm {realm}.')
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching character data: {e}')
        raise  # Re-raise the exception after logging

def fetch_character_render(realm, character_name, access_token):
   
    url = f'https://{REGION}.api.blizzard.com/profile/wow/character/{realm}/{character_name}/character-media'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'namespace': 'profile-us', 'locale': 'en_US'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        logging.info(f'Successfully fetched media for character {character_name} on realm {realm}.')
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching character media: {e}')
        raise  # Re-raise the exception after logging


# Discord command to fetch character stats
@bot.command()
async def stats(ctx, realm: str, character_name: str):
    try:
        access_token = get_access_token()
        character_data = fetch_character_data(realm.lower(), character_name.lower(), access_token)
        professions = fetch_character_professions(realm.lower(), character_name.lower(), access_token)
        renders = fetch_character_render(realm.lower(), character_name.lower(), access_token)
        gear_level = character_data.get('equipped_item_level', 'N/A')
        
        charlevel = character_data.get('level', 'N/A')
        charclass = character_data.get('character_class', {}).get('name', 'N/A')
        charrace = character_data.get('race', {}).get('name', 'N/A')
        charfaction = character_data.get('faction', {}).get('name', 'N/A')
        charspec = character_data.get('active_spec', {}).get('name', 'N/A')
        charguild = character_data.get('guild', {}).get('name', 'N/A')
        
        professions = professions.get('primaries', [])
        profession_list = [i['profession'].get('name') for i in professions]
        renders = renders.get('assets', {})
        properrender = renders[1].get('value')
        # Create an embed message
        embed = discord.Embed(
            title=f"{character_name.title()} on {realm.title()}",
            description=(
                f"Faction: {charfaction}\n\n"
                f"**Summary: Level {charlevel} {charrace} {charspec} {charclass}**\n\n"
                f"Gear Level: {gear_level}\n"
                f"Professions: {', '.join(profession_list) if profession_list else 'None'}\n"
                f"Guild: {charguild}\n"
            ),
            color=discord.Color.blue()  # You can choose any color
        )

        # Set the image if the render URL is available
        if properrender:
            embed.set_image(url=properrender)
        else:
            embed.set_footer(text="Render image not available.")

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def races(ctx):
    """Fetch and display a list of playable races from the Blizzard API."""
    try:
        # Fetch the access token
        access_token = get_access_token()

        # Define the endpoint URL and parameters
        url = f'https://{REGION}.api.blizzard.com/data/wow/playable-race/index'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'namespace': 'static-us',
            'locale': 'en_US',
            'access_token': access_token
        }

        # Make the GET request to the Blizzard API
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the JSON response
        data = response.json()
        races = data.get('races', [])

        # Format the response message
        if races:
            race_list = '\n'.join([race['name'] for race in races])
            message = f"**Playable Races in World of Warcraft:**\n{race_list}"
        else:
            message = "No playable races found."

        # Send the response message in Discord
        await ctx.send(message)
        logging.info('Successfully fetched and displayed playable races.')

    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching playable races: {e}"
        await ctx.send(error_message)
        logging.error(error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        await ctx.send(error_message)
        logging.error(error_message)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Run the bot
bot.run(DISCORD_TOKEN)
