const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const auth = require('../middleware/auth');
const { validateProduct } = require('../middleware/validation');
const NotFoundError = require('../errors/NotFoundError');

let products = []; // In-memory storage for demo

// GET all products with optional filtering & pagination
router.get('/', (req, res) => {
    const { category, page = 1, limit = 10, search } = req.query;
    let result = products;

    if (category) {
        result = result.filter(p => p.category === category);
    }
    if (search) {
        result = result.filter(p => p.name.toLowerCase().includes(search.toLowerCase()));
    }

    // Pagination
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + parseInt(limit);
    result = result.slice(startIndex, endIndex);

    res.json(result);
});

// GET product by ID
router.get('/:id', (req, res, next) => {
    const product = products.find(p => p.id === req.params.id);
    if (!product) return next(new NotFoundError('Product not found'));
    res.json(product);
});

// POST create product
router.post('/', auth, validateProduct, (req, res) => {
    const newProduct = { id: uuidv4(), ...req.body };
    products.push(newProduct);
    res.status(201).json(newProduct);
});

// PUT update product
router.put('/:id', auth, validateProduct, (req, res, next) => {
    const index = products.findIndex(p => p.id === req.params.id);
    if (index === -1) return next(new NotFoundError('Product not found'));
    products[index] = { ...products[index], ...req.body };
    res.json(products[index]);
});

// DELETE product
router.delete('/:id', auth, (req, res, next) => {
    const index = products.findIndex(p => p.id === req.params.id);
    if (index === -1) return next(new NotFoundError('Product not found'));
    products.splice(index, 1);
    res.json({ message: 'Product deleted' });
});

module.exports = router;
