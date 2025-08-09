document.querySelectorAll(".clickable-row").forEach((row) => {
  row.addEventListener("click", () => {
    const subId = row.dataset.subId;
    const dropdown = document.getElementById(`dropdown-${subId}`);
    dropdown.style.display =
      dropdown.style.display === "table-row" ? "none" : "table-row";
  });
});

function copyToClipboard(codeId, buttonId) {
  const code = document.getElementById(codeId).innerText;
  navigator.clipboard.writeText(code).then(() => {
    const button = document.getElementById(buttonId);
    const originalText = button.innerHTML;

    button.innerHTML = "Copied!";
    button.disabled = true;

    setTimeout(() => {
      button.innerHTML = originalText;
      button.disabled = false;
    }, 3000);
  });
}
function filterSubmissions() {
  const rawInput = document.getElementById("problem-filter").value.trim();
  const searchTerm = rawInput.toLowerCase();

  document.querySelectorAll("tbody tr.clickable-row").forEach((row) => {
    const submissionId = row
      .querySelector("td:nth-child(1)")
      .innerText.trim()
      .toLowerCase(); // #ID
    const problemName = row
      .querySelector("td:nth-child(2)")
      .innerText.trim()
      .toLowerCase(); // Problem name
    const dropdown = document.getElementById(`dropdown-${row.dataset.subId}`);
    const problemId = row.dataset.problemId.toLowerCase(); // from data attribute

    let show = false;

    if (searchTerm.startsWith("#")) {
      // Match submission ID only
      const idSearch = searchTerm.slice(1);
      show = submissionId === idSearch;
    } else if (!isNaN(searchTerm)) {
      // Numeric input: match either problem name OR problem ID
      show = problemName.includes(searchTerm) || problemId === searchTerm;
    } else {
      // String input: match problem name
      show = problemName.includes(searchTerm);
    }

    if (show) {
      row.style.display = "";
      if (dropdown) dropdown.style.display = "none";
    } else {
      row.style.display = "none";
      if (dropdown) dropdown.style.display = "none";
    }
  });
}
function resetFilter() {
  // Clear the filter input
  document.getElementById("problem-filter").value = "";

  // Show all clickable rows
  document.querySelectorAll("tbody tr.clickable-row").forEach((row) => {
    row.style.display = "";
    const dropdown = document.getElementById(`dropdown-${row.dataset.subId}`);
    if (dropdown) dropdown.style.display = "none";
  });
}
