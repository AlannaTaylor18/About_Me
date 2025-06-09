// === RECOMMENDATION SECTION ===
function addRecommendation() {
  let recommendation = document.getElementById("new_recommendation");

  if (recommendation.value != null && recommendation.value.trim() != "") {
    console.log("New recommendation added");
    showPopup(true);

    let element = document.createElement("div");
    element.classList.add("recommendation");

    // Add opening quote
    const openQuote = document.createElement("span");
    openQuote.textContent = "“";
    element.appendChild(openQuote);

    // Add text safely
    let textNode = document.createTextNode(recommendation.value);
    element.appendChild(textNode);

    // Add closing quote
    const closeQuote = document.createElement("span");
    closeQuote.textContent = "”";
    element.appendChild(closeQuote);

    document.getElementById("all_recommendations").appendChild(element);
    recommendation.value = "";
  }
}

function showPopup(bool) {
  const popup = document.getElementById("popup");
  if (bool) {
    popup.style.visibility = "visible";
    setTimeout(() => (popup.style.visibility = "hidden"), 2000);
  } else {
    popup.style.visibility = "hidden";
  }
}

// Handle Enter key for recommendations
document.addEventListener("DOMContentLoaded", () => {
  document
    .getElementById("new_recommendation")
    .addEventListener("keydown", function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        addRecommendation();
      }
    });
});

// === CHATBOT SECTION ===
function sendMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();

  if (message !== "") {
    const chatMessages = document.getElementById("chat-messages");

    // Add user message
    const userMsg = document.createElement("div");
    userMsg.className = "user-message";
    userMsg.textContent = message;
    chatMessages.appendChild(userMsg);

    // Simulated bot response
    const botMsg = document.createElement("div");
    botMsg.className = "bot-message";
    botMsg.textContent = "Thanks for your message! (You said: " + message + ")";
    chatMessages.appendChild(botMsg);

    input.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
  }
}

// Handle Send button
document.addEventListener("DOMContentLoaded", () => {
  const sendButton = document.getElementById("chat-send");
  const inputField = document.getElementById("chat-input");

  if (sendButton && inputField) {
    sendButton.addEventListener("click", sendMessage);
    inputField.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
      }
    });
  }
});