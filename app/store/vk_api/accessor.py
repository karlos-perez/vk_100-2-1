import json
import time
import typing

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.store.base_accessor import BaseAccessor
from app.store.bot.dataclasses import Message
from app.store.utils import is_message_from_chat
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, *args, **kwargs):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(self.app.store, self.app.config.queue.enable)
        await self.poller.start()

    async def disconnect(self, *args, **kwargs):
        try:
            await self.poller.stop()
        except Exception as err:
            self.logger.error(err)
        try:
            await self.session.close()
        except Exception as err:
            self.logger.error(err)

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                    "lp_version": 3,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def poll(self):
        url = self._build_query(
            host=self.server,
            method="",
            params={
                "act": "a_check",
                "key": self.key,
                "ts": self.ts,
                "wait": 30,
                "mode": 2,
                "version": 3,
            },
        )
        # self.logger.info(url)
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.logger.info(data)
            if data.get("failed"):
                try:
                    await self._get_long_poll_service()
                except Exception as e:
                    self.logger.exception("Exception", exc_info=e)
            if data.get("error"):
                self.logger.error(data)
            self.ts = data["ts"]
            updates = data.get("updates", [])
        return updates

    async def get_user_info(self, user_id: int) -> dict | None:
        params = {"user_id": user_id, "access_token": self.app.config.bot.token}
        url = self._build_query(API_PATH, "users.get", params=params)
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.logger.info(data)
            return data.get("response")

    async def get_chat_users(self, peer_id: int) -> dict | None:
        params = {"peer_id": peer_id, "access_token": self.app.config.bot.token}
        url = self._build_query(
            API_PATH, "messages.getConversationMembers", params=params
        )
        # self.logger.info(url)
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.logger.info(data)
            return data.get("response")

    async def send_message(self, message: Message) -> None:
        params = {
            "random_id": int(time.time()),
            "peer_id": message.peer_id,
            "message": message.text,
            "access_token": self.app.config.bot.token,
        }
        if not is_message_from_chat(message.peer_id):
            params["user_id"] = message.user_id
        if message.buttons:
            params["keyboard"] = message.buttons
        url = self._build_query(API_PATH, "messages.send", params=params)
        self.logger.info(url)
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.logger.info(data)
            return data.get("response")

    async def send_event_answer(self, message: Message, event_data: dict) -> None:
        params = {
            "user_id": message.user_id,
            "event_id": message.text,
            "peer_id": message.peer_id,
            "event_data": json.dumps(event_data),
            "access_token": self.app.config.bot.token,
        }
        url = self._build_query(
            API_PATH, "messages.sendMessageEventAnswer", params=params
        )
        self.logger.info(url)
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.logger.info(data)
            return data.get("response")

    async def send_message_edit(self, message: Message) -> None:
        params = {
            "conversation_message_id": message.user_id,
            "peer_id": message.peer_id,
            "message": message.text,
            "access_token": self.app.config.bot.token,
        }
        if message.buttons:
            params["keyboard"] = message.buttons
        url = self._build_query(API_PATH, "messages.edit", params=params)
        self.logger.info(url)
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def send_message_delete(self, message_id: int, peer_id: int) -> None:
        params = {
            "cmids": message_id,
            "peer_id": peer_id,
            "delete_for_all": 1,
            "access_token": self.app.config.bot.token,
        }
        url = self._build_query(API_PATH, "messages.delete", params=params)
        self.logger.info(url)
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.logger.info(data)
