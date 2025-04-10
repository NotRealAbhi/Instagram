# Handlers/Profile.py
from Scraper import fetch_instagram_data

async def get_profile_data(username):
    """ Fetch Instagram profile data """
    profile_data = await fetch_instagram_data(username)
    if profile_data:
        return f"Profile Data for {username}: {profile_data}"
    else:
        return "Failed to fetch profile data."
