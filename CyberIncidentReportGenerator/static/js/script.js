/**
 * script.js
 * ---------
 * Small client-side enhancements for the Cybersecurity Incident Report
 * Generator. All real validation happens on the server (app.py), so this
 * file is only responsible for making the UI feel responsive:
 *   1. Basic inline validation before submit (fast feedback, doesn't
 *      replace server-side checks).
 *   2. Making the "Clear Form" button actually clear error states too.
 *   3. Auto-dismissing flash messages after a few seconds.
 *   4. A tiny "generating..." state on the submit button so users know
 *      the FLAN-T5 model is working (it can take a few seconds).
 */

document.addEventListener("DOMContentLoaded", function () {
  initFlashAutoDismiss();
  initIncidentFormValidation();
  initClearFormButton();
});

/* -------------------------------------------------------------------- */
/* 1. Auto-dismiss flash messages                                       */
/* -------------------------------------------------------------------- */
function initFlashAutoDismiss() {
  var flashes = document.querySelectorAll(".flash");
  flashes.forEach(function (el) {
    setTimeout(function () {
      el.style.transition = "opacity 0.6s ease";
      el.style.opacity = "0";
      setTimeout(function () {
        el.remove();
      }, 600);
    }, 4000);
  });
}

/* -------------------------------------------------------------------- */
/* 2. Incident form: lightweight client-side validation                 */
/* -------------------------------------------------------------------- */
function initIncidentFormValidation() {
  var form = document.getElementById("incident-form");
  if (!form) return; // not on the form page

  var submitBtn = form.querySelector('button[type="submit"]');

  form.addEventListener("submit", function (event) {
    var errors = validateIncidentForm(form);

    // Clear old inline error highlights first
    clearFieldErrorStyles(form);

    if (Object.keys(errors).length > 0) {
      event.preventDefault();
      Object.keys(errors).forEach(function (fieldName) {
        highlightFieldError(form, fieldName, errors[fieldName]);
      });
      // Scroll to the first error so the user sees it immediately
      var firstErrorField = form.querySelector(".field-error-inline");
      if (firstErrorField) {
        firstErrorField.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      return;
    }

    // Valid: show a "generating" state, since FLAN-T5 inference takes a
    // few seconds and we don't want users double-clicking Generate.
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = "Generating report...";
    }
  });
}

function validateIncidentForm(form) {
  var errors = {};
  var required = [
    "incident_id", "date", "time", "attack_type", "severity", "source_ip",
    "destination_system", "affected_user", "malware", "detection_tool",
    "status", "action_taken",
  ];

  required.forEach(function (name) {
    var field = form.elements[name];
    if (!field) return;
    var value = (field.value || "").trim();
    if (!value) {
      errors[name] = fieldLabel(name) + " is required.";
    }
  });

  // Date sanity check (HTML date input already constrains format, but
  // double check it isn't empty/garbage)
  var dateField = form.elements["date"];
  if (dateField && dateField.value && isNaN(Date.parse(dateField.value))) {
    errors["date"] = "Please enter a valid date.";
  }

  // Basic IPv4/IPv6-ish check (server does the authoritative check)
  var ipField = form.elements["source_ip"];
  if (ipField && ipField.value.trim()) {
    var ip = ipField.value.trim();
    var ipv4Pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    var looksLikeIpv4 = ipv4Pattern.test(ip);
    var looksLikeIpv6 = ip.indexOf(":") !== -1;
    if (looksLikeIpv4) {
      var octets = ip.split(".").map(Number);
      var allValid = octets.every(function (n) {
        return n >= 0 && n <= 255;
      });
      if (!allValid) {
        errors["source_ip"] = "Source IP has an invalid octet (must be 0-255).";
      }
    } else if (!looksLikeIpv6) {
      errors["source_ip"] = "Source IP does not look like a valid IP address.";
    }
  }

  return errors;
}

function fieldLabel(name) {
  return name
    .split("_")
    .map(function (w) { return w.charAt(0).toUpperCase() + w.slice(1); })
    .join(" ");
}

function highlightFieldError(form, fieldName, message) {
  var field = form.elements[fieldName];
  if (!field) return;

  field.classList.add("input-error");

  var msg = document.createElement("span");
  msg.className = "field-error field-error-inline";
  msg.textContent = message;

  var group = field.closest(".form-group");
  if (group) {
    group.appendChild(msg);
  }
}

function clearFieldErrorStyles(form) {
  form.querySelectorAll(".input-error").forEach(function (el) {
    el.classList.remove("input-error");
  });
  form.querySelectorAll(".field-error-inline").forEach(function (el) {
    el.remove();
  });
}

/* -------------------------------------------------------------------- */
/* 3. Clear Form button                                                 */
/* -------------------------------------------------------------------- */
function initClearFormButton() {
  var clearBtn = document.getElementById("clear-form-btn");
  var form = document.getElementById("incident-form");
  if (!clearBtn || !form) return;

  clearBtn.addEventListener("click", function () {
    // "reset" type already clears field values; we just also need to
    // wipe any error highlighting left over from a failed submission.
    setTimeout(function () {
      clearFieldErrorStyles(form);
    }, 0);
  });
}
