import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from config.config import DATABASE_URL
from config.database import Base


# IMPORT ALL MODELS


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

from app.models.review_model import Review
from app.models.notification_model import Notification


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata



# DATABASE URL


# config.config থেকে DATABASE_URL
# postgresql:// → postgresql+asyncpg:// already converted.


# OFFLINE MIGRATION


def run_migrations_offline() -> None:

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()



# ONLINE MIGRATION


def do_run_migrations(connection: Connection) -> None:

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:

    connectable = create_async_engine(
        DATABASE_URL,
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



# RUN


if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()