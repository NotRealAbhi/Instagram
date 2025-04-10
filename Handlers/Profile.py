import json
from Scraper import fetch_page  # Import the fetch_page function from Scraper
from bs4 import BeautifulSoup

async def fetch_profile_info(username: str):
    """
    Fetch Instagram profile information including profile pic, bio, followers count, etc.
    :param username: Instagram username
    :return: Tuple containing profile picture URL and profile details caption
    """
    url = f"https://www.instagram.com/{username}/"
    
    # Fetch the page HTML
    html = await fetch_page(url)
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    
    # Find the script tag containing the profile data
    scripts = soup.find_all("script", type="text/javascript")
    data_script = next((s for s in scripts if "window._sharedData" in s.text), None)
    
    if not data_script:
        raise Exception("Couldn't extract profile data.")
    
    # Extract the JSON data from the script
    json_text = data_script.string.split(" = ", 1)[1].rstrip(";")
    data = json.loads(json_text)
    
    try:
        # Extract user data from the JSON
        user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        
        # Extract the necessary details from the user profile
        name = user.get("full_name", "N/A")
        bio = user.get("biography", "N/A")
        profile_pic = user.get("profile_pic_url_hd", "")
        posts_count = user['edge_owner_to_timeline_media']['count']
        followers_count = user['edge_followed_by']['count']
        following_count = user['edge_follow']['count']
        is_private = user['is_private']
        is_verified = user['is_verified']
        
        # Create a profile caption with the details
        caption = (
            f"👤 **{name}**\n"
            f"🔗 **Username:** `{username}`\n"
            f"📖 **Bio:** {bio or 'N/A'}\n"
            f"📸 **Posts:** {posts_count}\n"
            f"👥 **Followers:** {followers_count}\n"
            f"👣 **Following:** {following_count}\n"
            f"🔒 **Private:** {is_private}\n"
            f"✔ **Verified:** {is_verified}"
        )
        
        return profile_pic, caption
    except KeyError as e:
        raise Exception(f"Error extracting data: Missing key {e}")
        
