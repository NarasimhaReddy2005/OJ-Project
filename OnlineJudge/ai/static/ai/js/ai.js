document.addEventListener("DOMContentLoaded", () => {
  const aiBtn = document.getElementById("ai-review-btn");
  if (!aiBtn) return;

  aiBtn.addEventListener("click", () => {
    fetch(`/submission/latest/${window.problemId}/`)
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          alert("Error fetching submission");
          return;
        }

        const subId = data.id;
        return fetch(`/ai/review/${subId}/`);
      })
      .then((res) => res.text())
      .then((html) => {
        // Inject the HTML into the DOM
        const wrapper = document.createElement("div");
        wrapper.innerHTML = html;
        document.body.appendChild(wrapper);

        // Add close logic
        const closeBtn = document.getElementById("ai-popup-close");
        closeBtn.addEventListener("click", () => {
          wrapper.remove();
        });
        const continueBtn = document.getElementById("ai-continue-btn");
        if (continueBtn) {
          const subId = continueBtn.getAttribute("data-submission-id");
          continueBtn.addEventListener("click", () =>
            handleContinueClick(subId)
          );
        }
      })
      .catch((err) => {
        console.error("Error:", err);
        alert("Something went wrong");
      });
  });
});
function handleContinueClick(submissionId) {
  const responseBox = document.getElementById("ai-review-response");
  const content = document.getElementById("ai-review-content");
  const continueBtn = document.getElementById("ai-continue-btn");

  if (!responseBox || !content || !continueBtn) return;

  // Disable the button
  continueBtn.disabled = true;
  continueBtn.textContent = "Generating...";

  responseBox.style.display = "block";
  content.textContent = "🔍 Thinking...";

  fetch(`/ai/review/generate/${submissionId}/`)
    .then((res) => res.text())
    .then((html) => {
      content.innerHTML = html;
    })
    .then(() => {
      continueBtn.textContent = "Generated";
    })
    .catch((err) => {
      console.error("AI fetch failed:", err);
      content.textContent = "❌ Failed to generate review.";
    });
}

// function showAiPopup(data) {
//   fetch("/static/ai/html/ai_popup.html")
//     .then((res) => res.text())
//     .then((template) => {
//       const filled = template
//         .replace("{{problem_statement}}", data.problem_statement)
//         .replace("{{language}}", data.language)
//         .replace("{{verdict}}", data.verdict)
//         .replace("{{code}}", escapeHtml(data.code));

//       const modal = document.getElementById("ai-review-modal");
//       modal.innerHTML = filled;
//       modal.style.display = "block";

//       // Attach close button handler
//       const closeBtn = modal.querySelector("#ai-close-btn");
//       if (closeBtn) closeBtn.onclick = closeAiPopup;

//       // Attach Continue button handler
//       const continueBtn = modal.querySelector("#continue-btn");
//       if (continueBtn) {
//         continueBtn.onclick = () => {
//           fetchAiReview(data); // Next step
//         };
//       }
//     })
//     .catch((err) => {
//       console.error("Failed to load popup template:", err);
//     });
// }

// function closeAiPopup() {
//   document.getElementById("ai-review-modal").style.display = "none";
// }
// function escapeHtml(str) {
//   return str
//     .replace(/&/g, "&amp;")
//     .replace(/</g, "&lt;")
//     .replace(/>/g, "&gt;")
//     .replace(/"/g, "&quot;");
// }

// function fetchAiReview(data) {
//   fetch("/ai/review/generate/", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//       "X-CSRFToken": getCookie("csrftoken"),
//     },
//     body: JSON.stringify(data),
//   })
//     .then((res) => res.json())
//     .then((res) => {
//       if (res.error) {
//         alert("AI failed to generate response: " + res.error);
//         return;
//       }

//       const responseBox = document.getElementById("ai-review-response");
//       const contentBox = document.getElementById("ai-review-content");

//       if (!responseBox || !contentBox) {
//         console.error("Popup elements not found.");
//         return;
//       }

//       responseBox.style.display = "block";
//       contentBox.textContent = res.ai_response;
//       contentBox.style.whiteSpace = "pre-wrap"; // Keep line breaks
//       contentBox.style.overflowY = "auto";
//       contentBox.style.maxHeight = "300px"; // Add scroll if long
//     })
//     .catch((err) => {
//       console.error("Fetch failed:", err);
//       alert("Unexpected error occurred while fetching AI review.");
//     });
// }

// function getCookie(name) {
//   let cookieValue = null;
//   if (document.cookie && document.cookie !== "") {
//     const cookies = document.cookie.split(";");
//     for (let i = 0; i < cookies.length; i++) {
//       const cookie = cookies[i].trim();
//       // Does this cookie string begin with the name we want?
//       if (cookie.substring(0, name.length + 1) === name + "=") {
//         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//         break;
//       }
//     }
//   }
//   return cookieValue;
// }
