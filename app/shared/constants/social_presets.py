"""Centralized dimension presets for image tools.

Single source of truth for the image resizer and any future preset-driven
tools. Presets are served to the client through the
``/api/v1/tools/image/presets`` endpoint.
"""

STANDARD_PRESETS = [
    {
        "id": "hd-1080p",
        "name": "1920 x 1080",
        "width": 1920,
        "height": 1080,
        "description": "HD 1080p",
    },
    {
        "id": "ws-1600x900",
        "name": "1600 x 900",
        "width": 1600,
        "height": 900,
        "description": "16:9 widescreen",
    },
    {
        "id": "hd-1280x720",
        "name": "1280 x 720",
        "width": 1280,
        "height": 720,
        "description": "HD 720p",
    },
    {
        "id": "square-1080",
        "name": "1080 x 1080",
        "width": 1080,
        "height": 1080,
        "description": "Square",
    },
    {
        "id": "portrait-1080x1350",
        "name": "1080 x 1350",
        "width": 1080,
        "height": 1350,
        "description": "4:5 portrait",
    },
    {
        "id": "portrait-1080x1920",
        "name": "1080 x 1920",
        "width": 1080,
        "height": 1920,
        "description": "9:16 portrait",
    },
    {
        "id": "fb-1200x630",
        "name": "1200 x 630",
        "width": 1200,
        "height": 630,
        "description": "Facebook link preview",
    },
]

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
