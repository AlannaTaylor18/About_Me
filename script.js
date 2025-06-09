function addRecommendation() {
  let recommendation = document.getElementById("new_recommendation");

  if (recommendation.value != null && recommendation.value.trim() != "") {
    console.log("New recommendation added");
    showPopup(true);

    let element = document.createElement("div");
    element.classList.add("recommendation");

    // Add opening quote span
    element.appendChild(document.createElement("span")).textContent = "“";

    // Add the recommendation text safely as a text node
    let textNode = document.createTextNode(recommendation.value);
    element.appendChild(textNode);

    // Add closing quote span
    element.appendChild(document.createElement("span")).textContent = "”";

    document.getElementById("all_recommendations").appendChild(element);
    recommendation.value = "";
  }
}

function showPopup(bool) {
  const popup = document.getElementById('popup');
  if (bool) {
    popup.style.visibility = 'visible';
    setTimeout(() => popup.style.visibility = 'hidden', 2000); // Hide after 2 seconds
  } else {
    popup.style.visibility = 'hidden';
  }
}
