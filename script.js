document.getElementById('predictionForm').addEventListener('submit', function(event) {
    event.preventDefault();
  
    // Get form values
    const make = document.getElementById('make').value;
    const model = document.getElementById('model').value;
    const year = parseInt(document.getElementById('year').value);
  
    // Perform prediction logic (you can add your ML/AI model here)
  
    // Dummy result for demonstration
    const resaleValue = Math.floor(Math.random() * 500000) + 500000;
  
    // Display prediction result
    document.getElementById('predictionResult').innerHTML = `
      <h2>Predicted Resale Value</h2>
      <p>Make: ${make}</p>
      <p>Model: ${model}</p>
      <p>Year: ${year}</p>
      <p>Resale Value: Rs. ${resaleValue}</p>
    `;
  });
  