# 🍔 MealOrbit — Food Delivery Backend API

MealOrbit is a production-style **Food Delivery Backend API** built with FastAPI.
The project focuses on real-world backend architecture, authentication, database management, payments, caching, real-time communication, background processing, AI integration, testing, and deployment.

---

## 🎯 Project Goal

The main goal of MealOrbit is to build more than a basic CRUD application.

The project focuses on:

* Production-style backend architecture
* RESTful API development
* Role-Based Access Control
* Secure authentication
* Async database operations
* Redis caching and real-time communication
* Payment integration
* Background task processing
* AI-powered food assistance
* Automated testing
* Dockerized development and deployment

---

# 🛠️ Technology Stack

## Backend

* Python
* FastAPI
* Async SQLAlchemy
* PostgreSQL
* Alembic

## Authentication & Security

* JWT Authentication
* Access Token
* Refresh Token
* bcrypt Password Hashing
* Email Verification
* Forgot Password
* Password Reset
* Change Password
* Role-Based Access Control
* Input Validation
* CORS
* Secure Environment Variables

## Caching & Real-time

* Redis
* Redis Pub/Sub
* WebSocket
* Redis Caching

## Background Processing

* Celery
* RabbitMQ
* Flower

> **Current Status:** Celery, RabbitMQ, and Flower configuration are included in the project. The Celery Worker is currently disabled/commented and can be enabled when background processing is required.

## Payment

* SSLCOMMERZ Sandbox

## AI

* Hugging Face Transformers
* Gemma 3 1B
* PyTorch
* AI Food Recommendation
* AI Customer Support

## DevOps

* Docker
* Docker Compose
* Git
* GitHub

## Testing

* Pytest

---

# 👥 User Roles

MealOrbit supports four main user roles:

```text
CUSTOMER
RESTAURANT_OWNER
RIDER
ADMIN
```

Role-Based Access Control is used to manage permissions for different users.

---

# 📦 Main Features

## 🔐 Authentication

* User Registration
* User Login
* Logout
* JWT Access Token
* Refresh Token
* Email Verification
* Forgot Password
* Password Reset
* Change Password

---

## 👤 User Management

Customers can:

* View Profile
* Update Profile
* Upload Profile Image
* Delete Profile Image
* Update Phone Number
* Manage Addresses
* Set Default Address
* Deactivate Account

### Address

```text
id
user_id
address
city
area
postal_code
latitude
longitude
is_default
created_at
updated_at
```

---

## 🏪 Restaurant Management

Restaurant Owners can:

* Create Restaurant
* Update Restaurant
* Delete Restaurant
* View Restaurant
* Manage Restaurant Profile
* Upload Restaurant Image
* Manage Opening Hours
* Open / Close Restaurant
* View Restaurant Orders

### Restaurant Status

```text
OPEN
CLOSED
BUSY
```

---

## 🍔 Food Category

Example categories:

```text
Burger
Pizza
Chicken
Rice
Drinks
Dessert
```

Features:

* Create Category
* Update Category
* Delete Category
* Get Categories
* Search Categories
* Restaurant-based Categories

---

## 🍕 Food / Menu

Restaurant Owners can manage food items.

### Food Fields

```text
id
restaurant_id
category_id
name
description
price
image_url
is_available
created_at
updated_at
```

### Features

* Create Food
* Update Food
* Delete Food
* Get Food
* Search Food
* Filter by Category
* Filter by Restaurant
* Filter by Price
* Availability Management
* Pagination

---

## 🛒 Cart

Customers can:

* Add Food
* Update Quantity
* Remove Food
* Clear Cart
* View Cart

### Cart Calculation

```text
Food Price × Quantity
        +
Delivery Fee
        +
Tax
        -
Discount
        =
Grand Total
```

---

## 🎟️ Coupon / Discount

Features:

* Create Coupon
* Apply Coupon
* Remove Coupon
* Expiry Date
* Minimum Order Amount
* Maximum Discount
* Percentage Discount
* Fixed Discount
* Usage Limit

Example:

```text
FOOD20

20% OFF
Minimum Order: 500 BDT
Maximum Discount: 200 BDT
```

---

# 📦 Order Management

## Order Flow

```text
Cart
 ↓
Checkout
 ↓
Create Order
 ↓
Payment
 ↓
Restaurant Confirmation
 ↓
Food Preparing
 ↓
Rider Assigned
 ↓
Picked Up
 ↓
Out for Delivery
 ↓
Delivered
```

### Order Status

```text
PENDING
CONFIRMED
PREPARING
READY
RIDER_ASSIGNED
PICKED_UP
OUT_FOR_DELIVERY
DELIVERED
CANCELLED
```

---

# 🧾 Order Item

A single order can contain multiple food items.

Example:

```text
Order #1001

Burger × 2
Pizza × 1
Coke × 2
```

### Order Item Fields

```text
id
order_id
food_id
quantity
price
subtotal
```

The current food price is stored in `OrderItem.price` when the order is created.

This prevents old orders from changing when the food price is updated later.

---

# 💳 Checkout

Checkout process:

```text
Cart
 ↓
Validate Food Availability
 ↓
Calculate Subtotal
 ↓
Apply Coupon
 ↓
Calculate Tax
 ↓
Calculate Delivery Fee
 ↓
Calculate Grand Total
 ↓
Create Order
```

Checkout uses validation, transaction handling, and business rules to maintain data consistency.

---

# 💰 Payment

Payment provider:

**SSLCOMMERZ Sandbox**

### Payment Flow

```text
Create Order
      ↓
Create Payment
      ↓
SSLCOMMERZ
      ↓
Customer Payment
      ↓
Success / Fail / Cancel
      ↓
Callback / IPN
      ↓
Verify Payment
      ↓
Update Payment Status
      ↓
Update Order Status
```

### Payment Status

```text
PENDING
PROCESSING
PAID
FAILED
CANCELLED
REFUNDED
```

---

# 🛵 Rider & Delivery

Rider features:

* Rider Registration
* Rider Profile
* Online / Offline Status
* Accept Delivery
* Reject Delivery
* View Assigned Orders
* Update Delivery Status

### Delivery Flow

```text
Order Ready
     ↓
Find Available Rider
     ↓
Assign Rider
     ↓
Rider Accepts
     ↓
Food Pickup
     ↓
Delivery
     ↓
Delivered
```

---

# 📍 Real-time Delivery Tracking

Technologies:

* Redis
* Redis Pub/Sub
* WebSocket

### Tracking Flow

```text
Restaurant Accepted
       ↓
Food Preparing
       ↓
Rider Assigned
       ↓
Rider Picked Up
       ↓
Out for Delivery
       ↓
Delivered
```

### Future GPS Architecture

```text
Rider GPS
   ↓
Redis
   ↓
Redis Pub/Sub
   ↓
WebSocket
   ↓
Customer
```

---

# 🔔 Notification System

## Email Notifications

* Welcome Email
* Account Verification
* Password Reset
* Password Reset Success
* Order Confirmation
* Payment Confirmation
* Order Status Notification
* Order Delivered

## In-App Notifications

* Order Status
* Payment Status
* Rider Assigned
* Promotional Notifications

---

# ⚙️ Celery & RabbitMQ

MealOrbit includes Celery and RabbitMQ configuration for background processing.

### Planned Background Tasks

```text
Send Email
Send Notification
Process Order Notification
Generate Reports
Cleanup Expired Tokens
```

### Architecture

```text
FastAPI
   ↓
Celery Task
   ↓
RabbitMQ
   ↓
Celery Worker
   ↓
Task Processing
   ↓
Email / Notification
```

### Current Status

```text
RabbitMQ       → Configured
Celery         → Configured
Flower         → Configured
Celery Worker  → Currently Disabled / Commented
```

The worker can be enabled when background task processing is required.

---

# ⚡ Redis

Redis is currently used for:

## Caching

```text
Food Lists
Food Search
Food Filters
Food Categories
Popular Foods
```

## Temporary Data

```text
OTP
Verification Tokens
Rate Limiting
```

## Real-time Communication

```text
Rider Location
Order Status
WebSocket Pub/Sub
```

---

# ⭐ Review & Rating

Customers can review:

* Restaurant
* Food
* Delivery

### Review Fields

```text
rating
comment
user_id
restaurant_id
food_id
order_id
created_at
```

### Rating

```text
1 ⭐
2 ⭐
3 ⭐
4 ⭐
5 ⭐
```

Duplicate reviews are prevented through application validation and database constraints.

---

# 🔎 Search & Filtering

Food search:

```text
/search?query=burger
```

### Filters

```text
Category
Restaurant
Price
Rating
Availability
```

### Sorting

```text
Price Low → High
Price High → Low
Rating
Newest
Popular
```

Pagination is implemented for large datasets.

---

# 🤖 AI Food Assistant

MealOrbit uses **Hugging Face Gemma 3 1B** for AI-powered functionality.

### AI Stack

```text
Hugging Face Transformers
        ↓
Gemma 3 1B
        ↓
PyTorch
        ↓
FastAPI AI Service
```

### Example

User:

```text
My budget is 500 BDT.
I want chicken food.
I prefer spicy food.
```

AI:

```text
Recommended for you:

1. Chicken Burger - 250 BDT
2. Spicy Chicken Pizza - 400 BDT
3. Chicken Wings - 300 BDT
```

The backend can provide available food data to the AI service so that recommendations are based on actual database data.

---

# 🤖 AI Customer Support

Example:

```text
User:

Where is my order #1024?
```

AI:

```text
Order #1024 is currently
"Out for Delivery".

The rider is currently
on the way with your order.
```

The AI model should not have unrestricted access to sensitive database data.

Instead, the backend provides controlled and authorized data through application services/functions.

---

# 👨‍💼 Admin API

Admin features include:

## Users

```text
View Users
Block User
Unblock User
Delete User
Change User Role
```

Admin can change a user's role to:

```text
CUSTOMER
RESTAURANT_OWNER
RIDER
```

## Restaurants

```text
Approve Restaurant
Reject Restaurant
Block Restaurant
```

## Orders

```text
View All Orders
Filter Orders
Cancel Order
```

## Payments

```text
View Payments
Payment Statistics
Refund Management
```

## Reports

```text
Total Orders
Total Revenue
Total Users
Top Restaurants
Top Foods
```

---

# 🔒 Security

Security features include:

```text
JWT Authentication
Password Hashing
Role-Based Access Control
Input Validation
Rate Limiting
CORS
Secure Environment Variables
SQL Injection Protection
File Upload Validation
Payment Verification
```

---

# 🔗 API Versioning

Main API structure:

```text
/api/v1/auth
/api/v1/users
/api/v1/restaurants
/api/v1/categories
/api/v1/foods
/api/v1/cart
/api/v1/orders
/api/v1/payments
/api/v1/riders
/api/v1/reviews
/api/v1/notifications
/api/v1/admin
/api/v1/ai
```

---

# 📁 Project Structure

```text
MealOrbit/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth/
│   │       ├── users/
│   │       ├── restaurants/
│   │       ├── categories/
│   │       ├── foods/
│   │       ├── cart/
│   │       ├── orders/
│   │       ├── payments/
│   │       ├── riders/
│   │       ├── reviews/
│   │       ├── notifications/
│   │       ├── admin/
│   │       └── ai/
│   │
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── dependencies/
│   └── utils/
│
├── config/
├── tasks/
├── alembic/
├── tests/
├── uploads/
├── docker/
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── requirements.txt
├── README.md
└── main.py
```

---

# 🗄️ Main Database Tables

```text
users
addresses
restaurants
restaurant_hours

food_categories
foods
food_addons

carts
cart_items

coupons

orders
order_items

payments

riders
deliveries

reviews

notifications
refresh_tokens
password_reset_tokens
```

---

# 🚀 Development Roadmap

## Phase 1 — Foundation

```text
1. Project Setup
2. PostgreSQL
3. SQLAlchemy
4. Alembic
5. Docker
6. Environment Configuration
```

## Phase 2 — Authentication

```text
7. User Model
8. Register
9. Login
10. JWT
11. Refresh Token
12. Email Verification
13. Forgot Password
14. Reset Password
15. Change Password
```

## Phase 3 — Restaurant & Food

```text
16. Restaurant
17. Restaurant Hours
18. Food Category
19. Food
20. Search
21. Filtering
22. Pagination
23. Availability
```

## Phase 4 — Shopping

```text
24. Cart
25. Cart Items
26. Coupon
27. Checkout
```

## Phase 5 — Order

```text
28. Order
29. Order Item
30. Order Status
31. Order History
```

## Phase 6 — Payment

```text
32. Payment Model
33. SSLCOMMERZ
34. Payment Initialization
35. Success Callback
36. Fail Callback
37. Cancel Callback
38. IPN
39. Payment Verification
```

## Phase 7 — Delivery

```text
40. Rider
41. Delivery
42. Rider Assignment
43. Delivery Status
44. WebSocket Tracking
```

## Phase 8 — Async Processing

```text
45. RabbitMQ
46. Celery
47. Email Tasks
48. Notification Tasks
49. Flower
```

> Celery Worker is currently disabled/commented and can be enabled when background processing is required.

## Phase 9 — Redis

```text
50. Redis
51. Caching
52. Rate Limiting
53. Pub/Sub
54. Real-time Location
```

## Phase 10 — AI

```text
55. Hugging Face Transformers
56. Gemma 3 1B
57. AI Food Recommendation
58. AI Customer Support
59. Controlled Backend AI Tools
```

## Phase 11 — Testing

```text
60. Pytest
61. Authentication Tests
62. Food Tests
63. Cart Tests
64. Order Tests
65. Payment Tests
66. Integration Tests
```

## Phase 12 — Deployment

```text
67. Docker Compose
68. Production Environment
69. PostgreSQL
70. Redis
71. RabbitMQ
72. Celery Worker
73. Flower
74. FastAPI
75. Nginx
76. CI/CD
```

---

# 🏗️ Architecture

```text
                         ┌──────────────┐
                         │    Client    │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   FastAPI    │
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
       │ PostgreSQL  │   │    Redis    │   │ Gemma 3 1B  │
       │             │   │             │   │ HuggingFace │
       └─────────────┘   └──────┬──────┘   └─────────────┘
                                │
                                ▼
                       WebSocket / PubSub
                                │
                                ▼
                         Real-time Data


       ┌─────────────────────────────────────────┐
       │          Background Processing          │
       │                                         │
       │  FastAPI → Celery → RabbitMQ            │
       │                       ↓                 │
       │                 Celery Worker            │
       │                       ↓                 │
       │              Email / Notification       │
       └─────────────────────────────────────────┘


                         ┌──────────────┐
                         │  SSLCOMMERZ  │
                         └──────────────┘
```

---

# 📌 Current Project Status

| Component             | Status                  |
| --------------------- | ----------------------- |
| FastAPI               | ✅ Active                |
| PostgreSQL            | ✅ Active                |
| Async SQLAlchemy      | ✅ Active                |
| Alembic               | ✅ Active                |
| JWT Authentication    | ✅ Active                |
| Role-Based Access     | ✅ Active                |
| Redis                 | ✅ Active                |
| WebSocket             | ✅ Implemented           |
| RabbitMQ              | ✅ Configured            |
| Celery                | ✅ Configured            |
| Flower                | ✅ Configured            |
| Celery Worker         | ⏸️ Disabled / Commented |
| SSLCOMMERZ            | ✅ Sandbox               |
| Hugging Face          | ✅ Integrated            |
| Gemma 3 1B            | ✅ Integrated            |
| PyTorch               | ✅ Integrated            |
| Pytest                | 🚧 In Progress          |
| Docker                | ✅ Configured            |
| Production Deployment | 🚧 In Progress          |

---

# 🎯 Portfolio Goal

MealOrbit is designed as a portfolio project to demonstrate practical backend engineering skills:

* Production-style FastAPI Architecture
* Async PostgreSQL
* SQLAlchemy
* Alembic
* JWT Authentication
* Role-Based Access Control
* Redis Caching
* Redis Pub/Sub
* WebSocket
* RabbitMQ
* Celery Background Processing
* Flower Monitoring
* SSLCOMMERZ Payment Integration
* Hugging Face Transformers
* Gemma 3 1B
* AI Food Recommendation
* AI Customer Support
* Docker
* Automated Testing
* API Documentation
* Production Deployment

---

## 📄 API Documentation

FastAPI automatically provides interactive API documentation:

```text
/docs
```

and OpenAPI specification:

```text
/openapi.json
```

---

## 🚀 Project Status

MealOrbit is an ongoing backend engineering project focused on building and practicing a production-style food delivery platform with modern backend technologies, real-time features, asynchronous processing, payment integration, and AI capabilities.
