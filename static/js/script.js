document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('fetch-inventory').addEventListener('click', fetchInventory);
    document.getElementById('add-item-form').addEventListener('submit', addItem);
    document.getElementById('update-item-form').addEventListener('submit', updateItem);
    document.getElementById('check-stock-form').addEventListener('submit', checkStock);
    document.getElementById('place-order-form').addEventListener('submit', placeOrder);
    document.getElementById('predict-demand-form').addEventListener('submit', predictDemand);
});

function fetchInventory() {
    fetch('/inventory')
        .then(response => response.json())
        .then(data => {
            const inventoryList = document.getElementById('inventory-list');
            inventoryList.innerHTML = JSON.stringify(data, null, 2);
        })
        .catch(error => console.error('Error fetching inventory:', error));
}

function addItem(event) {
    event.preventDefault();
    const itemName = document.getElementById('item-name').value;
    const itemQuantity = document.getElementById('item-quantity').value;

    fetch('/inventory', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: itemName, quantity: itemQuantity })
    })
    .then(response => response.json())
    .then(data => {
        alert('Item added: ' + JSON.stringify(data));
        fetchInventory(); // Refresh the inventory list
    })
    .catch(error => console.error('Error adding item:', error));
}

function updateItem(event) {
    event.preventDefault();
    const itemId = document.getElementById('update-item-id').value;
    const newQuantity = document.getElementById('update-item-quantity').value;

    fetch(`/inventory/${itemId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ quantity: newQuantity })
    })
    .then(response => response.json())
    .then(data => {
        alert('Item updated: ' + JSON.stringify(data));
        fetchInventory(); // Refresh the inventory list
    })
    .catch(error => console.error('Error updating item:', error));
}

function checkStock(event) {
    event.preventDefault();
    const itemId = document.getElementById('stock-item-id').value;

    fetch('/inventory/check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item_id: itemId })
    })
    .then(response => response.json())
    .then(data => {
        const stockResult = document.getElementById('stock-result');
        stockResult.innerHTML = JSON.stringify(data, null, 2);
    })
    .catch(error => console.error('Error checking stock:', error));
}

function placeOrder(event) {
    event.preventDefault();
    const itemId = document.getElementById('order-item-id').value;
    const quantity = document.getElementById('order-quantity').value;

    fetch('/order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item_id: itemId, quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        alert('Order placed: ' + JSON.stringify(data));
        fetchInventory(); // Refresh the inventory list
    })
    .catch(error => console.error('Error placing order:', error));
}

function predictDemand(event) {
    event.preventDefault();
    const productId = document.getElementById('predict-product-id').value;
    const demand = document.getElementById('predict-demand').value;

    fetch('/predict_demand', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ product_id: productId, Demand: demand })
    })
    .then(response => response.json())
    .then(data => {
        const predictionResult = document.getElementById('prediction-result');
        predictionResult.innerHTML = JSON.stringify(data, null, 2);
    })
    .catch(error => console.error('Error predicting demand:', error));
}
