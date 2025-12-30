$(document).ready(function () {
  function showToast(message, type) {
    const toastEl = $("#toast-message");
    if (toastEl.length) {
      toastEl.removeClass("bg-success bg-danger").addClass(type === "success" ? "bg-success" : "bg-danger");
      toastEl.find(".toast-body").text(message);
      const toast = new bootstrap.Toast(toastEl[0]);
      toast.show();
    } else {
      console.log("Toast element not found");
    }
  }
  function getCookie(name) {
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
  }

  const csrftoken = getCookie("csrftoken");

  function showLoading(button, style) {
    const originalText = button.text();
    button.data("original-text", originalText);
    button.prop("disabled", true);
    button.html(`<div class="spinner-border spinner-border-sm text-${style}" role="status"></div>`);
    setTimeout(() => {
      hideLoading(button);
    }, 2000);
  }

  function hideLoading(button) {
    const originalText = button.data("original-text");
    button.prop("disabled", false);
    button.html(originalText);
  }

  $(document).on("click", "#delete-history", function (e) {
    e.preventDefault();
    $this = $(this);
    const $historyData = $(".history-data");

    showLoading($this, "dark");

    $.ajax({
      url: "/users/dashboard/history/delete/",
      type: "POST",
      data: { product_id: $this.data("product-id") },
      dataType: "json",
      headers: { "X-CSRFToken": csrftoken },
      success: function (response) {
        showToast(response.message, "success");
        setTimeout(() => {
          $historyData.load(location.href + " .history-data > *");
          hideLoading($this);
        }, 1500);
      },
      error: function (response) {
        showToast(response.error, "danger");
      },
    });
  });
});
