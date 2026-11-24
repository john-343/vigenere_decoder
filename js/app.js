const button = document.getElementById("decrypt-button");
const ciphertextInput = document.getElementById("ciphertext");
const results = document.getElementById("results");

button.addEventListener("click", () => {
    const ciphertext = ciphertextInput.value.trim();

    if (!ciphertext) {
        results.textContent = "Please enter some ciphertext.";
        return;
    }

    results.textContent = "Ciphertext received. Python integration coming next!";
});
