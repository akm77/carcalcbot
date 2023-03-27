from aiogram.fsm.state import StatesGroup, State


class AuctionMenuStates(StatesGroup):
    select_auction = State()
