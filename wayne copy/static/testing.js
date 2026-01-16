const container = document.getElementById('container');
const masterModal = document.getElementById('masterModal');
const modalBody = document.getElementById('dynamicModalBody');
const modalTitle = document.getElementById('modalHeaderTitle');
const primaryBtn = document.getElementById('modalPrimaryBtn');
const tableBody = document.getElementById('transaction-body');

// --- 1. THE DYNAMIC MODAL OPENER ---
function openActionModal(mode) {
    masterModal.className = "modal-container"; // Shows modal
    container.classList.add('blurred');
    modalBody.innerHTML = ""; // Clear old content

    if (mode === 'add') {
        modalTitle.innerText = "Record a manual transaction";
        modalBody.innerHTML = `
            <div class="transaction-form">
                <label>Amount (MWK)</label>
                <input type="number" id="amountIn" placeholder="0.00" class="search-bar" style="width:100%; margin-bottom:10px;">
                <label>From/To</label>
                <input type="text" id="fromToIn" placeholder="e.g. Bank -> Food" class="search-bar" style="width:100%; margin-bottom:10px;">
                <label>Description</label>
                <input type="text" id="descIn" placeholder="What was this for?" class="search-bar" style="width:100%; margin-bottom:10px;">
                <label>Date</label>
                <input type="date" id="dateIn" class="search-bar" style="width:100%;">
            </div>
        `;
        primaryBtn.innerText = "Record Transaction";
        primaryBtn.onclick = saveTransaction;

    } else if (mode === 'review') {
        modalTitle.innerText = "Audit & Review";
        modalBody.innerHTML = `
            <p>Scanning your recent entries for AI-detected discrepancies...</p>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db;">
                <strong>Status:</strong> All entries are currently synchronized with your cloud database.
            </div>
        `;
        primaryBtn.innerText = "Close Review";
        primaryBtn.onclick = closeMasterModal;

    } else if (mode === 'import') {
        modalTitle.innerText = "Import Data";
        modalBody.innerHTML = `
            <p>Select your statement source:</p>
            <select class="search-bar" style="width:100%; margin-bottom:15px;">
                <option>Bank Statement (PDF)</option>
                <option>Airtel Money SMS History</option>
                <option>Standard CSV/Excel</option>
            </select>
            <input type="file" style="margin-top:10px;">
        `;
        primaryBtn.innerText = "Process Import";
        primaryBtn.onclick = () => alert("Import service starting...");
    }
}

function closeMasterModal() {
    masterModal.className = "hidden";
    container.classList.remove('blurred');
}

// --- 2. LOAD DATA FROM API ---
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const data = await response.json();
        tableBody.innerHTML = '';

        // Inside loadTransactions()
        data.forEach(trans => {
            const row = `<tr>
                <td>${trans.date}</td>
                <td>${trans.description}</td>
                <td>${trans.fromTo}</td>
                <td>${trans.Direction}</td>
                <td>${trans.amount}</td>
                <td>
                    <button onclick="deleteTransaction('${trans.id}')" class="btn-delete">
                        Delete
                    </button>
                </td>
            </tr>`;
            tableBody.innerHTML += row;
        });
    } catch (error) {
        console.error("Load Error:", error);
    }

// The Delete Function
async function deleteTransaction(transID) {
    if (!confirm("Permanently delete this record?")) return;

    try {
        const response = await fetch('/api/transactions/delete', {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            // Ensure the key matches what Flask data.get('transID') looks for
            body: JSON.stringify({ "transID": transID }) 
        });

        if (response.ok) {
            // Refresh the table to show it's gone
            loadTransactions(); 
        } else {
            const err = await response.json();
            alert("Delete failed: " + err.error);
        }
    } catch (error) {
        console.error("Delete Error:", error);
    } 


// --- 3. SAVE DATA ---
async function saveTransaction() {
    const payload = {
        amount: document.getElementById('amountIn').value,
        fromTo: document.getElementById('fromToIn').value,
        description: document.getElementById('descIn').value,
        date: document.getElementById('dateIn').value,
        direction: "Outbound" // Defaulting or you can add a select
    };

    const response = await fetch('/api/transactions', {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (response.ok) {
        closeMasterModal();
        loadTransactions();
    }
}

// Initial Load
loadTransactions();
}    }      