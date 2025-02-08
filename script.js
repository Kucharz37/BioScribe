const form = document.getElementById("quiz");
const result = document.getElementById("result");
const loading = document.querySelector('.loading');
const settingsToggle = document.querySelector('.settings-toggle');
const advancedSettings = document.querySelector('.advanced-settings');
const customLengthToggle = document.getElementById('custom-length-toggle');
const customLengthInput = document.getElementById('custom-length');

// Obsługa przycisku ustawień
settingsToggle.addEventListener('click', () => {
    advancedSettings.hidden = !advancedSettings.hidden;
});

// Obsługa przełącznika własnej długości
customLengthToggle.addEventListener('change', (e) => {
    customLengthInput.disabled = !e.target.checked;
});

async function generateBio(data) {
    try {
        const response = await fetch('http://localhost:5000/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify(data)
        });

        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        alert('Skopiowano do schowka!');
    } catch (err) {
        console.error('Błąd podczas kopiowania:', err);
    }
}

function showLoading() {
    loading.classList.add('active');
    form.querySelector('button[type="submit"]').disabled = true;
    result.textContent = '';
}

function hideLoading() {
    loading.classList.remove('active');
    form.querySelector('button[type="submit"]').disabled = false;
}

function displayResult(data) {
    if (data.error) {
        result.textContent = `Błąd: ${data.error}`;
    } else {
        result.innerHTML = `
            <div>${data.description}</div>
            <button class="copy-btn" onclick="copyToClipboard('${data.description.replace(/'/g, "\\'")}')">
                Kopiuj do schowka 📋
            </button>
        `;
        result.classList.add('active');
    }
}

form.addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const formData = {
        hobby: document.getElementById("hobby").value,
        personality: document.getElementById("personality").value,
        goal: document.getElementById("goal").value,
        language: document.getElementById("language").value,
        max_length: customLengthToggle.checked ? customLengthInput.value : 1000
    };

    showLoading();
    
    try {
        const data = await generateBio(formData);
        displayResult(data);
    } catch (error) {
        result.textContent = "Wystąpił błąd podczas generowania opisu. Spróbuj ponownie.";
    } finally {
        hideLoading();
    }
});