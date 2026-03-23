// Copied from Pax ML/frontend/script.js
// ... existing code ... 

document.getElementById('predict-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const total_present = document.getElementById('present').value;
    const date = document.getElementById('date').value;
    const is_exam = document.getElementById('is_exam').checked;
    const exam_time = document.getElementById('exam_time').value;

    const payload = {
        total_present: parseInt(total_present),
        date: date,
        is_exam: is_exam,
        exam_time: exam_time || null
    };

    const res = await fetch('/pax_predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    let data;
    try {
        data = await res.json();
    } catch (err) {
        data = { detail: "Invalid JSON response from backend." };
    }

    const resultDiv = document.getElementById('result');
    if (res.ok) {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `
            <h2>Predicted Pax</h2>
            <ul>
                <li><b>Breakfast:</b> ${data.breakfast}</li>
                <li><b>Brunch:</b> ${data.brunch}</li>
                <li><b>Lunch:</b> ${data.lunch}</li>
                <li><b>Snacks:</b> ${data.snacks}</li>
                <li><b>Dinner:</b> ${data.dinner}</li>
            </ul>
            ${data.notes && data.notes.length ? `<p><b>Notes:</b> ${data.notes.join('<br>')}</p>` : ''}
        `;
    } else {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `<b>Error:</b> ${typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)}`;
    }
}); 