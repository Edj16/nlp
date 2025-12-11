// TAB SWITCHING
document.getElementById("tabChat").onclick = () => {
    document.getElementById("chatMode").classList.add("active-mode");
    document.getElementById("formMode").classList.add("hidden");
    document.getElementById("tabChat").classList.add("active");
    document.getElementById("tabForm").classList.remove("active");
};

document.getElementById("tabForm").onclick = () => {
    document.getElementById("chatMode").classList.remove("active-mode");
    document.getElementById("chatMode").classList.add("hidden");
    document.getElementById("formMode").classList.remove("hidden");
    document.getElementById("tabForm").classList.add("active");
    document.getElementById("tabChat").classList.remove("active");
};

// CHAT PARSE
document.getElementById("parseBtn").addEventListener("click", () => {
    let text = document.getElementById("userInput").value;
    if (!text.trim()) return alert("Please type something!");

    document.getElementById("contractPreview").value =
        "Generated Contract Based on Input:\n\n" + text;
});

// CLEAR CHAT
document.getElementById("clearBtn").onclick = () => {
    document.getElementById("userInput").value = "";
};

// FORM GENERATION
document.getElementById("generateDraft").onclick = () => {
    let a = document.getElementById("partyA").value;
    let b = document.getElementById("partyB").value;
    let type = document.getElementById("contractType").value;
    let start = document.getElementById("startDate").value;
    let months = document.getElementById("duration").value;
    let amount = document.getElementById("amount").value;
    let currency = document.getElementById("currency").value;
    let freq = document.getElementById("paymentFreq").value;
    let special = document.getElementById("special").value;

    let contract =
        `CONTRACT DRAFT

Contract Type: ${type}

This agreement is made between:
Party A: ${a}
Party B: ${b}

Start Date: ${start}
Duration: ${months} months
Payment: ${amount} ${currency}
Frequency: ${freq}

Special Clauses:
${special || "None"}

Generated automatically.`;

    document.getElementById("contractPreview").value = contract;
};

// RESET FORM
document.getElementById("resetForm").onclick = () => {
    document.querySelectorAll("#formMode input").forEach(i => i.value = "");
};

// COPY CONTRACT
document.getElementById("copyBtn").onclick = () => {
    navigator.clipboard.writeText(document.getElementById("contractPreview").value);
    alert("Copied!");
};

// CLEAR PREVIEW
document.getElementById("clearPreview").onclick = () => {
    document.getElementById("contractPreview").value = "No contract generated yet.";
};

// EXPORT PDF — placeholder
document.getElementById("exportBtn").onclick = () => {
    alert("PDF export requires jsPDF or backend. I can add it if you want.");
};