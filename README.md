# Week 2: Express.js – Products API

This project is a RESTful API built with **Express.js** for managing products. It includes standard CRUD operations, middleware for logging and authentication, validation, error handling, and advanced features like filtering, search, and pagination.

---

## **Table of Contents**
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Examples](#examples)
- [Error Handling](#error-handling)



1. Clone your GitHub Classroom repository:
```bash
git clone <your-github-classroom-repo-url>
cd <repo-folder>/express-api
Install dependencies:
bash
npm install
Create a .env file based on .env.example:

env
PORT=3000
API_KEY=my-secret-key

Running the Server
bash
node server.js
Server runs on http://localhost:3000/

Root endpoint / returns:

nginx
Hello World!
Environment Variables
Variable	Description
PORT	Port the server listens on (default 3000)
API_KEY	API key required for authentication

API Endpoints
Root
GET /
Returns a simple "Hello World!" message.

Products
GET /api/products
List all products

Supports optional query parameters:

category → filter by category

search → search by product name

page → page number (default 1)

limit → items per page (default 10)

GET /api/products/:id
Get a product by its id

POST /api/products
Create a new product

Headers: x-api-key: my-secret-key

Body (JSON):

json
{
  "name": "Laptop",
  "description": "Powerful gaming laptop",
  "price": 1200,
  "category": "electronics",
  "inStock": true
}
PUT /api/products/:id
Update an existing product by id

Headers: x-api-key: my-secret-key

Body: Same as POST

DELETE /api/products/:id
Delete a product by id

Headers: x-api-key: my-secret-key



Create a product
bash
POST /api/products
Headers:
  x-api-key: my-secret-key
Body:
{
  "name": "Smartphone",
  "description": "Latest model",
  "price": 800,
  "category": "electronics",
  "inStock": true
}

Filter products by category
bash
GET /api/products?category=electronics&page=1&limit=5


Search products by name
bash
GET /api/products?search=laptop
Middleware
Logger: Logs request method, URL, and timestamp

Authentication: Checks x-api-key header

Validation: Ensures all required product fields are provided

Error Handling
404 Not Found: Product does not exist

400 Validation Error: Missing or invalid product data

401 Unauthorized: Missing or invalid API key

All errors return JSON:

