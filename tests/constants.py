USERNAME = "testuser"
TOKEN = "testtoken"  # noqa: S105
TEST_URL = f"https://eventsapi.chaturbate.com/events/{USERNAME}/{TOKEN}/"
VALID_TIP_EVENT = {
    "method": "tip",
    "object": {
        "tip": {
            "tokens": 100,
            "isAnon": False,
            "message": "Example message",
        },
        "user": {
            "username": "example_user",
            "inFanclub": True,
            "hasTokens": True,
            "isMod": False,
            "gender": "m",
            "recentTips": "some",
        },
    },
    "id": "event_id_1",
}
INVALID_TIP_EVENT = {
    "method": "tip",
    "object": {
        "tip": {
            "tokens": 0,
            "isAnon": False,
            "message": "",
        },
        "user": {
            "username": "example_user",
            "inFanclub": True,
            "hasTokens": True,
            "isMod": False,
            "gender": "m",
            "recentTips": "some",
        },
    },
    "id": "event_id_2",
}
