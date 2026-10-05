import uvicorn
from fastapi import FastAPI
from app.api.v1.auth.auth_router import router as auth_router
from app.api.v1.users.user_router import router as user_router
from app.api.v1.restaurants.restaurant_router import router as restaurant_router
from app.api.v1.restaurants.restaurant_hours_router import router as restaurant_hours_router
from app.api.v1.categories.food_category_router import router as category_router
from app.api.v1.foods.food_router import router as food_router
from app.api.v1.cart.cart_router import router as cart_router
from app.api.v1.coupon.coupon_router import router as coupon_router
from app.api.v1.orders.order_router import router as order_router
from app.api.v1.payments.payment_router import router as payment_router
from app.api.v1.riders.rider_router import router as rider_router
from app.api.v1.reviews.review_router import router as review_router
from app.api.v1.notifications.notification_router import router as notification_router
from app.api.v1.delivery.delivery_router import router as delivery_router
from app.api.v1.location.location_router import router as location_router
from app.api.v1.location.location_ws_router import router as websocket_router
from app.api.v1.redis.redis_router import router as redis_router





app = FastAPI(title=" MealOrbit food Delivery Backend API")


app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(restaurant_router, prefix="/api/v1/restaurants", tags=["Restaurants"])
app.include_router(restaurant_hours_router,prefix="/api/v1/restaurant-hours", tags=["Restaurant-Hours"])
app.include_router(category_router, prefix="/api/v1/categories", tags=["Food category"])
app.include_router(food_router, prefix="/api/v1/food", tags=["Food"])
app.include_router(coupon_router, prefix="/api/v1/coupon", tags=["Coupon"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(cart_router, prefix="/api/v1/cart", tags=["Cart"])
app.include_router(payment_router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(rider_router, prefix="/api/v1/riders", tags=["Riders"])
app.include_router(delivery_router, prefix="/api/v1/delivery", tags=["Delivery"])
app.include_router(location_router, prefix="/api/v1/locations", tags=["Locations"])
app.include_router(notification_router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(websocket_router,prefix="/api/v1/location-ws",tags=["WebSocket Tracking"])
app.include_router(review_router, prefix="/api/v1/reviews", tags=["Reviews"])
app.include_router(redis_router, prefix="/api/v1/redis", tags=["Redis"])




@app.get("/")
async def root():
    return {"message": "Welcome to Food Delivery API"}

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


