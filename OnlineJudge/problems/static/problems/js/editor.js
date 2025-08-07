const languageModeMap = {
  cpp: "text/x-c++src",
  java: "text/x-java",
  python: "python",
};

// Initialize CodeMirror
var myCodeMirror = CodeMirror.fromTextArea(
  document.getElementById("codeArea"),
  {
    lineNumbers: true,
    theme: "material",
    mode: languageModeMap["cpp"],
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
  }
);
myCodeMirror.setSize("100%", "50vh");

// Get CSRF token
function getCSRFToken() {
  const cookie = document.cookie
    .split(";")
    .find((c) => c.trim().startsWith("csrftoken="));
  return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}

// Handle Run Button
document.getElementById("runBtn").addEventListener("click", () => {
  const code = myCodeMirror.getValue();
  const input = document.getElementById("inputArea").value;
  const language = document.getElementById("languageSelect").value;

  fetch("/submission/run/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({ code, input, language }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("outputArea").value =
        data.output || data.error || "No output";
    });
});

// Handle Submit Button
document.getElementById("submitBtn").addEventListener("click", function () {
  const submitBtn = this;
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";
  const code = myCodeMirror.getValue();
  const language = document.getElementById("languageSelect").value;
  const problemId = window.problemId || 1;

  console.log("Submitting Problem ID:", problemId);

  fetch(`/submission/submit/${problemId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCSRFToken(),
    },
    body: new URLSearchParams({
      code: code,
      language: language,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById(
        "outputArea"
      ).value = `Verdict: ${data.verdict}\n\nOutput:\n${data.output}`;
    })
    .catch((error) => {
      document.getElementById("outputArea").value = "Error during submission";
      console.error("Submission Error:", error);
    })
    .finally(() => {
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit";
    });
});

document.addEventListener("DOMContentLoaded", () => {
  const aiBtn = document.getElementById("ai-review-btn");

  if (!aiBtn) return;

  aiBtn.addEventListener("click", () => {
    if (!window.problemId) {
      alert("Problem ID not found.");
      return;
    }

    fetch(`/submission/latest/${window.problemId}/`)
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
          return;
        }

        const latestSubmissionId = data.id;
        console.log("✅ Latest submission ID:", latestSubmissionId);

        // 🔜 Next step: Call AI review API using this ID
      })
      .catch((err) => {
        console.error("Failed to fetch latest submission:", err);
        alert("Something went wrong.");
      });
  });
});
