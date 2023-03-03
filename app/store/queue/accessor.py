import asyncio
import json
import typing
from asyncio import Task

from aio_pika import connect, Message, IncomingMessage

from app.store.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Update, to_list_dt

if typing.TYPE_CHECKING:
    from app.web.app import Application


class QueueAccessor(BaseAccessor):
    ROUTING_KEY = "vk_queue"

    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.connection = None
        self.consumer_task: Task | None = None

    async def connect(self, *args, **kwargs):
        self.connection = await connect(self.app.config.queue.url)
        self.consumer_task = asyncio.create_task(self.consumer())
        self.logger.info("START queue")

    async def disconnect(self, *args, **kwargs):
        await self.consumer_task

        try:
            await self.connection.close()
            self.logger.info("STOP queue")
        except Exception as err:
            self.logger.error(err)

    async def publish(self, data: list[Update]):
        if not self.connection:
            raise ConnectionError
        channel = await self.connection.channel()
        await channel.default_exchange.publish(
            Message(body=json.dumps(data).encode()), routing_key=self.ROUTING_KEY
        )

    async def massage_handler(self, message: IncomingMessage) -> None:
        async with message.process():
            try:
                # self.logger.info(f"Queue Income Message: {message.body.decode()}")
                raw_updates = json.loads(message.body.decode())
            except Exception as err:
                self.logger.exception(err)
            updates = to_list_dt(raw_updates)
            await self.app.store.bot_manager.handler_updates(updates)

    async def consumer(self):
        if self.connection is None:
            raise ConnectionError
        channel = await self.connection.channel()
        queue = await channel.declare_queue(self.ROUTING_KEY, auto_delete=True)
        await queue.consume(self.massage_handler)
