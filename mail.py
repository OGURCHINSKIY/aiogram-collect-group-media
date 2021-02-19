import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext


bot = Bot(token='')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_group_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(f"Media group: {data[message.media_group_id]}")


@dp.message_handler(lambda message: message.media_group_id is not None, content_types="photo")
async def album_handle(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.media_group_id not in data:
            asyncio.get_event_loop().call_later(1, asyncio.create_task, on_group_photo(message, state))
        # data._data.setdefault(message.media_group_id, []).append(message.photo[-1].file_id) # for version <2.11.2
        data.setdefault(message.media_group_id, []).append(message.photo[-1].file_id)


async def on_group_document(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        for file in data[message.media_group_id]:
            await file.download()


@dp.message_handler(lambda message: message.media_group_id is not None, content_types="document")
async def album_handle(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.media_group_id not in data:
            asyncio.get_event_loop().call_later(1, asyncio.create_task, on_group_document(message, state))
        # data._data.setdefault(message.media_group_id, []).append(message.document) # for version <2.11.2
        data.setdefault(message.media_group_id, []).append(message.document)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
