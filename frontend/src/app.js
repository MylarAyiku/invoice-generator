const API = '/api';
let currentInvoiceId = null;
let items = [];

// ---- Navigation ----
function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`page-${page}`).classList.add('active');
    event.target.classList.add('active');
    if (page === 'history') loadHistory();
}

// ---- Items ----
function addItem() {
    const id = Date.now();
    items.push({ id, description: '', quantity: 1, unit_price: 0 });
    renderItems();
}

function removeItem(id) {
    items = items.filter(i => i.id !== id);
    renderItems();
    updateTotals();
}

function renderItems() {
    const list = document.getElementById('items-list');
    list.innerHTML = items.map(item => `
        <div class="item-row">
            <input type="text" placeholder="Description" value="${item.description}"
                oninput="updateItem(${item.id}, 'description', this.value)" />
            <input type="number" min="0" value="${item.quantity}"
                oninput="updateItem(${item.id}, 'quantity', parseFloat(this.value) || 0)" />
            <input type="number" min="0" step="0.01" value="${item.unit_price}"
                oninput="updateItem(${item.id}, 'unit_price', parseFloat(this.value) || 0)" />
            <div class="amount">$${(item.quantity * item.unit_price).toFixed(2)}</div>
            <button class="remove-btn" onclick="removeItem(${item.id})">✕</button>
        </div>
    `).join('');
    updateTotals();
}

function updateItem(id, field, value) {
    const item = items.find(i => i.id === id);
    if (item) { item[field] = value; updateTotals(); renderItems(); }
}

function updateTotals() {
    const subtotal = items.reduce((sum, i) => sum + (i.quantity * i.unit_price), 0);
    const taxRate = parseFloat(document.getElementById('tax_rate').value) || 0;
    const taxAmount = subtotal * (taxRate / 100);
    const total = subtotal + taxAmount;
    document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('tax_amount').textContent = `$${taxAmount.toFixed(2)}`;
    document.getElementById('total').textContent = `$${total.toFixed(2)}`;
}

// ---- Submit ----
async function submitInvoice() {
    const payload = {
        sender_name: document.getElementById('sender_name').value,
        sender_email: document.getElementById('sender_email').value,
        sender_address: document.getElementById('sender_address').value,
        client_name: document.getElementById('client_name').value,
        client_email: document.getElementById('client_email').value,
        client_address: document.getElementById('client_address').value,
        items: items.map(({ description, quantity, unit_price }) => ({ description, quantity, unit_price })),
        tax_rate: parseFloat(document.getElementById('tax_rate').value) || 0,
        notes: document.getElementById('notes').value
    };

    if (!payload.sender_name || !payload.client_name || items.length === 0) {
        alert('Please fill in your details, client details, and add at least one item.');
        return;
    }

    try {
        const res = await fetch(`${API}/invoices/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Failed to create invoice');
        const data = await res.json();
        currentInvoiceId = data.id;

        document.getElementById('invoice-number').textContent = data.invoice_number;
        document.getElementById('success-banner').classList.remove('hidden');
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    } catch (err) {
        alert('Error creating invoice. Make sure the backend is running.');
    }
}

// ---- PDF ----
function downloadPDF() {
    if (currentInvoiceId) {
        window.open(`${API}/pdf/${currentInvoiceId}`, '_blank');
    }
}

// ---- History ----
async function loadHistory() {
    try {
        const res = await fetch(`${API}/invoices/`);
        const invoices = await res.json();
        const list = document.getElementById('history-list');

        if (invoices.length === 0) {
            list.innerHTML = '<p style="color:#64748b">No invoices yet.</p>';
            return;
        }

        list.innerHTML = invoices.map(inv => `
            <div class="history-item">
                <div class="inv-info">
                    <h3>${inv.invoice_number}</h3>
                    <p>${inv.client_name} · ${new Date(inv.created_at).toLocaleDateString()}</p>
                </div>
                <div class="inv-amount">$${inv.total.toFixed(2)}</div>
                <button class="btn-secondary" onclick="window.open('${API}/pdf/${inv.id}', '_blank')">
                    Download PDF
                </button>
            </div>
        `).join('');
    } catch (err) {
        document.getElementById('history-list').innerHTML = '<p style="color:#ef4444">Failed to load invoices.</p>';
    }
}

// Init
addItem();