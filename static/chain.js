async function fetchChain() {
    try {
        const response = await fetch('/api/chain');
        const chain = await response.json();

        const chainDiv = document.getElementById("blockchainOutput");
        chainDiv.innerHTML = ""; // Очистка предыдущих данных

        chain.forEach(block => {
            const blockDiv = document.createElement("div");
            blockDiv.className = "validation-step";
            blockDiv.style.border = "1px solid #ccc";
            blockDiv.style.borderRadius = "10px";
            blockDiv.style.backgroundColor = "#f9f9f9";
            blockDiv.style.padding = "15px";
            blockDiv.style.marginBottom = "15px";

            blockDiv.innerHTML = `
                <h3>Index: ${block.index}</h3>
                <p><strong>Timestamp:</strong> ${new Date(block.timestamp * 1000).toLocaleString()}</p>
                <p><strong>Hash:</strong> ${block.hash}</p>
                <p><strong>Previous Hash:</strong> ${block.previous_hash}</p>
                <p><strong>Transactions:</strong></p>
                <ul>
                    ${
                        block.transactions.length > 0
                            ? block.transactions.map(tx => `
                                <li>
                                    <strong>Sender:</strong> ${tx.sender}, 
                                    <strong>Recipient:</strong> ${tx.recipient}, 
                                    <strong>Amount:</strong> ${tx.amount}
                                    ${tx.signature ? `<br><strong>Signature:</strong> ${tx.signature.slice(0, 20)}...` : ""}
                                </li>
                            `).join("")
                            : "<li>No transactions in this block.</li>"
                    }
                </ul>
            `;
            chainDiv.appendChild(blockDiv);
        });
    } catch (error) {
        console.error("Error fetching chain:", error);
        alert("Failed to load blockchain.");
    }
}



// Инициализация загрузки данных при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
    loadChain();
});
