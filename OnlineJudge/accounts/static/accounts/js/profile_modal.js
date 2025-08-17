document.addEventListener("DOMContentLoaded", () => {
  // Expect these to be provided by data-attributes
  const getUrl = window.PROFILE_ENDPOINTS?.get;
  const updateUrl = window.PROFILE_ENDPOINTS?.update;

  if (!getUrl || !updateUrl) {
    console.error(
      "PROFILE_ENDPOINTS missing. Inject window.PROFILE_ENDPOINTS before profile_modal.js."
    );
    return;
  }

  // CSRF helper
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2)
      return decodeURIComponent(parts.pop().split(";").shift());
  }
  const csrftoken = getCookie("csrftoken");

  // Elements
  const editLink = document.getElementById("edit-profile-link");
  const modalEl = document.getElementById("editProfileModal");
  if (!modalEl || !editLink) return; // guard if not on this page

  // Requires Bootstrap JS to be loaded on the page
  const bsModal = new bootstrap.Modal(modalEl);

  const form = document.getElementById("edit-profile-form");
  const bioInput = document.getElementById("form-bio");
  const emailInput = document.getElementById("form-email");
  const linkedinInput = document.getElementById("form-linkedin");
  const fileInput = document.getElementById("form-profile-picture");
  const previewImg = document.getElementById("form-preview");

  // Card elements to update
  const cardBio = document.getElementById("profile-bio");
  const cardEmailSpan = document.getElementById("profile-email");
  const cardLinkedin = document.getElementById("profile-linkedin");
  const cardEmpty = document.getElementById("profile-empty");
  const cardPicture = document.getElementById("profile-picture");

  // Image preview
  if (fileInput && previewImg) {
    fileInput.addEventListener("change", () => {
      const file = fileInput.files && fileInput.files[0];
      if (file) {
        previewImg.src = URL.createObjectURL(file);
        previewImg.style.display = "inline-block";
      } else {
        previewImg.src = "";
        previewImg.style.display = "none";
      }
    });
  }

  // Open modal and prefill
  editLink.addEventListener("click", async (e) => {
    e.preventDefault();

    // clear validation
    for (const el of [bioInput, emailInput, linkedinInput, fileInput]) {
      if (el) el.classList.remove("is-invalid");
    }
    const errIds = [
      "error-bio",
      "error-email",
      "error-linkedin",
      "error-profile_picture",
    ];
    errIds.forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.textContent = "";
    });
    if (previewImg) {
      previewImg.src = "";
      previewImg.style.display = "none";
    }
    if (fileInput) fileInput.value = "";

    try {
      const resp = await fetch(getUrl, { credentials: "same-origin" });
      const json = await resp.json();
      if (!json.ok) throw new Error("Failed to fetch");
      const d = json.data;

      if (bioInput) bioInput.value = d.bio || "";
      if (emailInput) emailInput.value = d.email || "";
      if (linkedinInput) linkedinInput.value = d.linkedin || "";
      if (d.profile_picture_url && previewImg) {
        previewImg.src = d.profile_picture_url;
        previewImg.style.display = "inline-block";
      }

      bsModal.show();
    } catch (err) {
      console.error(err);
      alert("Could not load profile data.");
    }
  });

  // Submit form via AJAX
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    form.querySelector(".save-text").classList.add("d-none");
    form.querySelector(".spinner-border").classList.remove("d-none");

    for (const el of [bioInput, emailInput, linkedinInput, fileInput]) {
      if (el) el.classList.remove("is-invalid");
    }
    const errIds = [
      "error-bio",
      "error-email",
      "error-linkedin",
      "error-profile_picture",
    ];
    errIds.forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.textContent = "";
    });

    try {
      const fd = new FormData(form);

      const resp = await fetch(updateUrl, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        body: fd,
        credentials: "same-origin",
      });

      const json = await resp.json();

      if (!resp.ok || !json.ok) {
        if (json.errors) {
          Object.entries(json.errors).forEach(([field, msgs]) => {
            const input = document.getElementById(`form-${field}`);
            const errBox = document.getElementById(`error-${field}`);
            if (input) input.classList.add("is-invalid");
            if (errBox)
              errBox.textContent = Array.isArray(msgs) ? msgs.join(" ") : msgs;
          });
        } else {
          alert("Failed to save profile.");
        }
        return;
      }

      // Update visible card instantly
      const d = json.data;
      const hasAny =
        (d.bio && d.bio.trim()) ||
        (d.email && d.email.trim()) ||
        (d.linkedin && d.linkedin.trim());

      if (cardEmpty) cardEmpty.classList.toggle("d-none", !!hasAny);
      if (cardBio) {
        cardBio.textContent = d.bio || "";
        cardBio.classList.toggle("d-none", !(d.bio && d.bio.trim()));
      }

      if (cardEmailSpan) {
        const emailWrapper = cardEmailSpan.closest("small");
        if (d.email && d.email.trim()) {
          cardEmailSpan.textContent = d.email;
          if (emailWrapper) emailWrapper.classList.remove("d-none");
        } else {
          cardEmailSpan.textContent = "";
          if (emailWrapper) emailWrapper.classList.add("d-none");
        }
      }

      if (cardLinkedin) {
        const linkWrapper = cardLinkedin.closest("small");
        if (d.linkedin && d.linkedin.trim()) {
          cardLinkedin.href = d.linkedin;
          cardLinkedin.textContent = d.linkedin;
          if (linkWrapper) linkWrapper.classList.remove("d-none");
        } else {
          cardLinkedin.href = "";
          cardLinkedin.textContent = "";
          if (linkWrapper) linkWrapper.classList.add("d-none");
        }
      }

      if (d.profile_picture_url && cardPicture) {
        cardPicture.src = d.profile_picture_url;
      }

      bsModal.hide();
    } catch (err) {
      console.error(err);
      alert("An error occurred while saving.");
    } finally {
      submitBtn.disabled = false;
      form.querySelector(".save-text").classList.remove("d-none");
      form.querySelector(".spinner-border").classList.add("d-none");
    }
  });
});
