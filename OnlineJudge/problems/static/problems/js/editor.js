const languageModeMap = {
  cpp: "text/x-c++src",
  java: "text/x-java",
  python: "python",
};
// boilerplates.js

// Boilerplate starter code for each language
const boilerplates = {
  cpp: `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // Your code here

    return 0;
}`,

  python: `def main():
    # Your code here
    pass

if __name__ == "__main__":
    main()`,

  java: `import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // Your code here

        sc.close();
    }
}`,
};

const langSelect = document.getElementById("languageSelect");

// Determine initial language (latest or default cpp)
const initialLang =
  window.latestLang && window.latestLang.trim() !== ""
    ? window.latestLang
    : "cpp";

langSelect.value = initialLang;

// Initialize CodeMirror
var myCodeMirror = CodeMirror.fromTextArea(
  document.getElementById("codeArea"),
  {
    lineNumbers: true,
    theme: "material",
    mode: languageModeMap[initialLang],
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
  }
);
myCodeMirror.setSize("100%", "50vh");

// Set initial code content
if (window.latestCode && window.latestCode.trim().length > 0) {
  myCodeMirror.setValue(window.latestCode);
} else {
  myCodeMirror.setValue(boilerplates[initialLang]);
}

// Track whether user has modified the editor
let userModified = false;
myCodeMirror.on("change", function () {
  userModified = true;
});

langSelect.addEventListener("change", function () {
  const selectedLang = this.value;

  myCodeMirror.setOption("mode", languageModeMap[selectedLang]);

  // Only insert boilerplate if user hasn’t typed their own code yet
  myCodeMirror.setValue(boilerplates[selectedLang]);
});

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
        data.output || data.error || data.message || "No output";
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
