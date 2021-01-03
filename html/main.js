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

const toggleMedia = e => {
  const img = e.target;
  const preview = img.parentNode;
  preview.classList.toggle("full");
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

  for (let preview of document.querySelectorAll(".preview")) {
      const media = preview.querySelector("img") || preview.querySelector("video");
      if (media) {
        media.addEventListener("click", toggleMedia);
      }
  }
})