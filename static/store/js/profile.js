function showLoading(button) {
  const $button = $(button);
  const originalText = $button.text();
  $button.data("original-text", originalText);
  $button.prop("disabled", true);
  $button.html(
    '<div class="spinner-border spinner-border-sm text-light" role="status"></div>',
  );
}

function hideLoading(button) {
  const $button = $(button);
  const originalText = $button.data("original-text") || "تایید";
  $button.prop("disabled", false);
  $button.html(originalText);
}

function showToast(message, type = "success") {
  const toastEl = $("#toast-message");
  if (toastEl.length) {
    toastEl
      .removeClass("bg-success bg-danger")
      .addClass(type === "success" ? "bg-success" : "bg-danger");
    toastEl.find(".toast-body").text(message);
    const toast = new bootstrap.Toast(toastEl[0]);
    toast.show();
  } else {
    console.log("Toast element not found");
  }
}

const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

const csrftoken = getCookie("csrftoken");

// فرم موبایل
document
  .getElementById("submit-mobile")
  .addEventListener("click", function (event) {
    event.preventDefault();
    const form = document.getElementById("mobile-form");
    const mobileInput = form.querySelector('[name="mobile"]');
    const mobileValue = mobileInput.value.trim();
    const button = form.querySelector("button");

    const existingError = mobileInput.parentNode.querySelector(".text-danger");
    if (existingError) existingError.remove();

    if (!mobileValue) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً شماره موبایل را وارد کنید.";
      mobileInput.parentNode.appendChild(errorDiv);
      return;
    }

    if (!/^\d{11}$/.test(mobileValue)) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "شماره موبایل باید 11 رقمی و فقط شامل اعداد باشد.";
      mobileInput.parentNode.appendChild(errorDiv);
      return;
    }

    showLoading(button);

    const formData = new FormData(form);
    fetch("/users/update-mobile/", {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success && data.next_step === "verify_otp") {
          showToast(`کد تایید به شماره ${mobileValue} ارسال شد . `);
          setTimeout(() => {
            hideLoading(button);
            const otpModal = $(
              '[data-remodal-id="personal-info-otp-modal"]',
            ).remodal();
            otpModal.open();
          }, 2000);
        } else {
          for (var field in data.errors) {
            var error = data.errors[field];
            var input = form.querySelector(`[name="${field}"]`);
            var errorDiv = document.createElement("div");
            errorDiv.className = "text-danger";
            errorDiv.innerText = error[0];
            input.parentNode.appendChild(errorDiv);
          }
          if (data.error) {
            showToast(data.error, "error");
          }
        }
      })
      .catch((error) => {
        hideLoading(button);
        console.error("Error:", error);
      });
  });

// فرم تأیید OTP
document
  .getElementById("submit-otp")
  .addEventListener("click", function (event) {
    event.preventDefault();
    const form = document.getElementById("otp-form");
    const otpInput = form.querySelector('[name="otp"]');
    const otpValue = otpInput.value.trim();
    const button = form.querySelector("button");

    const existingError = otpInput.parentNode.querySelector(".text-danger");
    if (existingError) existingError.remove();

    if (!otpValue) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً کد تأیید را وارد کنید.";
      otpInput.parentNode.appendChild(errorDiv);
      return;
    }

    if (!/^\d+$/.test(otpValue)) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "کد تأیید باید فقط شامل اعداد باشد.";
      otpInput.parentNode.appendChild(errorDiv);
      return;
    }

    showLoading(button);

    const formData = new FormData(form);
    fetch("/users/verify-mobile-otp/", {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast("شماره موبایل با موفقیت تغییر یافت.");
          setTimeout(() => {
            hideLoading(button);
            location.reload();
          }, 2000);
        } else {
          for (var field in data.errors) {
            var error = data.errors[field];
            var input = form.querySelector(`[name="${field}"]`);
            var errorDiv = document.createElement("div");
            errorDiv.className = "text-danger";
            errorDiv.innerText = error[0];
            input.parentNode.appendChild(errorDiv);
          }
          if (data.error) {
            showToast(data.error, "error");
          }
        }
      })
      .catch((error) => {
        hideLoading(button);
        console.error("Error:", error);
      });
  });

// فرم نام و نام خانوادگی
document
  .getElementById("submit-fullname")
  .addEventListener("click", function (event) {
    event.preventDefault();
    const form = document.getElementById("fullname-form");
    const firstNameInput = form.querySelector('[name="first_name"]');
    const lastNameInput = form.querySelector('[name="last_name"]');
    const firstNameValue = firstNameInput.value.trim();
    const lastNameValue = lastNameInput.value.trim();
    const button = form.querySelector("button");

    [firstNameInput, lastNameInput].forEach((input) => {
      const existingError = input.parentNode.querySelector(".text-danger");
      if (existingError) existingError.remove();
    });

    let hasError = false;

    if (!firstNameValue) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً نام را وارد کنید.";
      firstNameInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    if (!lastNameValue) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً نام خانوادگی را وارد کنید.";
      lastNameInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    if (firstNameValue.length > 15) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "نام نباید بیشتر از 15 حرف باشد.";
      firstNameInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    if (lastNameValue.length > 15) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "نام خانوادگی نباید بیشتر از 15 حرف باشد.";
      lastNameInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    if (hasError) return;

    showLoading(button);

    const formData = new FormData(form);
    fetch("/users/update-full-name/", {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast("نام و نام خانوادگی با موفقیت آپدیت شد.");
          setTimeout(() => {
            hideLoading(button);
            location.reload();
          }, 2000);
        } else {
          for (var field in data.errors) {
            var error = data.errors[field];
            var input = form.querySelector(`[name="${field}"]`);
            var errorDiv = document.createElement("div");
            errorDiv.className = "text-danger";
            errorDiv.innerText = error[0];
            input.parentNode.appendChild(errorDiv);
          }
        }
      })
      .catch((error) => {
        hideLoading(button);
        console.error("Error:", error);
      });
  });

// فرم ایمیل
document
  .getElementById("submit-email")
  .addEventListener("click", function (event) {
    event.preventDefault();
    const form = document.getElementById("email-form");
    const emailInput = form.querySelector('[name="email"]');
    const emailValue = emailInput.value.trim();
    const button = form.querySelector("button");

    const existingError = emailInput.parentNode.querySelector(".text-danger");
    if (existingError) existingError.remove();

    if (!emailValue) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً ایمیل را وارد کنید.";
      emailInput.parentNode.appendChild(errorDiv);
      return;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(emailValue)) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً یک ایمیل معتبر وارد کنید.";
      emailInput.parentNode.appendChild(errorDiv);
      return;
    }

    showLoading(button);

    const formData = new FormData(form);
    fetch("/users/update-email/", {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast("ایمیل با موفقیت آپدیت شد.");
          setTimeout(() => {
            hideLoading(button);
            location.reload();
          }, 2000);
        } else {
          for (var field in data.errors) {
            var error = data.errors[field];
            var input = form.querySelector(`[name="${field}"]`);
            var errorDiv = document.createElement("div");
            errorDiv.className = "text-danger";
            errorDiv.innerText = error[0];
            input.parentNode.appendChild(errorDiv);
          }
        }
      })
      .catch((error) => {
        hideLoading(button);
        console.error("Error:", error);
      });
  });

// فرم تاریخ تولد
document
  .getElementById("submit-birth")
  .addEventListener("click", function (event) {
    event.preventDefault();
    const form = document.getElementById("birth-form");
    const yearInput = form.querySelector('[name="year"]');
    const monthInput = form.querySelector('[name="month"]');
    const dayInput = form.querySelector('[name="day"]');
    const yearValue = yearInput.value.trim();
    const monthValue = monthInput.value.trim();
    const dayValue = dayInput.value.trim();
    const button = form.querySelector("button");

    [yearInput, monthInput, dayInput].forEach((input) => {
      const existingError = input.parentNode.querySelector(".text-danger");
      if (existingError) existingError.remove();
    });

    let hasError = false;

    if (!yearValue) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً سال را وارد کنید.";
      yearInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    if (!monthValue) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً ماه را انتخاب کنید.";
      monthInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    if (!dayValue) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً روز را وارد کنید.";
      dayInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    const year = parseInt(yearValue, 10);
    if (!isNaN(year) && (year < 1300 || year > 1403)) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "سال باید بین 1300 تا 1403 باشد.";
      yearInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    const month = parseInt(monthValue, 10);
    if (!isNaN(month) && (month < 1 || month > 12)) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "ماه باید بین 1 تا 12 باشد.";
      monthInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    const day = parseInt(dayValue, 10);
    if (!isNaN(day) && (day < 1 || day > 31)) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "روز باید بین 1 تا 31 باشد.";
      dayInput.parentNode.appendChild(errorDiv);
      hasError = true;
    }

    if (hasError) return;

    showLoading(button);

    const formData = new FormData(form);
    fetch("/users/update-birth-date/", {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast("تاریخ تولد با موفقیت آپدیت شد.");
          setTimeout(() => {
            hideLoading(button);
            location.reload();
          }, 2000);
        } else {
          for (var field in data.errors) {
            var error = data.errors[field];
            var input = form.querySelector(`[name="${field}"]`);
            var errorDiv = document.createElement("div");
            errorDiv.className = "text-danger";
            errorDiv.innerText = error[0];
            input.parentNode.appendChild(errorDiv);
          }
        }
      })
      .catch((error) => {
        hideLoading(button);
        console.error("Error:", error);
      });
  });

// فرم آواتار
document
  .getElementById("submit-avatar")
  .addEventListener("click", function (event) {
    event.preventDefault();
    const form = document.getElementById("avatar-form");
    const avatarInput = form.querySelector('[name="avatar"]');
    const button = form.querySelector("button");

    const existingError = avatarInput.parentNode.querySelector(".text-danger");
    if (existingError) existingError.remove();

    const file = avatarInput.files[0];
    if (!file) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "لطفاً یک فایل انتخاب کنید.";
      avatarInput.parentNode.appendChild(errorDiv);
      return;
    }

    const allowedTypes = ["image/jpeg", "image/png"];
    if (!allowedTypes.includes(file.type)) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "فقط فایل‌های JPG و PNG مجاز هستند.";
      avatarInput.parentNode.appendChild(errorDiv);
      return;
    }

    const maxSize = 2 * 1024 * 1024;
    if (file.size > maxSize) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-danger";
      errorDiv.innerText = "حجم فایل نباید بیشتر از 2 مگابایت باشد.";
      avatarInput.parentNode.appendChild(errorDiv);
      return;
    }

    showLoading(button);

    const formData = new FormData(form);
    fetch("/users/update-avatar/", {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showToast("عکس پروفایل با موفقیت آپدیت شد.");
          setTimeout(() => {
            hideLoading(button);
            location.reload();
          }, 2000);
        } else {
          for (var field in data.errors) {
            var error = data.errors[field];
            var input = form.querySelector(`[name="${field}"]`);
            var errorDiv = document.createElement("div");
            errorDiv.className = "text-danger";
            errorDiv.innerText = error[0];
            input.parentNode.appendChild(errorDiv);
          }
        }
      })
      .catch((error) => {
        hideLoading(button);
        console.error("Error:", error);
      });
  });
