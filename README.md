
# 🛒 Flask E-Commerce Web Application

<!-- Project Title -->
A full-stack E-Commerce web application built using Flask, SQLite, HTML, CSS, and JavaScript.

<!-- Short Project Description -->
This project demonstrates user authentication, product management, shopping cart functionality, order processing, and admin role-based access control.

---

## 🚀 Features

### 👤 User Features
- User Registration & Login
- Secure Password Hashing (SHA-256)
- Session-Based Authentication
- Browse Product Catalog
- Add Products to Cart
- Place Orders
- View Order History
- Logout

### 🛠️ Admin Features
- Add New Products
- Delete Products
- View All Orders
- Update Order Status (Pending → Shipped)
- Role-Based Access Control

---

## 🏗️ Tech Stack

<!-- Technologies used in the project -->
- Backend: Flask (Python)
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Authentication: Flask Sessions
- API Style: RESTful JSON APIs

---

## 📂 Project Structure

<!-- Folder Structure -->
ecommerce-project/
│
├── app.py              # Main Flask Application
├── requirements.txt    # Python Dependencies
├── README.md           # Project Documentation
└── .gitignore          # Files ignored by Git

<!-- Important Note -->
Note: ecommerce.db is auto-generated when the application runs and should NOT be uploaded to GitHub.

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

<!-- Clone project from GitHub -->
https://github.com/anusiya8148/ecommerceflask.git
cd ecommerce-project

---

### 2️⃣ Create Virtual Environment (Recommended)

<!-- Create virtual environment -->
python -m venv venv

Activate environment:

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

---

### 3️⃣ Install Dependencies

<!-- Install required packages -->
pip install -r requirements.txt

If you don’t have requirements.txt:
pip install flask

---

### 4️⃣ Run the Application

<!-- Run Flask App -->
python app.py

Server will start at:
http://127.0.0.1:5000/

---

## 🗄️ Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- password (Hashed)
- role (user/admin)

### Products Table
- id
- name
- price
- image
- description

### Orders Table
- id
- user_id (Foreign Key)
- items
- total
- image_desc
- status (default: pending)
- created_at (timestamp)

---

## 📡 API Endpoints

### Authentication
- POST /api/register
- POST /api/login
- GET /api/logout

### Products
- GET /api/products
- POST /api/products (Admin only)
- DELETE /api/products/<id> (Admin only)

### Orders
- POST /api/orders
- GET /api/orders
- PUT /api/orders/<id> (Admin only)

---

## 🔐 Security Features

<!-- Security Implementation Details -->
- Passwords hashed using SHA-256
- Session-based authentication
- Admin routes protected
- User can only view their own orders
- Role-based access control

---

## 📈 Future Improvements

<!-- Possible upgrades -->
- JWT Authentication
- Stripe Payment Integration
- Product Quantity System
- Order Tracking
- Admin Dashboard with Analytics
- Docker Support
- Cloud Deployment (Render / Railway / AWS)

---

## 🎯 Resume Description

Developed a full-stack E-Commerce web application using Flask and SQLite featuring session-based authentication, RESTful APIs, product CRUD operations, order management, and admin role-based access control.
---
##Author
Anusiya R
Second-year student ,Full Stack Developer.
---

## 📜 License

This project is built for educational and portfolio purposes.
