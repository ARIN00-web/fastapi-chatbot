document.getElementById('chatForm').addEventListener('submit', async function (e) {
    e.preventDefault();
  
    const input = document.getElementById('userInput');
    const userText = input.value;
    input.value = '';
  
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.innerHTML += `<div class="message user">${userText}</div>`;
  
    const response = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: userText })
    });
  
    const data = await response.json();
    chatWindow.innerHTML += `<div class="message bot">${data.answer}</div>`;
    chatWindow.scrollTop = chatWindow.scrollHeight;
  });
  