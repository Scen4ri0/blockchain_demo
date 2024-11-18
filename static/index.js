async function addBlock() {
    const blockData = document.getElementById("blockData").value.trim();
    if (!blockData) {
        alert("Please enter block data.");
        return;
    }

    try {
        const response = await fetch('/api/add_block', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ data: blockData }),
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById("output").innerText = result.message;
        } else {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error("Error adding block:", error);
        document.getElementById("output").innerText = `Failed to add block: ${error.message}`;
    }
}

async function validateBlockchain() {
    const response = await fetch('/api/validate');
    const result = await response.json();

    const outputDiv = document.getElementById("output");
    outputDiv.innerHTML = ""; // Очистка предыдущего вывода

    // Показ результата валидации
    const resultText = document.createElement("div");
    resultText.textContent = result.steps[0].details;
    resultText.style.color = result.valid ? "green" : "red";
    resultText.style.fontWeight = "bold";
    resultText.style.marginBottom = "20px";
    outputDiv.appendChild(resultText);

    // Отображение отладочной информации
    result.steps.slice(1).forEach(step => {
        const stepDiv = document.createElement("div");
        stepDiv.className = "validation-step";
        stepDiv.style.border = step.status === "valid" ? "1px solid green" : "1px solid red";
        stepDiv.style.backgroundColor = step.status === "valid" ? "#e8ffe8" : "#ffe8e8";

        const blockInfo = document.createElement("p");
        blockInfo.textContent = `Block: ${step.block}`;
        stepDiv.appendChild(blockInfo);

        const stepInfo = document.createElement("p");
        stepInfo.textContent = `Step: ${step.step}`;
        stepDiv.appendChild(stepInfo);

        const details = document.createElement("p");
        details.textContent = `Details: ${step.details}`;
        stepDiv.appendChild(details);

        outputDiv.appendChild(stepDiv);
    });
}
async function createTransaction() {
    const sender = document.getElementById("transactionSender").value;
    const recipient = document.getElementById("transactionRecipient").value;
    const amount = document.getElementById("transactionAmount").value;

    const response = await fetch('/api/create_transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sender, recipient, amount }),
    });
    const result = await response.json();
    alert(result.message || result.error);
}

async function fetchPendingTransactions() {
    const response = await fetch('/api/pending_transactions');
    const transactions = await response.json();

    const outputDiv = document.getElementById("pendingTransactionsOutput");
    outputDiv.innerHTML = ""; // Очистка предыдущих данных

    transactions.forEach(tx => {
        const txDiv = document.createElement("div");
        txDiv.className = "validation-step";
        txDiv.style.border = "1px solid #ccc";
        txDiv.style.marginBottom = "10px";
        txDiv.style.padding = "10px";
        txDiv.innerHTML = `
            <p><strong>Sender:</strong> ${tx.sender}</p>
            <p><strong>Recipient:</strong> ${tx.recipient}</p>
            <p><strong>Amount:</strong> ${tx.amount}</p>
        `;
        outputDiv.appendChild(txDiv);
    });
}


// Initial fetch to populate the chain
fetchChain();