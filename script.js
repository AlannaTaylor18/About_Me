// === RECOMMENDATION SECTION ===
function addRecommendation() {
  const recommendation = document.getElementById("new_recommendation");

  if (recommendation.value && recommendation.value.trim() !== "") {
    console.log("New recommendation added");
    showPopup(true);

    const element = document.createElement("div");
    element.classList.add("recommendation");

    const openQuote = document.createElement("span");
    openQuote.textContent = "“";
    element.appendChild(openQuote);

    const textNode = document.createTextNode(recommendation.value);
    element.appendChild(textNode);

    const closeQuote = document.createElement("span");
    closeQuote.textContent = "”";
    element.appendChild(closeQuote);

    document.getElementById("all_recommendations").appendChild(element);
    recommendation.value = "";
  }
}

function showPopup(show) {
  const popup = document.getElementById("popup");
  popup.style.visibility = show ? "visible" : "hidden";
  if (show) {
    setTimeout(() => (popup.style.visibility = "hidden"), 2000);
  }
}

// === CHATBOT SECTION ===
async function sendMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();

  if (message !== "") {
    const chatMessages = document.getElementById("chat-messages");

    // Add user message
    const userMsg = document.createElement("div");
    userMsg.className = "user-message";
    userMsg.textContent = message;
    chatMessages.appendChild(userMsg);

    input.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      // ✅ Replace with your real deployed backend URL
      const response = await fetch("https://resume-chatbot-alanna.herokuapp.com/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "HRKU-AAAJB02PkglwW9bmx4OzJtHBstGFt_TVup8s9DpVnCsg_____waHx_synQFI"
        },
        body: JSON.stringify({ message: message }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();

      // Add bot response
      const botMsg = document.createElement("div");
      botMsg.className = "bot-message";
      botMsg.textContent = data.reply || "Sorry, I didn't get that.";
      chatMessages.appendChild(botMsg);
      chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
      console.error("Error calling backend:", error);
      const botMsg = document.createElement("div");
      botMsg.className = "bot-message";
      botMsg.textContent = "Error contacting the server. Please try again later.";
      chatMessages.appendChild(botMsg);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }
}

// === INIT EVENT LISTENERS ===
document.addEventListener("DOMContentLoaded", () => {
  // Recommendation input Enter key
  const newRecommendation = document.getElementById("new_recommendation");
  if (newRecommendation) {
    newRecommendation.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        addRecommendation();
      }
    });
  }

  // Chatbot: Handle Send button and Enter key
  const sendButton = document.getElementById("chat-send");
  const inputField = document.getElementById("chat-input");

  if (sendButton && inputField) {
    sendButton.addEventListener("click", sendMessage);
    inputField.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
      }
    });
  }
});