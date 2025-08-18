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
    indentWithTabs: true,
    lineWrapping: true,
    scrollbarStyle: "simple",
  }
);
myCodeMirror.setSize("100%", "50vh");

// Set initial code content
if (window.latest_submissions[initialLang]?.code?.length > 0) {
  myCodeMirror.setValue(window.latest_submissions[initialLang].code);
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
  if (window.latest_submissions[selectedLang]?.code?.length > 0) {
    myCodeMirror.setValue(window.latest_submissions[selectedLang].code);
  } else {
    myCodeMirror.setValue(boilerplates[selectedLang]);
  }
});

// Get CSRF token
function getCSRFToken() {
  const cookie = document.cookie
    .split(";")
    .find((c) => c.trim().startsWith("csrftoken="));
  return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}

// Handle Run Button
// Handle Run Button
document.getElementById("runBtn").addEventListener("click", async function () {
  const runBtn = this;
  runBtn.disabled = true;
  runBtn.textContent = "Running";
  document.getElementById("tab-output").click();
  try {
    const code = myCodeMirror.getValue();
    const input = document.getElementById("inputArea").value;
    const language = document.getElementById("languageSelect").value;

    const res = await fetch("/submission/run/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ code, input, language }),
    });

    const data = await res.json();
    document.getElementById("outputArea").value =
      data.output || data.error || data.message || "No output";
  } catch (err) {
    console.error("Run Error:", err);
    toastr.error("Something went wrong while running your code.");
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = "Run";
  }
});

// Handle Submit Button
document
  .getElementById("submitBtn")
  .addEventListener("click", async function () {
    const submitBtn = this;
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";
    document.getElementById("tab-output").click();
    try {
      const code = myCodeMirror.getValue();
      const language = document.getElementById("languageSelect").value;
      const problemId = window.problemId || 1;

      console.log("Submitting Problem ID:", problemId);

      const response = await fetch(`/submission/submit/${problemId}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": getCSRFToken(),
        },
        body: new URLSearchParams({ code, language }),
      });

      const data = await response.json();

      document.getElementById(
        "outputArea"
      ).value = `Verdict: ${data.verdict}\n\nOutput:\n${data.output}`;
    } catch (error) {
      console.error("Submission Error:", error);
      document.getElementById("outputArea").value = "Error during submission";
      toastr.error("Something went wrong while submitting your code.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit";
    }
  });

// Handle AI Review Button
document.addEventListener("DOMContentLoaded", () => {
  const aiBtn = document.getElementById("ai-review-btn");
  if (!aiBtn) return;

  aiBtn.addEventListener("click", async () => {
    if (!window.problemId) {
      toastr.error("Problem ID not found.");
      return;
    }

    try {
      const res = await fetch(`/submission/latest/${window.problemId}/`);
      const data = await res.json();

      if (data.error) {
        toastr.error(data.error);
        return;
      }

      const latestSubmissionId = data.id;
      console.log("Latest submission ID:", latestSubmissionId);

      // 🔜 Next step: Call AI review API using this ID
    } catch (err) {
      console.error("Failed to fetch latest submission:", err);
      toastr.error("Something went wrong while fetching latest submission.");
    }
  });
});

// Tab switching logic
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    // Hide all panels
    document.querySelectorAll(".tab-content").forEach((tab) => {
      tab.classList.add("hidden");
    });

    // Reset button styles
    document.querySelectorAll(".tab-btn").forEach((b) => {
      b.classList.remove("border-b-2", "border-yellow-300", "text-white");
      b.classList.add("text-gray-400");
    });

    // Show correct panel
    if (btn.id === "tab-input") {
      document.getElementById("input-tab").classList.remove("hidden");
    } else {
      document.getElementById("output-tab").classList.remove("hidden");
    }

    // Highlight active button
    btn.classList.add("border-b-2", "border-yellow-300", "text-white");
    btn.classList.remove("text-gray-400");
  });
});

// Default active tab on page load
document.getElementById("tab-input").click();
