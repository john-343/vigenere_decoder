let pyodide = null;

async function loadPython() {
    pyodide = await loadPyodide();
    console.log("Python is ready!");
}

loadPython().then(async () => {
    const response = await fetch("english_quadgrams.txt");
    const quadgramText = await response.text();

    pyodide.FS.writeFile("/english_quadgrams.txt", quadgramText);
    console.log("Quadgram dataset loaded!");
    
    await pyodide.loadPackage("matplotlib");
    console.log("Matplotlib loaded!");
    
    const pythonResponse = await fetch("python/decrypt.py");
    const pythonCode = await pythonResponse.text();

    pyodide.runPython(pythonCode);

    console.log("Decryption algorithm loaded!");
});

const button = document.getElementById("decrypt-button");
const ciphertextInput = document.getElementById("ciphertext");
const results = document.getElementById("results");

button.addEventListener("click", async () => {
    const ciphertext = ciphertextInput.value.trim();

    if (!ciphertext) {
        results.textContent = "Please enter some ciphertext.";
        return;
    }

    results.textContent = "Ciphertext received. Python integration coming next!";
});
