const ValidationError = require('../errors/ValidationError');

function validateProduct(req, res, next) {
    const { name, description, price, category, inStock } = req.body;
    if (!name || !description || price === undefined || !category || inStock === undefined) {
        return next(new ValidationError('Invalid product data'));
    }
    next();
}

module.exports = { validateProduct };
