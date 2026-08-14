"""Centralized social media dimension presets.

Single source of truth for the social media resizer and any future
preset-driven tools. Presets are served to the client through the
``/api/v1/tools/image/social-presets`` endpoint.
"""

SOCIAL_PRESETS = [
    {
        "id": "instagram-post",
        "name": "Instagram Post",
        "width": 1080,
        "height": 1080,
        "description": "Square feed post",
    },
    {
        "id": "instagram-story",
        "name": "Instagram Story / Reels",
        "width": 1080,
        "height": 1920,
        "description": "9:16 vertical story",
    },
    {
        "id": "instagram-portrait",
        "name": "Instagram Portrait",
        "width": 1080,
        "height": 1350,
        "description": "4:5 feed portrait",
    },
    {
        "id": "instagram-landscape",
        "name": "Instagram Landscape",
        "width": 1080,
        "height": 566,
        "description": "1.91:1 feed landscape",
    },
    {
        "id": "facebook-post",
        "name": "Facebook Post",
        "width": 1200,
        "height": 630,
        "description": "1.91:1 link preview",
    },
    {
        "id": "facebook-cover",
        "name": "Facebook Cover",
        "width": 820,
        "height": 312,
        "description": "Profile cover photo",
    },
    {
        "id": "facebook-story",
        "name": "Facebook Story",
        "width": 1080,
        "height": 1920,
        "description": "9:16 story",
    },
    {
        "id": "twitter-post",
        "name": "X / Twitter Post",
        "width": 1600,
        "height": 900,
        "description": "In-stream image",
    },
    {
        "id": "twitter-card",
        "name": "X / Twitter Card",
        "width": 1200,
        "height": 675,
        "description": "Link card",
    },
    {
        "id": "linkedin-post",
        "name": "LinkedIn Post",
        "width": 1200,
        "height": 627,
        "description": "Feed image",
    },
    {
        "id": "linkedin-banner",
        "name": "LinkedIn Banner",
        "width": 1584,
        "height": 396,
        "description": "Profile banner",
    },
    {
        "id": "youtube-thumbnail",
        "name": "YouTube Thumbnail",
        "width": 1280,
        "height": 720,
        "description": "16:9 video thumbnail",
    },
    {
        "id": "youtube-banner",
        "name": "YouTube Banner",
        "width": 2560,
        "height": 1440,
        "description": "Channel banner",
    },
    {
        "id": "pinterest-pin",
        "name": "Pinterest Pin",
        "width": 1000,
        "height": 1500,
        "description": "2:3 vertical pin",
    },
    {
        "id": "tiktok-story",
        "name": "TikTok / Status",
        "width": 1080,
        "height": 1920,
        "description": "9:16 vertical video",
    },
    {
        "id": "whatsapp-status",
        "name": "WhatsApp Status",
        "width": 1080,
        "height": 1920,
        "description": "9:16 status image",
    },
]
