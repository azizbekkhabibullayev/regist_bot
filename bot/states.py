from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    address = State()


class AddCourseState(StatesGroup):
    name = State()
    description = State()


class TeacherProfileState(StatesGroup):
    full_name = State()
    phone = State()
    social_links = State()
    bio = State()


class CourseBroadcastState(StatesGroup):
    message = State()
