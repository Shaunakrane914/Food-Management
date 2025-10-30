// Fetch and display batch settings
fetch('http://localhost:8000/settings/batches')
  .then(res => res.json())
  .then(batches => {
    const tbody = document.querySelector('#batch-table tbody');
    tbody.innerHTML = '';
    batches.forEach(batch => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${batch.batch_name}</td>
        <td>${batch.total_count}</td>
        <td>${(batch.weekend_stay_percent * 100).toFixed(1)}%</td>
        <td></td>
      `;
      tbody.appendChild(tr);
    });
  });

// Fetch and display exam rules
function loadExamRules() {
  fetch('http://localhost:8000/settings/exam_rules')
    .then(res => res.json())
    .then(rules => {
      const tbody = document.querySelector('#exam-table tbody');
      tbody.innerHTML = '';
      rules.forEach(rule => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${rule.exam_time}</td>
          <td>${rule.meal}</td>
          <td>${(rule.reduction_percent * 100).toFixed(0)}%</td>
        `;
        tbody.appendChild(tr);
      });
    });
}
loadExamRules();

// Add new exam rule
const examForm = document.getElementById('exam-form');
examForm.addEventListener('submit', async function(e) {
  e.preventDefault();
  const exam_time = document.getElementById('exam_time').value;
  const meal = document.getElementById('meal').value;
  const reduction = parseFloat(document.getElementById('reduction').value) / 100;
  await fetch('http://localhost:8000/settings/exam_rules', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ exam_time, meal, reduction_percent: reduction })
  });
  loadExamRules();
  examForm.reset();
}); 