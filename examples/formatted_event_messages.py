import asyncio

from chaturbate_poller import ChaturbateClient, ConfigManager, format_message

config_manager = ConfigManager()
username = config_manager.get("CB_USERNAME", "")
token = config_manager.get("CB_TOKEN", "")


async def main():
    async with ChaturbateClient(username, token) as client:
        url = None

        while True:
            response = await client.fetch_events(url)

            for event in response.events:
                message = await format_message(event)
                print(f"{message}")

            url = response.next_url


if __name__ == "__main__":
    asyncio.run(main())
