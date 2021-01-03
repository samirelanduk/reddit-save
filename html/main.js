const toggleView = () => {
  const postsSection = document.querySelector(".posts-section");
  const commentsSection = document.querySelector(".comments-section");
  if (commentsSection.style.display === "none") {
      commentsSection.style.display = "block";
      postsSection.style.display = "none";
  } else {
      postsSection.style.display = "block";
      commentsSection.style.display = "none";
  }
}

window.addEventListener("load", function() {
const postsSection = document.querySelector(".posts-section");
const commentsSection = document.querySelector(".comments-section");
if (commentsSection) {
  commentsSection.style.display = "none";
  const toggleButton = document.createElement("button");
  toggleButton.innerText = "toggle";
  toggleButton.addEventListener("click", toggleView);
  document.body.insertBefore(toggleButton, postsSection);
}
})