const languageModeMap = {
  cpp: "text/x-c++src",
  java: "text/x-java",
  python: "python",
};
// script for editor
var myCodeMirror = CodeMirror.fromTextArea(
  document.getElementById("codeArea"),
  {
    lineNumbers: true,
    theme: "material",
    mode: languageModeMap["cpp"], // default to C++
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
  }
);

document.getElementById("runBtn").addEventListener("click", () => {
  const code = myCodeMirror.getValue(); // ✅ Correct way to get CodeMirror content
  const input = document.getElementById("inputArea").value;
  const language = document.getElementById("languageSelect").value;

  fetch("/submission/run/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({ code, input, language }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("outputArea").value = data.output || data.error;
    });

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
