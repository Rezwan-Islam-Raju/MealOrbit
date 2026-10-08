# 🍔 MealOrbit — Food Delivery Backend API

MealOrbit is a production-style **Food Delivery Backend API** built with FastAPI.

The project focuses on real-world backend engineering concepts including authentication, role-based access control, database management, payments, caching, real-time communication, background processing, AI integration, testing, Docker, and deployment.

---

## 🎯 Project Goal

The main goal of MealOrbit is to build more than a basic CRUD application.

The project focuses on:

* Production-style backend architecture
* RESTful API development
* Role-Based Access Control
* Secure authentication
* Async database operations
* PostgreSQL database management
* Redis caching and real-time communication
* Payment integration
* Background task processing
* AI-powered food assistance
* Automated testing
* Dockerized development
* Production deployment

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

> **Current Status:** Celery, RabbitMQ, and Flower are configured in the project. The Celery Worker is currently disabled/commented and can be enabled when background processing is required.

## Payment

* SSLCOMMERZ Sandbox

## AI

* Hugging Face Transformers
* Gemma 3 1B
* PyTorch
* AI Food Recommendation
* AI Customer Support

> **Deployment Note:** Gemma 3 1B is integrated and tested locally. Due to the memory requirements of PyTorch and the Gemma model, the AI service is not currently deployed on the Render web service. A separate higher-memory AI service is planned for production deployment.

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

# 🏪 Restaurant Management

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

Administrators can manage and control restaurant-related operations.

### Restaurant Status

```text
OPEN
CLOSED
BUSY
```

---

# 🍔 Food Category

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

# 🍕 Food / Menu

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

# 🛒 Cart

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

# 🎟️ Coupon / Discount

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

### Real-time Architecture

```text
Rider
  ↓
FastAPI
  ↓
Redis
  ↓
Redis Pub/Sub
  ↓
WebSocket
  ↓
Customer
```

The WebSocket layer is used for real-time delivery location and status communication.

---

# 🔔 Notification System

## Email Notifications

The project includes email notification functionality for:

* Welcome Email
* Account Verification
* Password Reset
* Password Reset Success
* Order Confirmation
* Payment Confirmation
* Order Status Notification
* Order Delivered

## In-App Notifications

Examples:

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

Food search supports queries such as:

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

### Current AI Deployment Status

```text
Gemma 3 1B
        ↓
Local Development
        ↓
Integrated & Tested
```

The model is currently **not deployed inside the Render MealOrbit web service** because the memory requirements of PyTorch and Gemma 3 1B exceed the available memory of the current deployment environment.

A separate higher-memory AI service is planned for production deployment.

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

Instead, the backend provides controlled and authorized data through application services or backend functions.

---

# 👨‍💼 Admin API

MealOrbit uses the existing `User` model with an `admin` role for administrative functionality.

No separate Admin model is required.

## User Management

Admin features include:

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

The admin role itself is not assigned through the normal user role-change endpoint.

## Restaurant Management

Administrative operations can include:

```text
Approve Restaurant
Reject Restaurant
Block Restaurant
```

## Order Management

```text
View All Orders
Filter Orders
Cancel Order
```

## Payment Management

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

> Celery Worker is currently disabled/commented and can be enabled when background task processing is required.

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
60. Separate AI Production Deployment
```

## Phase 11 — Testing

```text
61. Pytest
62. Authentication Tests
63. Food Tests
64. Cart Tests
65. Order Tests
66. Payment Tests
67. Integration Tests
```

## Phase 12 — Deployment

```text
68. Docker Compose
69. Production Environment
70. PostgreSQL
71. Redis
72. RabbitMQ
73. Celery Worker
74. Flower
75. FastAPI
76. Nginx
77. CI/CD
78. Separate AI Service
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
                         │  MealOrbit   │
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
       │ PostgreSQL  │   │    Redis    │   │ AI Service   │
       │             │   │             │   │ Gemma 3 1B   │
       └─────────────┘   └──────┬──────┘   └──────┬───────┘
                                │                 │
                                ▼                 ▼
                       WebSocket / PubSub   Hugging Face
                                │            Transformers
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

### AI Production Architecture

The current AI model is designed to be separated from the main API during production deployment.

```text
                    ┌──────────────┐
                    │   Client     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ MealOrbit API│
                    │   FastAPI    │
                    └──────┬───────┘
                           │
                           │ AI Request
                           ▼
                 ┌─────────────────────┐
                 │   Separate AI       │
                 │      Service        │
                 │                     │
                 │    Gemma 3 1B       │
                 │    PyTorch          │
                 │    Transformers     │
                 └─────────────────────┘
```

This architecture avoids loading the large AI model inside the main API server.

---

# 📊 Current Project Status

| Component                | Status                  |
| ------------------------ | ----------------------- |
| FastAPI                  | ✅ Active                |
| PostgreSQL               | ✅ Active                |
| Async SQLAlchemy         | ✅ Active                |
| Alembic                  | ✅ Active                |
| JWT Authentication       | ✅ Active                |
| Role-Based Access        | ✅ Active                |
| Redis                    | ✅ Active                |
| WebSocket                | ✅ Implemented           |
| RabbitMQ                 | ✅ Configured            |
| Celery                   | ✅ Configured            |
| Flower                   | ✅ Configured            |
| Celery Worker            | ⏸️ Disabled / Commented |
| SSLCOMMERZ               | ✅ Sandbox               |
| Hugging Face             | ✅ Integrated            |
| Gemma 3 1B               | ✅ Integrated / Local    |
| PyTorch                  | ✅ Integrated            |
| AI Production Deployment | 🚧 Planned              |
| Pytest                   | 🚧 In Progress          |
| Docker                   | ✅ Configured            |
| Production Deployment    | 🚧 In Progress          |

---

# 🧪 Testing

MealOrbit uses **Pytest** for automated testing.

Planned and ongoing test coverage includes:

```text
Authentication
User Management
Restaurant
Food
Cart
Coupon
Order
Payment
Rider
Delivery
Review
Admin
AI
Integration
```

Testing is an ongoing part of the project.

---

# 🐳 Docker

Docker is used for local infrastructure and development.

Configured services include:

```text
PostgreSQL
Redis
RabbitMQ
```

Docker Compose is used to manage the infrastructure services.

The project can be run using the Docker Compose configuration inside:

```text
docker/docker-compose.yml
```

---

# 🌐 Deployment

The main MealOrbit API is being prepared for production deployment.

The project has been tested with a cloud deployment environment using:

```text
FastAPI
PostgreSQL
Docker
Environment Variables
```

### AI Deployment Limitation

The Gemma 3 1B model works locally but requires more memory than the current Render web service environment provides.

Therefore:

```text
Main API
   ↓
Production Web Service

Gemma 3 1B
   ↓
Separate Higher-Memory AI Service
   ↓
Future Production Deployment
```

This separation is planned to keep the main API lightweight and stable.

---

# 📌 Current Project Status Summary

MealOrbit currently has:

```text
FastAPI Backend
        ↓
Async PostgreSQL
        ↓
JWT Authentication
        ↓
Role-Based Access Control
        ↓
Restaurant & Food Management
        ↓
Cart & Checkout
        ↓
Orders
        ↓
SSLCOMMERZ Sandbox
        ↓
Rider & Delivery
        ↓
Redis
        ↓
WebSocket
        ↓
RabbitMQ / Celery Configuration
        ↓
AI Integration with Gemma 3 1B
```

The AI model is currently available for local development and testing, while production AI deployment is planned as a separate service.

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

# 📄 API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
/docs
```

### OpenAPI Specification

```text
/openapi.json
```

When running locally:

```text
http://127.0.0.1:8000/docs
```

---

# 📦 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Rezwan-Islam-Raju/MealOrbit.git
cd MealOrbit
```

## 2. Create Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file based on `.env.example`.

Configure:

```text
DATABASE_URL
JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY

EMAIL_HOST
EMAIL_PORT
EMAIL_USERNAME
EMAIL_PASSWORD

REDIS_URL

RABBITMQ_URL

SSLCOMMERZ_STORE_ID
SSLCOMMERZ_STORE_PASSWORD

HUGGINGFACE_TOKEN
```

## 5. Run Database Migrations

```powershell
alembic upgrade head
```

## 6. Start FastAPI

```powershell
python -m uvicorn main:app --reload
```

API will be available at:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 🐇 RabbitMQ / Redis

Docker Compose configuration:

```text
docker/docker-compose.yml
```

From the project root:

```powershell
docker compose -f docker/docker-compose.yml up -d
```

Check services:

```powershell
docker compose -f docker/docker-compose.yml ps
```

---

# ⚙️ Celery Worker

The Celery Worker is currently disabled/commented in the project workflow.

When background processing is required, the worker can be started with:

```powershell
celery -A app.core.celery_app.celery_app worker --loglevel=info --pool=solo
```

Flower can be used for task monitoring when configured:

```text
http://127.0.0.1:5555
```

---

# 🤖 Local AI Development

Gemma 3 1B is integrated for local AI development.

The model is stored locally and loaded through:

```text
Hugging Face Transformers
        ↓
Gemma 3 1B
        ↓
PyTorch
        ↓
FastAPI
```

Because the model requires significant memory, it is not currently loaded into the production Render web service.

A separate AI deployment is planned.

---

# 📈 Future Improvements

Planned improvements include:

* Separate production AI service
* Higher-memory AI deployment
* Improved AI tool calling
* Database-aware AI recommendations
* RAG-based food knowledge
* More comprehensive Pytest coverage
* Production Celery Worker
* Production Flower monitoring
* Better rate limiting
* Advanced restaurant analytics
* Order analytics
* Payment reconciliation
* CI/CD pipeline
* Nginx reverse proxy
* Production monitoring
* Logging and observability
* Automated deployment

---

# 🏁 Project Status

MealOrbit is an ongoing backend engineering project focused on building and practicing a production-style food delivery platform with:

* Modern backend architecture
* Secure authentication
* Async database operations
* Real-time communication
* Redis caching
* Background processing
* Payment integration
* AI capabilities
* Automated testing
* Dockerized development
* Cloud deployment

The core backend is actively developed, while AI production deployment and several advanced production features remain ongoing work.

---

## 👨‍💻 Developer

**Rezwan Islam Raju**

Backend-focused developer working with:

```text
Python
FastAPI
PostgreSQL
SQLAlchemy
Redis
Celery
RabbitMQ
Docker
AI / LLM Integration
```

---

## ⭐ Project

If you find this project useful or interesting, feel free to explore the repository and follow the development progress.

**MealOrbit — Food Delivery Backend API**
