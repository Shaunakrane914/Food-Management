document.getElementById('predict-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const total_present = document.getElementById('total_present').value;
    const date = document.getElementById('date').value;

    const payload = {
        total_present: parseInt(total_present),
        date: date
    };

    console.log("Sending payload:", payload);

    const res = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    let data;
    try {
        data = await res.json();
    } catch (err) {
        console.error("Failed to parse JSON:", err);
        data = { detail: "Invalid JSON response from backend." };
    }

    console.log("Response status:", res.status);
    console.log("Response data:", data);

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
        // Show the actual error message from backend
        resultDiv.innerHTML = `<b>Error:</b> ${typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)}`;
    }
}); 

// Meal-wise prediction logic

document.getElementById('mealwise-btn').addEventListener('click', async function() {
    // For demo: use a static menu for the selected date (in real use, extract from your menu UI)
    const date = document.getElementById('date').value;
    if (!date) {
        alert('Please select a date first.');
        return;
    }
    // For demo, use a static mapping for a Saturday (update as needed)
    const menu = [
        { date, day: 'Saturday', meal_type: 'Breakfast', unique_dish: 'UniqueDish_Missal Pav' },
        { date, day: 'Saturday', meal_type: 'Lunch', unique_dish: 'UniqueDish_Bhindi Onion Dry' },
        { date, day: 'Saturday', meal_type: 'Snacks', unique_dish: 'UniqueDish_Aloo Papdi Chaat' },
        { date, day: 'Saturday', meal_type: 'Dinner', unique_dish: 'UniqueDish_Sindhi Kadi' }
    ];
    const res = await fetch('http://localhost:8000/predict_meal_pax', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ menu })
    });
    let data;
    try {
        data = await res.json();
    } catch (err) {
        data = { predictions: [] };
    }
    const mealwiseDiv = document.getElementById('mealwise-result');
    if (res.ok && data.predictions && data.predictions.length) {
        mealwiseDiv.style.display = 'block';
        mealwiseDiv.innerHTML = `<h2>Meal-wise Pax Predictions</h2><ul>` +
            data.predictions.map(pred =>
                `<li><b>${pred.meal_type}:</b> ${pred.predicted_pax !== null ? pred.predicted_pax : 'No data'} ` +
                `<span style='color:gray;font-size:smaller;'>(method: ${pred.method})</span></li>`
            ).join('') + '</ul>';
    } else {
        mealwiseDiv.style.display = 'block';
        mealwiseDiv.innerHTML = '<b>No predictions available.</b>';
    }
}); 