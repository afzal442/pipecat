import argparse
import asyncio

import aiohttp

from dailyai.queue_frame import TextQueueFrame
from dailyai.services.daily_transport_service import DailyTransportService
from dailyai.services.fal_ai_services import FalImageGenService

local_joined = False
participant_joined = False


async def main(room_url):
    async with aiohttp.ClientSession() as session:
        meeting_duration_minutes = 1
        transport = DailyTransportService(
            room_url,
            None,
            "Show a still frame image",
            meeting_duration_minutes,
        )
        transport.mic_enabled = False
        transport.camera_enabled = True
        transport.camera_width = 1024
        transport.camera_height = 1024

        imagegen = FalImageGenService(image_size="1024x1024", aiohttp_session=session)
        image_task = asyncio.create_task(
            imagegen.run_to_queue(
                transport.send_queue, [
                    TextQueueFrame("a cat in the style of picasso")]))

        @transport.event_handler("on_first_other_participant_joined")
        async def on_first_other_participant_joined(transport):
            await image_task

        await transport.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Daily Bot Sample")
    parser.add_argument(
        "-u", "--url", type=str, required=True, help="URL of the Daily room to join"
    )

    args, unknown = parser.parse_known_args()

    asyncio.run(main(args.url))