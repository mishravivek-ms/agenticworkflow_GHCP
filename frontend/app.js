"use strict";

const API_LOGIN_URL = "/api/login";

const form = document.getElementById("login-form");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const usernameError = document.getElementById("username-error");
const passwordError = document.getElementById("password-error");
const submitBtn = document.getElementById("submit-btn");
const alertBanner = document.getElementById("alert");

/* ── Helpers ─────────────────────────────────────────────────────────── */

function showAlert(message, type) {
  alertBanner.textContent = message;
  alertBanner.className = `alert alert--${type}`;
  alertBanner.hidden = false;
}

function hideAlert() {
  alertBanner.hidden = true;
  alertBanner.textContent = "";
  alertBanner.className = "alert";
}

function setFieldInvalid(input, errorEl, message) {
  input.classList.add("is-invalid");
  errorEl.textContent = message;
}

function clearFieldError(input, errorEl) {
  input.classList.remove("is-invalid");
  errorEl.textContent = "";
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  if (isLoading) {
    submitBtn.classList.add("btn--loading");
    submitBtn.textContent = "Signing in";
  } else {
    submitBtn.classList.remove("btn--loading");
    submitBtn.textContent = "Login";
  }
}

/* ── Client-side validation ──────────────────────────────────────────── */

function validate() {
  let valid = true;

  if (!usernameInput.value.trim()) {
    setFieldInvalid(usernameInput, usernameError, "Username is required.");
    valid = false;
  } else {
    clearFieldError(usernameInput, usernameError);
  }

  if (!passwordInput.value) {
    setFieldInvalid(passwordInput, passwordError, "Password is required.");
    valid = false;
  } else {
    clearFieldError(passwordInput, passwordError);
  }

  return valid;
}

/* ── Form submission ─────────────────────────────────────────────────── */

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideAlert();

  if (!validate()) return;

  const payload = {
    username: usernameInput.value.trim(),
    password: passwordInput.value,
  };

  setLoading(true);

  try {
    const response = await fetch(API_LOGIN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    let data = null;
    try {
      data = await response.json();
    } catch {
      // Server returned a non-JSON body (e.g. 500 HTML error page)
      showAlert("An unexpected server error occurred. Please try again.", "error");
      return;
    }

    if (response.ok && data.success) {
      showAlert(data.message || "Login successful", "success");
      form.reset();
    } else {
      showAlert(
        data.message || "Invalid username or password",
        "error"
      );
    }
  } catch {
    showAlert(
      "Unable to reach the server. Please try again later.",
      "error"
    );
  } finally {
    setLoading(false);
  }
});

/* ── Clear errors on input ───────────────────────────────────────────── */

usernameInput.addEventListener("input", () =>
  clearFieldError(usernameInput, usernameError)
);
passwordInput.addEventListener("input", () =>
  clearFieldError(passwordInput, passwordError)
);
