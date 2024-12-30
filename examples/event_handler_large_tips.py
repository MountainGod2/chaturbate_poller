import asyncio

from chaturbate_poller import ChaturbateClient, ConfigManager

LARGE_TIP_THRESHOLD = 100  # Set the threshold for large tips

config_manager = ConfigManager()

username = config_manager.get("CB_USERNAME", "")
token = config_manager.get("CB_TOKEN", "")


async def handle_large_tip(tip, user):
    if tip.tokens >= LARGE_TIP_THRESHOLD:
        # Do something with the large tip here
        print(f"User {user.username} tipped {tip.tokens} tokens!")


async def main():
    async with ChaturbateClient(username, token) as client:
        url = None

        # Fetch events in a loop
        while True:
            response = await client.fetch_events(url)

            for event in response.events:
                if event.method == "tip":  # Check if the event is a tip event
                    tip = event.object.tip
                    user = event.object.user

                    if tip and user:
                        await handle_large_tip(tip, user)  # Handle the large tip

            # Get the next URL to fetch the next page of events
            url = response.next_url


if __name__ == "__main__":
    asyncio.run(main())
