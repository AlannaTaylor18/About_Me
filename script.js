function addRecommendation() {
  let recommendation = document.getElementById("new_recommendation");

  if (recommendation.value != null && recommendation.value.trim() != "") {
    console.log("New recommendation added");
    showPopup(true);

    let element = document.createElement("div");
    element.setAttribute("class", "recommendation");
    element.innerHTML = "<span>&#8220;</span>" + recommendation.value + "<span>&#8221;</span>";

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
