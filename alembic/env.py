import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from config.database import Base

from app.models.user_model import User
from app.models.user_activation_token_model import UserActivationToken
from app.models.refresh_token_model import RefreshToken
from app.models.password_reset_token_model import PasswordResetToken

from app.models.restaurants_model import Restaurant
from app.models.restaurant_hours_model import RestaurantHours

from app.models.food_category_model import FoodCategory
from app.models.food_model import Food

from app.models.cart_model import Cart, CartItem
from app.models.coupon_model import Coupon
from app.models.order_model import Order, OrderItem
from app.models.payment_model import Payment
from app.models.rider_model import Rider
from app.models.delivery_model import Delivery


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:

        await connection.run_sync(
            do_run_migrations
        )

    await connectable.dispose()


def run_migrations_online() -> None:

    asyncio.run(
        run_async_migrations()
    )


if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()