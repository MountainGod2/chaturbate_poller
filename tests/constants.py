USERNAME = "testuser"
TOKEN = "testtoken"  # noqa: S105
TEST_URL = f"https://eventsapi.chaturbate.com/events/{USERNAME}/{TOKEN}/"
EVENT_DATA = {
    "events": [
        {
            "method": "userEnter",
            "object": {
                "user": {
                    "username": "fan_user",
                    "inFanclub": True,
                    "hasTokens": True,
                    "isMod": False,
                    "gender": "m",
                    "recentTips": "none",
                }
            },
            "id": "event_id_1",
        }
    ],
    "nextUrl": TEST_URL,
}
INVALID_TIP_EVENT_DATA = {
    "events": [
        {
            "method": "tip",
            "object": {
                "tip": {
                    "tokens": 0,
                    "isAnon": False,
                    "message": "Test message",
                },
                "user": {
                    "username": "fan_user",
                    "inFanclub": True,
                    "hasTokens": True,
                    "isMod": False,
                    "gender": "m",
                    "recentTips": "none",
                },
            },
            "id": "event_id_1",
        }
    ],
    "nextUrl": TEST_URL,
}
