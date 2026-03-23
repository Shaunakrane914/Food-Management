// Pax prediction for menu
const showPaxBtn = document.getElementById('showPaxBtn');
console.log('[DEBUG] showPaxBtn:', showPaxBtn);
if (showPaxBtn) {
    showPaxBtn.addEventListener('click', async function() {
        // Show loading spinner/text on button
        const originalBtnHTML = showPaxBtn.innerHTML;
        showPaxBtn.disabled = true;
        showPaxBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Loading...';
        try {
            // Get menu data from hidden input or global
            let menuData;
            if (window.menuData) {
                menuData = window.menuData;
                console.log('[DEBUG] window.menuData found:', menuData);
            } else if (document.getElementById('menuDataJson')) {
                menuData = JSON.parse(document.getElementById('menuDataJson').value);
                console.log('[DEBUG] menuDataJson found:', menuData);
            } else {
                console.error('[DEBUG] No menu data found!');
                return;
            }
            // Prepare payload
            const menuItems = [];
            Object.entries(menuData).forEach(([_, dayData]) => {
                const date = dayData.Date;
                const day = dayData.Day;
                const items = dayData.Items;
                if (day === 'Sunday') {
                    if (items['Brunch']) {
                        items['Brunch'].forEach(dish => {
                            menuItems.push({date, day, meal_type: 'Brunch', unique_dish: dish});
                        });
                    }
                    ['Snacks', 'Dinner'].forEach(meal => {
                        if (items[meal]) {
                            items[meal].forEach(dish => {
                                menuItems.push({date, day, meal_type: meal, unique_dish: dish});
                            });
                        }
                    });
                } else {
                    ['Breakfast', 'Lunch', 'Snacks', 'Dinner'].forEach(meal => {
                        if (items[meal]) {
                            items[meal].forEach(dish => {
                                menuItems.push({date, day, meal_type: meal, unique_dish: dish});
                            });
                        }
                    });
                }
            });
            console.log('[DEBUG] menuItems payload:', menuItems);
            // Send to backend
            const res = await fetch('/predict_meal_pax', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({menu: menuItems})
            });
            console.log('[DEBUG] Fetch response status:', res.status);
            const data = await res.json();
            console.log('[DEBUG] Backend response:', data);
            // Update UI with data.predictions
            if (data && data.predictions) {
                // Map predictions by normalized key
                const normalize = str => (str || '').toLowerCase().trim();
                // Aggregate dish-level predictions to meal-level
                const mealPaxMap = {};
                data.predictions.forEach(pred => {
                    const mealKey = [
                        normalize(pred.date),
                        normalize(pred.day),
                        normalize(pred.meal_type)
                    ].join('|');
                    // Use the max pax for the meal (or you can use first, or average, as you prefer)
                    if (!mealPaxMap[mealKey] || pred.predicted_pax > mealPaxMap[mealKey]) {
                        mealPaxMap[mealKey] = pred.predicted_pax;
                    }
                });
                // Update only meal heading pax-counts (data-dish="")
                document.querySelectorAll('.pax-count[data-dish=""]').forEach(span => {
                    const date = normalize(span.getAttribute('data-date'));
                    const day = normalize(span.getAttribute('data-day'));
                    const meal = normalize(span.getAttribute('data-meal'));
                    const mealKey = [date, day, meal].join('|');
                    if (mealPaxMap[mealKey] !== undefined) {
                        span.textContent = `(Pax: ${mealPaxMap[mealKey]})`;
                        span.style.color = '';
                        span.title = '';
                    } else {
                        span.textContent = '(No Pax Data)';
                        span.style.color = 'red';
                        span.title = 'No prediction found for this meal.';
                    }
                });
            }
        } catch (err) {
            // ... existing code ...
        } finally {
            // Restore button
            showPaxBtn.disabled = false;
            showPaxBtn.innerHTML = originalBtnHTML;
        }
    });
} 