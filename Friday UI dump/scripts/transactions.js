const tableBody = document.getElementById('transaction-table-body');
const form = document.getElementById("new-transaction"); 
const editForm = document.getElementById("edit-transaction-form");
const userID = "something";

// 1. Load History
async function loadTransactions() {
    try {
        let response = await fetch('link.link');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        let transactions = await response.json();
        tableBody.innerHTML = '';
        
        transactions.forEach(element => {
            const rowID = `txn-${element.id}`;
            const row = `
            <tr id="${rowID}">
                <td>${element.date}</td>
                <td>${element.from} -> ${element.to}</td>
                <td>${element.description}</td>
                <td>${Number(element.amount).toLocaleString()}</td>
                <td>
                    <div class="table-btn">
                        <button onclick="handleEdit('${rowID}')" class="btn-edit">
                            <img src="../icons/edit-2-svgrepo-com.svg" alt="Edit">
                        </button>
                        <button onclick="deleteTransaction('${rowID}')" class="btn-delete">
                            <img src="../icons/delete-1487-svgrepo-com.svg" alt="Delete">
                        </button>
                    </div>
                </td>
            </tr>`;  
            tableBody.insertAdjacentHTML('beforeend', row);
        });
    } catch (error) {
        console.error("Failed to fetch", error);
    }
}

// 2. Form Submission
async function newTransaction() {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    if(data.amount) data.amount = Number(data.amount); // Ensure amount is a number for the database
    try {
        const response = await fetch('link.link', {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error("Server rejected the post");
        
        await response.json();
        loadTransactions(); // Refresh table
        form.reset();       // Clear form
    } catch (error) {
        console.error("Failed to post", error);
    }
}

// 3. Delete Transaction
async function deleteTransaction(transID) {
    try {
        const response = await fetch('deletelink.link', {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ transID, userID }),
        });

        if (response.ok) {
            const row = document.getElementById(transID);
            if (row) row.remove();
            console.log("Deleted successfully");
        } else {
            alert("Failed to delete");
        }
    } catch (error) {
        console.error("Failed to delete", error);
    }
}

// 4. Editing functions

function handleEdit(transID) {
    const row = document.getElementById(transID);
    const date = row.cells[0].innerText;
    const category = row.cells[1].innerText; // "Airtel -> Food"
    const desc = row.cells[2].innerText;
    const amount = row.cells[3].innerText.replace(/,/g, ''); // Remove commas for the input

    // 3. Fill your SECOND form's inputs
    editForm.querySelector('[name="edit-date"]').value = date;
    editForm.querySelector('[name="edit-description"]').value = desc;
    editForm.querySelector('[name="edit-amount"]').value = amount;
    editForm.dataset.editingId = transID;
    showEditModal();
}


async function editTransaction(){
    const formData = new FormData(editForm);
    const updatedData = Object.fromEntries(formData.entries());
    if(updatedData.amount) updatedData.amount = Number(updatedData.amount);
    const transID = editForm.dataset.editingId;
    const numericId = transID.replace('txn-', '');
    const finalData = {
        ...updatedData,
        id : numericId,
        userID: userID
    }; 
    try{
        const response = await fetch('update.link', {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(finalData),
        });
        hideEditModal();
        if (response.ok) {
            loadTransactions();
            console.log("Edited successfully");
        } else {
            alert("Failed to update");
        }
    } catch (error){
        console.error("Failed to edit", error);
    }
}

// Event Listeners
form.addEventListener('submit', (event) => {
    event.preventDefault();
    newTransaction();
});
editForm.addEventListener('submit', (event) => {
    event.preventDefault();
    editTransaction();
});
// Initial Load
loadTransactions();