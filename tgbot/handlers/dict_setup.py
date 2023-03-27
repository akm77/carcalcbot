from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager

from tgbot.dialogs.auction_menu import states as auction_states
from tgbot.dialogs.country_menu import states as country_states

country_router = Router()
auction_router = Router()


@country_router.message(Command("country"))
async def setup_countries(message: types.Message, dialog_manager: DialogManager, state: FSMContext, **kwargs):
    await dialog_manager.start(country_states.CountryMenuStates.select_country,
                               data={"started_by": message.from_user.mention_html()})


@auction_router.message(Command("auction"))
async def setup_auction(message: types.Message, dialog_manager: DialogManager, state: FSMContext, **kwargs):
    await dialog_manager.start(auction_states.AuctionMenuStates.select_auction,
                               data={"started_by": message.from_user.mention_html()})
