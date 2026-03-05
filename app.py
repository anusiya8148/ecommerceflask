from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import sqlite3, hashlib, os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # More secure random key...

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anivique Shop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }

        /* Header & Nav */
        header {
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        nav {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            backdrop-filter: blur(10px);
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        nav button, nav a {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 20px;
            margin: 0 8px;
            cursor: pointer;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s;
            font-size: 14px;
        }
        nav button:hover { background: #0056b3; transform: translateY(-2px); }

        /* Search Bar */
        .search-container {
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        .search-box {
            position: relative;
            max-width: 500px;
            margin: 0 auto;
        }
        #searchInput, #adminSearchInput {
            width: 100%;
            padding: 15px 50px 15px 20px;
            font-size: 18px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            outline: none;
            transition: all 0.3s;
            background: white;
        }
        #searchInput:focus, #adminSearchInput:focus {
            border-color: #007bff;
            box-shadow: 0 0 20px rgba(0,123,255,0.3);
        }
        .search-btn {
            position: absolute;
            right: 5px;
            top: 50%;
            transform: translateY(-50%);
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 16px;
        }
        .search-btn:hover { background: #0056b3; }

        /* Categories */
        .categories {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
        }
        .category-btn {
            background: rgba(255,255,255,0.9);
            color: #333;
            border: 2px solid #e9ecef;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }
        .category-btn:hover, .category-btn.active {
            background: #007bff;
            color: white;
            border-color: #007bff;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,123,255,0.4);
        }

        /* Admin Categories */
        .admin-categories {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }

        /* Products */
        .products {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }
        .product {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        .product:hover { transform: translateY(-5px); }
        .image-wrapper {
            position: relative;
            cursor: zoom-in;
            border-radius: 10px;
            overflow: hidden;
        }
        .image-wrapper img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            transition: transform 0.3s;
        }
        .image-wrapper:hover img { transform: scale(1.05); }
        .image-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(transparent, rgba(0,0,0,0.8));
            color: white;
            padding: 10px;
            text-align: center;
            font-size: 14px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .image-wrapper:hover .image-overlay { opacity: 1; }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            animation: fadeIn 0.3s;
        }
        .modal-content {
            position: relative;
            margin: auto;
            padding: 20px;
            max-width: 90%;
            max-height: 90%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        .modal img {
            max-width: 100%;
            max-height: 80vh;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: white;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover { color: #ff4444; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        /* Cart */
        .cart {
            position: fixed;
            top: 120px;
            right: 20px;
            background: rgba(255,255,255,0.95);
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 350px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .checkout-form {
            background: rgba(255,255,255,0.9);
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        form { display: flex; flex-direction: column; gap: 15px; }
        input, textarea, select {
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #007bff;
        }
        button {
            background: linear-gradient(45deg, #007bff, #0056b3);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            padding: 12px;
            border-radius: 10px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,123,255,0.4);
        }
        .add-to-cart {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 12px;
            width: 100%;
            cursor: pointer;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s;
        }
        .add-to-cart:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(40,167,69,0.4);
        }

        /* Admin Panel */
        .admin-panel {
            background: rgba(255,243,205,0.9);
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .admin-search-container {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        #prodCategory {
            background: white;
            font-size: 16px;
            font-weight: 500;
        }
        #prodCategory option {
            padding: 10px;
            background: white;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #dee2e6;
            padding: 12px;
            text-align: left;
        }
        th {
            background: linear-gradient(45deg, #f8f9fa, #e9ecef);
            font-weight: bold;
        }
        .btn {
            padding: 6px 12px;
            margin: 0 2px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
        .btn-edit { background: #ffc107; color: #212529; }
        .btn-delete { background: #dc3545; color: white; }
        .btn-edit:hover { background: #e0a800; }
        .btn-delete:hover { background: #c82333; }

        /* Hidden & Messages */
        .hidden { display: none; }
        .orders {
            background: rgba(255,255,255,0.9);
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .message {
            padding: 15px;
            margin: 15px 0;
            border-radius: 10px;
            font-weight: 500;
        }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .cart-total {
            font-size: 24px;
            font-weight: bold;
            color: #28a745;
            margin: 15px 0;
        }
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }
        .status-pending { background: #ffc107; }
        .status-shipped { background: #28a745; }
        .status-delivered { background: #007bff; }
        .no-results {
            text-align: center;
            color: #999;
            font-size: 18px;
            margin: 50px 0;
        }

        /* MOBILE RESPONSIVE - FULLY OPTIMIZED */
        @media (max-width: 768px) {
            .container { padding: 10px; }
            nav { flex-direction: column; gap: 10px; padding: 10px; }
            .cart {
                position: static !important;
                max-width: none;
                margin: 20px 0;
            }
            .products {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            .search-box { max-width: 100%; }
            header { padding: 15px; }
            .category-btn {
                padding: 8px 12px;
                font-size: 14px;
                flex: 1;
                min-width: 120px;
            }
            .product { padding: 15px; }
            h2 { font-size: 20px; }
            button { padding: 10px; font-size: 16px; }
            table { font-size: 14px; }
            th, td { padding: 8px; }
        }

        @media (max-width: 480px) {
            .search-container, .admin-search-container { padding: 15px; }
            .product img { height: 180px; }
            .modal-content { margin: 10px; padding: 10px; }
            input, textarea, select { font-size: 16px; padding: 12px; }
            .btn { padding: 4px 8px; font-size: 11px; }
        }
    </style>
</head>
<body>
    <header>
        <h1>Anivique shop</h1>
        <p>Modern shopping experience with full admin control</p>
    </header>

    <nav>
        <button onclick="showSection('catalog')">Search Products</button>
        <button onclick="showSection('cart')">Cart <span id="cartCount">0</span></button>
        <button onclick="showSection('orders')">My Orders</button>
        <button onclick="showSection('login')">Login</button>
        <button onclick="showSection('register')">Register</button>
        <span id="userInfo"></span>
    </nav>

    <div class="container">
        <!-- Catalog with Search & Categories -->
        <section id="catalog">
            <h2>Find Products</h2>
            <div class="search-container">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Search shirts, shoes, electronics..." onkeyup="handleSearch(event)">
                    <button class="search-btn" onclick="performSearch()">🔍</button>
                </div>
            </div>
            <div class="categories" id="categories">
                <button class="category-btn active" data-category="all">All Products</button>
                <button class="category-btn" data-category="shirts">Shirts</button>
                <button class="category-btn" data-category="shoes">Shoes</button>
                <button class="category-btn" data-category="electronics">Electronics</button>
                <button class="category-btn" data-category="accessories">Accessories</button>
            </div>
            <div id="products" class="products"></div>
            <div id="noResults" class="no-results hidden">No products found</div>
        </section>

        <!-- Admin Panel with SEARCH & CATEGORIES -->
        <section id="adminPanel" class="admin-panel hidden">
            <h2>Admin Dashboard</h2>
            <!-- ADMIN SEARCH BAR -->
            <div class="admin-search-container">
                <h3>Filter Products</h3>
                <div class="search-box">
                    <input type="text" id="adminSearchInput" placeholder="Search products by name, category..." onkeyup="adminFilterProducts()">
                    <button class="search-btn" onclick="adminFilterProducts()">🔍</button>
                </div>
            </div>
            <div class="admin-categories">
                <div class="categories">
                    <button class="category-btn active" data-category="all" onclick="adminSetCategory('all')">All Products</button>
                    <button class="category-btn" data-category="shirts" onclick="adminSetCategory('shirts')">Shirts</button>
                    <button class="category-btn" data-category="shoes" onclick="adminSetCategory('shoes')">Shoes</button>
                    <button class="category-btn" data-category="electronics" onclick="adminSetCategory('electronics')">Electronics</button>
                    <button class="category-btn" data-category="accessories" onclick="adminSetCategory('accessories')">Accessories</button>
                </div>
            </div>

            <!-- UPDATED ADD PRODUCT FORM WITH CATEGORY DROPDOWN -->
            <form id="addProductForm">
                <input type="text" id="prodName" placeholder="Product Name" required>
                <input type="number" id="prodPrice" placeholder="Price" step="0.01" min="0" required>
                <input type="url" id="prodImage" placeholder="Image URL (https://images.unsplash.com...)" required>
                <!-- CATEGORY DROPDOWN -->
                <select id="prodCategory" required>
                    <option value="">Select Category</option>
                    <option value="shirts">Shirts</option>
                    <option value="shoes">Shoes</option>
                    <option value="electronics">Electronics</option>
                    <option value="accessories">Accessories</option>
                    <option value="general">General</option>
                </select>
                <textarea id="prodDesc" placeholder="Product Description (optional)"></textarea>
                <button type="submit">Add Product</button>
            </form>

            <h3>Products Management</h3>
            <table id="adminProducts">
                <thead>
                    <tr>
                        <th>ID</th><th>Name</th><th>Price</th><th>Image</th><th>Category</th><th>Sales</th><th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>

            <h3>Orders Management</h3>
            <table id="adminOrders">
                <thead>
                    <tr><th>ID</th><th>User</th><th>Items</th><th>Total</th><th>Status</th><th>Date</th><th>Actions</th></tr>
                </thead>
                <tbody></tbody>
            </table>
        </section>

        <!-- Cart -->
        <section id="cart" class="hidden">
            <h2>Shopping Cart</h2>
            <div id="cartItems"></div>
            <div class="cart-total" id="cartTotal">$0.00</div>
            <div class="checkout-form">
                <h3>Checkout</h3>
                <form id="checkoutForm">
                    <input type="text" id="customerName" placeholder="Full Name" required>
                    <input type="text" id="customerAddress" placeholder="Shipping Address" required>
                    <textarea id="imageDesc" placeholder="Special instructions or image description (optional)"></textarea>
                    <button type="submit">Place Order</button>
                </form>
            </div>
        </section>

        <!-- Orders -->
        <section id="orders" class="hidden">
            <h2>Your Orders</h2>
            <div id="userOrders" class="orders"></div>
        </section>

        <!-- Login -->
        <section id="login" class="hidden">
            <h2>Login</h2>
            <div class="checkout-form">
                <form id="loginForm">
                    <input type="email" id="loginEmail" placeholder="Email Address" required>
                    <input type="password" id="loginPass" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
            </div>
        </section>

        <!-- Register -->
        <section id="register" class="hidden">
            <h2>Register</h2>
            <div class="checkout-form">
                <form id="registerForm">
                    <input type="email" id="regEmail" placeholder="Email Address" required>
                    <input type="password" id="regPass" placeholder="Password (min 6 chars)" required>
                    <select id="regRole">
                        <option value="user">Customer</option>
                        <option value="admin">Admin</option>
                    </select>
                    <button type="submit">Create Account</button>
                </form>
            </div>
        </section>

        <div id="message"></div>
    </div>

    <!-- IMAGE MODAL -->
    <div id="imageModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <img id="modalImage">
            <div style="text-align:center;color:white;margin-top:15px;font-size:18px" id="modalTitle"></div>
        </div>
    </div>

    <script>
        let cart = JSON.parse(sessionStorage.getItem('cart') || '[]');
        let userId = sessionStorage.getItem('userId');
        let isAdmin = sessionStorage.getItem('isAdmin') === 'true';
        let allProducts;
        let currentSearch = '';
        let currentCategory = 'all';

        // ADMIN VARIABLES
        let adminAllProducts;
        let adminCurrentSearch = '';
        let adminCurrentCategory = 'all';

        function showSection(sectionId) {
            document.querySelectorAll('section').forEach(s => s.classList.add('hidden'));
            document.getElementById(sectionId).classList.remove('hidden');
            if (sectionId === 'catalog') loadProducts();
            if (sectionId === 'orders') loadOrders();
            if (sectionId === 'cart') loadCart();
            if (sectionId === 'adminPanel') loadAdminProducts();
            updateNav();
        }

        function updateNav() {
            const info = document.getElementById('userInfo');
            document.getElementById('cartCount').textContent = cart.length;
            if (userId) {
                info.innerHTML = isAdmin ? 'Admin | <a href="#" onclick="logout()" style="color:#ffc107">Logout</a>' : 'Customer';
                document.getElementById('adminPanel').classList.toggle('hidden', !isAdmin);
            } else {
                info.innerHTML = '';
            }
        }

        // IMAGE MODAL FUNCTIONS
        function openModal(imageSrc, productName) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const modalTitle = document.getElementById('modalTitle');
            modal.style.display = 'block';
            modalImg.src = imageSrc;
            modalTitle.textContent = productName;
            document.onkeydown = function(e) { if (e.key === 'Escape') closeModal(); }
        }
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
            document.onkeydown = null;
        }
        window.onclick = function(event) {
            const modal = document.getElementById('imageModal');
            if (event.target === modal) closeModal();
        }

        // CATALOG FUNCTIONS
        async function loadProducts() {
            const res = await fetch('/api/products');
            allProducts = await res.json();
            displayProducts(allProducts);
        }
        function handleSearch(event) { if (event.key === 'Enter') performSearch(); }
        function performSearch() {
            currentSearch = document.getElementById('searchInput').value.toLowerCase().trim();
            filterAndDisplayProducts();
        }
        function setCategory(category) {
            currentCategory = category;
            document.querySelectorAll('#categories .category-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.category === category);
            });
            filterAndDisplayProducts();
        }
        function filterAndDisplayProducts() {
            let filtered = allProducts;
            if (currentSearch) {
                filtered = filtered.filter(p =>
                    p.name.toLowerCase().includes(currentSearch) ||
                    p.description.toLowerCase().includes(currentSearch) ||
                    p.category.toLowerCase().includes(currentSearch)
                );
            }
            if (currentCategory !== 'all') {
                filtered = filtered.filter(p => p.category.toLowerCase() === currentCategory);
            }
            displayProducts(filtered);
        }
        function displayProducts(products) {
            const container = document.getElementById('products');
            const noResults = document.getElementById('noResults');
            if (products.length === 0) {
                container.innerHTML = '';
                noResults.classList.remove('hidden');
            } else {
                container.innerHTML = products.map(p => `
                    <div class="product">
                        <div class="image-wrapper" onclick="openModal('${p.image}', '${p.name}')">
                            <img src="${p.image}" alt="${p.name}" onerror="this.src='https://via.placeholder.com/280x200/ddd?text=No+Image'">
                            <div class="image-overlay">Click to Zoom</div>
                        </div>
                        <h3>${p.name}</h3>
                        <p style="font-size:14px;color:#666">${p.category}</p>
                        <p style="font-size:18px;font-weight:bold;color:#28a745">$${parseFloat(p.price).toFixed(2)}</p>
                        <p>${p.description || 'Great product!'}</p>
                        <button class="add-to-cart" onclick="addToCart(${p.id})">Add to Cart</button>
                    </div>
                `).join('');
                noResults.classList.add('hidden');
            }
        }

        // CATEGORY BUTTONS
        document.getElementById('categories').addEventListener('click', function(e) {
            if (e.target.classList.contains('category-btn')) {
                setCategory(e.target.dataset.category);
            }
        });

        // ADMIN FUNCTIONS
        async function loadAdminProducts() {
            const res = await fetch('/api/products');
            adminAllProducts = await res.json();
            adminDisplayProducts(adminAllProducts);
        }
        function adminFilterProducts() {
            adminCurrentSearch = document.getElementById('adminSearchInput').value.toLowerCase().trim();
            adminFilterAndDisplay();
        }
        function adminSetCategory(category) {
            adminCurrentCategory = category;
            document.querySelectorAll('.admin-categories .category-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.category === category);
            });
            adminFilterAndDisplay();
        }
        function adminFilterAndDisplay() {
            let filtered = adminAllProducts;
            if (adminCurrentSearch) {
                filtered = filtered.filter(p =>
                    p.name.toLowerCase().includes(adminCurrentSearch) ||
                    p.category.toLowerCase().includes(adminCurrentSearch) ||
                    p.description?.toLowerCase().includes(adminCurrentSearch)
                );
            }
            if (adminCurrentCategory !== 'all') {
                filtered = filtered.filter(p => p.category.toLowerCase() === adminCurrentCategory);
            }
            adminDisplayProducts(filtered);
        }
        function adminDisplayProducts(products) {
            const tbody = document.querySelector('#adminProducts tbody');
            if (products.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#999;padding:30px">No products match your filter</td></tr>';
                return;
            }
            tbody.innerHTML = products.map(p => `
                <tr>
                    <td>${p.id}</td>
                    <td>${p.name}</td>
                    <td>$${parseFloat(p.price).toFixed(2)}</td>
                    <td><img src="${p.image}" style="width:50px;height:50px;object-fit:cover;border-radius:5px" onerror="this.src=\'https://via.placeholder.com/50?text=No+Img\'"></td>
                    <td><span style="text-transform:capitalize">${p.category}</span></td>
                    <td>${p.sales || 0}</td>
                    <td>
                        <button class="btn btn-edit" onclick="editProduct(${p.id})">Edit</button>
                        <button class="btn btn-delete" onclick="deleteProduct(${p.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        }

        // UPDATED ADD PRODUCT FORM HANDLER - handles dropdown
        document.getElementById('addProductForm').addEventListener('submit', async e => {
            e.preventDefault();
            const data = {
                name: document.getElementById('prodName').value,
                price: parseFloat(document.getElementById('prodPrice').value),
                image: document.getElementById('prodImage').value,
                description: document.getElementById('prodDesc').value,
                category: document.getElementById('prodCategory').value  // Gets from dropdown
            };
            const res = await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if (res.ok) {
                showMessage('Product added successfully!', 'success');
                e.target.reset();
                loadAdminProducts();
                loadProducts();
            } else {
                showMessage('Error adding product', 'error');
            }
        });

        function addToCart(id) {
            cart.push(id);
            sessionStorage.setItem('cart', JSON.stringify(cart));
            showMessage('Added to cart!', 'success');
            updateNav();
        }

        function loadCart() {
            const uniqueCart = [...new Set(cart)];
            const cartItems = document.getElementById('cartItems');
            if (uniqueCart.length === 0) {
                cartItems.innerHTML = '<p style="text-align:center;color:#999">Your cart is empty</p>';
                document.getElementById('cartTotal').textContent = '$0.00';
                return;
            }
            Promise.all(uniqueCart.map(id =>
                fetch(`/api/products/${id}`).then(r => r.json()).catch(() => null)
            )).then(products => {
                cartItems.innerHTML = products.map((p, i) =>
                    p ? `
                        <div style="border-bottom:1px solid #eee;padding:10px 0">
                            <strong>${p.name}</strong> - $${p.price}
                        </div>
                    ` : `<div>Item ${uniqueCart[i]} unavailable</div>`
                ).join('');
                const total = products.reduce((sum, p) => sum + (p ? parseFloat(p.price) : 0), 0);
                document.getElementById('cartTotal').textContent = `$${total.toFixed(2)}`;
            });
        }

        document.getElementById('checkoutForm').addEventListener('submit', async e => {
            e.preventDefault();
            if (!userId) return showMessage('Please login first!', 'error');
            if (cart.length === 0) return showMessage('Cart is empty!', 'error');
            const data = {
                userid: userId,
                items: cart,
                total: parseFloat(document.getElementById('cartTotal').textContent.replace('$', '')),
                customername: document.getElementById('customerName').value,
                customeraddress: document.getElementById('customerAddress').value,
                imagedesc: document.getElementById('imageDesc').value
            };
            const res = await fetch('/api/orders', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if (res.ok) {
                cart = [];
                sessionStorage.setItem('cart', JSON.stringify(cart));
                showMessage('Order placed successfully!', 'success');
                loadCart();
                e.target.reset();
            } else {
                showMessage('Error placing order', 'error');
            }
        });

        async function loadOrders() {
            if (!userId) return;
            const res = await fetch(`/api/orders?userid=${userId}`);
            const orders = await res.json();
            document.getElementById('userOrders').innerHTML = orders.length ? orders.map(order => `
                <div class="message success">
                    <strong>Order #${order.id}</strong> - $${order.total.toFixed(2)}
                    <span class="status-badge status-${order.status}">${order.status.toUpperCase()}</span><br>
                    ${order.customername} - ${new Date(order.created_at).toLocaleDateString()}
                </div>
            `).join('') : '<p>No orders yet</p>';
        }

        document.getElementById('loginForm').addEventListener('submit', async e => {
            e.preventDefault();
            const data = {
                email: document.getElementById('loginEmail').value,
                password: document.getElementById('loginPass').value
            };
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            if (res.ok) {
                sessionStorage.setItem('userId', result.userid);
                sessionStorage.setItem('isAdmin', result.isadmin);
                userId = result.userid;
                isAdmin = result.isadmin;
                showMessage('Login successful!', 'success');
                updateNav();
            } else {
                showMessage(result.error || 'Login failed', 'error');
            }
        });

        document.getElementById('registerForm').addEventListener('submit', async e => {
            e.preventDefault();
            const data = {
                email: document.getElementById('regEmail').value,
                password: document.getElementById('regPass').value,
                role: document.getElementById('regRole').value
            };
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if (res.ok) {
                showMessage('Registration successful! Please login.', 'success');
                e.target.reset();
            } else {
                showMessage('Registration failed - email may exist', 'error');
            }
        });

        function showMessage(text, type) {
            const msg = document.getElementById('message');
            msg.textContent = text;
            msg.className = `message ${type}`;
            setTimeout(() => msg.className += ' hidden', 3000);
        }

        function logout() {
            sessionStorage.clear();
            userId = null;
            isAdmin = false;
            updateNav();
            showMessage('Logged out successfully', 'success');
        }

        // ADMIN CRUD FUNCTIONS
        async function deleteProduct(id) {
            if (confirm('Delete this product?')) {
                await fetch(`/api/products/${id}`, { method: 'DELETE' });
                showMessage('Product deleted!', 'success');
                loadAdminProducts();
                loadProducts();
            }
        }

        async function editProduct(id) {
            const product = adminAllProducts.find(p => p.id == id);
            if (product) {
                document.getElementById('prodName').value = product.name;
                document.getElementById('prodPrice').value = product.price;
                document.getElementById('prodImage').value = product.image;
                document.getElementById('prodCategory').value = product.category;
                document.getElementById('prodDesc').value = product.description;

                // Change form to update mode
                const form = document.getElementById('addProductForm');
                form.onsubmit = async e => {
                    e.preventDefault();
                    const data = {
                        name: document.getElementById('prodName').value,
                        price: parseFloat(document.getElementById('prodPrice').value),
                        image: document.getElementById('prodImage').value,
                        description: document.getElementById('prodDesc').value,
                        category: document.getElementById('prodCategory').value
                    };
                    await fetch(`/api/products/${id}`, {
                        method: 'PUT',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    showMessage('Product updated!', 'success');
                    form.onsubmit = null; // Reset to add mode
                    form.reset();
                    loadAdminProducts();
                    loadProducts();
                    form.lastElementChild.textContent = 'Add Product';
                };
                form.lastElementChild.textContent = 'Update Product';
            }
        }

        // Initialize
        updateNav();
        showSection('catalog');
    </script>
</body>
</html>
"""

def init_db():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()

    # Database setup
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        image TEXT,
        description TEXT,
        category TEXT DEFAULT 'general',
        sales INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userid INTEGER,
        items TEXT,
        total REAL,
        customername TEXT,
        customeraddress TEXT,
        imagedesc TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(userid) REFERENCES users (id)
    )''')

    # Sample products
    c.execute("SELECT COUNT(*) FROM products WHERE name='Premium Cotton Shirt'")
    if not c.fetchone()[0]:
        sample_products = [
            ("Premium Cotton Shirt", 29.99, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400", "Comfortable 100% cotton shirt", "shirts"),
            ("Wireless Headphones", 89.99, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", "Premium sound quality", "electronics"),
            ("Running Shoes", 79.99, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400", "Lightweight running shoes", "shoes"),
            ("Leather Wallet", 39.99, "https://images.unsplash.com/photo-1618221195710-dd2dabb60b29?w=400", "Genuine leather wallet", "accessories"),
            ("Graphic T-Shirt", 24.99, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400", "Cool graphic tee", "shirts"),
        ]
        c.executemany("INSERT INTO products (name, price, image, description, category) VALUES (?, ?, ?, ?, ?)", sample_products)

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/products')
def get_products():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = []
    for row in c.fetchall():
        products.append({
            'id': row[0], 'name': row[1], 'price': row[2], 'image': row[3],
            'description': row[4], 'category': row[5], 'sales': row[6]
        })
    conn.close()
    return jsonify(products)

@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify({
            'id': row[0], 'name': row[1], 'price': row[2], 'image': row[3],
            'description': row[4], 'category': row[5], 'sales': row[6]
        })
    return jsonify({}), 404

@app.route('/api/products', methods=['POST'])
def add_product():
    if session.get('isadmin') != '1':
        return 'Admin access required', 403
    data = request.json
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''INSERT INTO products (name, price, image, description, category)
                 VALUES (?, ?, ?, ?, ?)''',
              (data['name'], data['price'], data['image'], data['description'], data.get('category', 'general')))
    conn.commit()
    conn.close()
    return 'Product added successfully', 200

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if session.get('isadmin') != '1':
        return 'Admin access required', 403
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return 'Product deleted successfully', 200

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if session.get('isadmin') != '1':
        return 'Admin access required', 403
    data = request.json
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''UPDATE products SET name=?, price=?, image=?, description=?, category=?
                 WHERE id=?''', (data['name'], data['price'], data['image'], data['description'], data['category'], product_id))
    conn.commit()
    conn.close()
    return 'Product updated successfully', 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    hashed_pw = hashlib.sha256(data['password'].encode()).hexdigest()
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                  (data['email'], hashed_pw, data['role']))
        conn.commit()
        return 'Registration successful', 200
    except sqlite3.IntegrityError:
        return 'Email already exists', 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    hashed_pw = hashlib.sha256(data['password'].encode()).hexdigest()
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT id, role FROM users WHERE email = ? AND password = ?', (data['email'], hashed_pw))
    user = c.fetchone()
    conn.close()
    if user:
        session['userid'] = user[0]
        session['isadmin'] = '1' if user[1] == 'admin' else '0'
        return jsonify({'userid': user[0], 'isadmin': user[1] == 'admin'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/orders')
def get_orders():
    userid = request.args.get('userid')
    if not userid:
        return jsonify([])
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE userid = ? ORDER BY created_at DESC', (userid,))
    orders = []
    for row in c.fetchall():
        orders.append({
            'id': row[0], 'userid': row[1], 'items': row[2], 'total': row[3],
            'customername': row[4], 'status': row[7], 'created_at': row[8]
        })
    conn.close()
    return jsonify(orders)

@app.route('/api/orders', methods=['POST'])
def create_order():
    if not session.get('userid'):
        return 'Login required', 401
    data = request.json
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''INSERT INTO orders (userid, items, total, customername, customeraddress, imagedesc)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (data['userid'], json.dumps(data['items']), data['total'], data['customername'], data['customeraddress'], data['imagedesc']))
    conn.commit()
    conn.close()
    return 'Order created', 201

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
