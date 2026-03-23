// Copied from Pax ML/frontend/settings.js
// ... existing code ... 

// Fetch and display batch settings
async function loadBatches() {
  const res = await fetch('/pax_settings/batches');
  const batches = await res.json();
  // You can display these in a table or console for now
  console.log('Batches:', batches);
}
loadBatches();

// Add or update batch setting
const settingsForm = document.getElementById('settings-form');
settingsForm.addEventListener('submit', async function(e) {
  e.preventDefault();
  const batch_name = document.getElementById('batch').value;
  const total_count = parseInt(document.getElementById('count').value);
  const weekend_stay_percent = parseFloat(document.getElementById('weekend').value) / 100;
  await fetch('/pax_settings/batches', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batch_name, total_count, weekend_stay_percent })
  });
  settingsForm.reset();
  loadBatches();
});

// Fetch and display exam rules
async function loadExamRules() {
  const res = await fetch('/pax_settings/exam_rules');
  const rules = await res.json();
  console.log('Exam Rules:', rules);
}
loadExamRules();

// Example: Add more UI for exam rules and exam dates as needed
// You can expand this to display in tables and add forms for exam rules/dates 