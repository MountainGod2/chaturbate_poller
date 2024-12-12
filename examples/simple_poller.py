import asyncio

from chaturbate_poller import ChaturbateClient, ConfigManager

config_manager = ConfigManager()
username = config_manager.get("CB_USERNAME", "")
token = config_manager.get("CB_TOKEN", "")


async def main():
    async with ChaturbateClient(username, token) as client:
        url = None

        # Fetch events in a loop
        while True:
            # Call the fetch_events method to get the events
            response = await client.fetch_events(url)

            for event in response.events:
                print(event.model_dump())  # Print the event as a dictionary

            # Get the next URL to fetch the next page of events
            url = response.next_url


if __name__ == "__main__":
    asyncio.run(main())
