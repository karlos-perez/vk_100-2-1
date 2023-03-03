import asyncio
from asyncio import Task
from logging import getLogger

from app.store import Store
from app.store.vk_api.dataclasses import to_list_dt


class Poller:
    def __init__(self, store: Store, queue: bool):
        self.logger = getLogger(self.__class__.__name__)
        self.store = store
        self.queue = queue
        self.is_running = False
        self.poll_task: Task | None = None

    async def start(self):
        self.poll_task = asyncio.create_task(self.poll())
        self.is_running = True
        self.logger.info("START polling")

    async def stop(self):
        self.is_running = False
        await self.poll_task
        self.logger.info("STOP polling")

    async def poll(self):
        while self.is_running:
            raw_updates = await self.store.vk_api.poll()
            if raw_updates:
                if self.queue:
                    await self.store.queue.publish(raw_updates)
                else:
                    updates = to_list_dt(raw_updates)
                    await self.store.bot_manager.handler_updates(updates)
