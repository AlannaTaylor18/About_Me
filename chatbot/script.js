// --- Recommendation Functions ---

function addRecommendation() {
  // Get the message of the new recommendation
  let recommendation = document.getElementById("new_recommendation");
  showPopup(true);
  if (recommendation.value != null && recommendation.value.trim() != "") {
    console.log("New recommendation added");
    showPopup(true);

    // Create a new 'recommendation' element and set its value to the user's message
    var element = document.createElement("div");
    element.setAttribute("class","recommendation");
    element.innerHTML = "<span>&#8220;</span>" + recommendation.value + "<span>&#8221;</span>";
    // Add this element to the end of the list of recommendations
    document.getElementById("all_recommendations").appendChild(element); 
    
    // Reset the value of the textarea
    recommendation.value = "";
  }
}

function showPopup(bool) {
  if (bool) {
    document.getElementById('popup').style.visibility = 'visible'
  } else {
    document.getElementById('popup').style.visibility = 'hidden'
  }
}

// --- Chatbot Functions ---

// Listen for user pressing Enter in the input box with id="user-input"
document.getElementById("user-input").addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    const userInput = event.target.value.trim();
    if (userInput === "") return;

    addMessageToChat("You", userInput);

    // Generate chatbot response based on user input
    const response = generateResponse(userInput.toLowerCase());
    addMessageToChat("Bot", response);

    event.target.value = "";  // Clear input box
  }
});

// Function to add a message (either user or bot) to the chatbox div with id="chatbox"
function addMessageToChat(sender, message) {
  const chatbox = document.getElementById("chatbox");
  const msgDiv = document.createElement("div");
  msgDiv.className = sender === "Bot" ? "bot-message" : "user-message";
  msgDiv.textContent = `${sender}: ${message}`;
  chatbox.appendChild(msgDiv);
  chatbox.scrollTop = chatbox.scrollHeight;  // Scroll chat to bottom
}

// Simple keyword-based chatbot response generator
function generateResponse(input) {
  if (input.includes("skill")) {
    return "I have skills in Python, Flask, IBM Watson, and more!";
  } else if (input.includes("project")) {
    return "I developed projects including a chatbot and a portfolio website.";
  } else if (input.includes("resume")) {
    return "You can view my resume by clicking the 'Resume' link in the navigation.";
  } else if (input.includes("hello") || input.includes("hi")) {
    return "Hello! How can I assist you today?";
  } else {
    return "Sorry, I didn't understand that. Could you please ask something else?";
  }
}