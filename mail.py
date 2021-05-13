import asyncio
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler, _check_spec, SkipHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.filters import check_filters, FilterNotPassed


class CollectAlbum(BaseMiddleware):
    def __init__(self, delay=1):
        super().__init__()
        self.albums = {}
        self.timerHandles = {}
        self.delay = delay

    async def notify(self, message: types.Message):
        data = {}
        for handler_obj in self.manager.dispatcher.message_handlers.handlers:
            try:
                data.update(await check_filters(handler_obj.filters, (message,)))
            except FilterNotPassed:
                continue
            else:
                try:
                    data[handler_obj.spec.args[0]] = self.albums.get(message.media_group_id)  # 🤢
                    partial_data = _check_spec(handler_obj.spec, data)
                    await handler_obj.handler(**partial_data)
                except SkipHandler:
                    continue
                except CancelHandler:
                    break
                finally:
                    break

    async def on_pre_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return
        self.albums.setdefault(message.media_group_id, []).append(message)
        await self.adaptive_delay(message)
        raise CancelHandler()

    async def adaptive_delay(self, message: types.Message):
        if len(self.albums.get(message.media_group_id, [])) != 1:
            self.timerHandles[message.media_group_id].cancel()
        self.timerHandles[message.media_group_id] = asyncio.get_event_loop().call_later(
                self.delay,
                asyncio.create_task,
                self.notify(message)
            )
