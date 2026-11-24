let pyodide = null;
let pythonOutput = "";

function capturePythonOutput(text) {
    pythonOutput += text;
}

async function loadPython() {
    pyodide = await loadPyodide({
        stdout: capturePythonOutput
    });
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

    if (!pyodide) {
        results.textContent = "Python is still loading. Please wait.";
        return;
    }

    pythonOutput = "";

    try {
        const pythonFunction = pyodide.globals.get("analyze_ciphertext");
        const pythonResult = pythonFunction(ciphertext);

        const result = pythonResult.toJs({
            dict_converter: Object.fromEntries
        });

        pythonResult.destroy();

        console.log("Python output:", pythonOutput);
        console.log("Structured results:", result);
        
        results.textContent = pythonOutput;

const graphContainer = document.getElementById("graph-container");
graphContainer.innerHTML = "";

if (result.plot) {
    const graph = document.createElement("img");
    graph.src = `data:image/png;base64,${result.plot}`;
    graph.alt = "Frequency analysis graph";
    graph.style.width = "100%";
    graph.style.maxWidth = "900px";

    graphContainer.appendChild(graph);
} else {
    graphContainer.textContent = "No graph available.";
}
        
        const decryptedText = document.getElementById("decrypted-text");
        decryptedText.innerHTML = "";

        if (result.results && result.results.length > 0) {
            result.results.forEach(item => {
                const entry = document.createElement("div");

                const heading = document.createElement("h3");
                heading.textContent = `#${item.rank} — Key: ${item.key} (Score: ${item.score})`;

                const text = document.createElement("pre");
                text.textContent = item.decrypted_text;

                entry.appendChild(heading);
                entry.appendChild(text);
                decryptedText.appendChild(entry);
            });
        } else {
            decryptedText.textContent = "No decrypted results available.";
        }

    } catch (error) {
        results.textContent = "Error: " + error.message;
        console.error(error);
    }
});
