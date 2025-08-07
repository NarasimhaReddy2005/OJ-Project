document.addEventListener("DOMContentLoaded", () => {
  const aiBtn = document.getElementById("ai-review-btn");
  if (!aiBtn) return;

  aiBtn.addEventListener("click", () => {
    console.log("AI Review button clicked.");
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
      .then((res) => res.json())
      .then((data) => {
        if (!data || data.error) {
          alert("AI failed to load");
          return;
        }

        // Load AI modal or popup here (next step)
        console.log("AI Data:", data);
        showAiPopup(data); // You’ll define this in the next step
      });
  });
});

function showAiPopup(data) {
  fetch("/static/ai/html/ai_popup.html")
    .then((res) => res.text())
    .then((template) => {
      const filled = template
        .replace("{{problem_statement}}", data.problem_statement)
        .replace("{{language}}", data.language)
        .replace("{{verdict}}", data.verdict)
        .replace("{{code}}", escapeHtml(data.code));

      const modal = document.getElementById("ai-review-modal");
      modal.innerHTML = filled;
      modal.style.display = "block";

      // Attach close button handler
      const closeBtn = modal.querySelector("#ai-close-btn");
      if (closeBtn) closeBtn.onclick = closeAiPopup;

      // Attach Continue button handler
      const continueBtn = modal.querySelector("#continue-btn");
      if (continueBtn) {
        continueBtn.onclick = () => {
          fetchAiReview(data); // Next step
        };
      }
    })
    .catch((err) => {
      console.error("Failed to load popup template:", err);
    });
}

function closeAiPopup() {
  document.getElementById("ai-review-modal").style.display = "none";
}
function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function fetchAiReview(data) {
  fetch("/ai/review/generate/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(data),
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.error) {
        alert("AI failed to generate response: " + res.error);
        return;
      }

      const responseBox = document.getElementById("ai-review-response");
      const contentBox = document.getElementById("ai-review-content");

      if (!responseBox || !contentBox) {
        console.error("Popup elements not found.");
        return;
      }

      responseBox.style.display = "block";
      contentBox.textContent = res.ai_response;
      contentBox.style.whiteSpace = "pre-wrap"; // Keep line breaks
      contentBox.style.overflowY = "auto";
      contentBox.style.maxHeight = "300px"; // Add scroll if long
    })
    .catch((err) => {
      console.error("Fetch failed:", err);
      alert("Unexpected error occurred while fetching AI review.");
    });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
