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

  function showLoading(button) {
    const originalText = button.text();
    button.data("original-text", originalText);
    button.prop("disabled", true);
    button.html('<div class="spinner-border spinner-border-sm text-dark" role="status"></div>');
  }

  function hideLoading(button) {
    const originalText = button.data("original-text");
    button.prop("disabled", false);
    button.html(originalText);
  }

  $(document).on("click", "#add-to-wishlist", function (e) {
    e.preventDefault();
    const $this = $(this);
    const product_id = $("#product-id").val();
    const $cart_data = $(".cart-data");

    showLoading($this);

    if (!isAuthenticated) {
      showToast("برای افزودن به سبد بعدی ابتدا وارد حساب کاربری شوید", "danger");
      setTimeout(() => {
        window.location.href = loginRedirectUrl;
        hideLoading($this);
      }, 2500);
      return;
    }

    $.ajax({
      type: "POST",
      url: "/add-to-wishlist/",
      data: {
        product_id: product_id,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        if (response.status === "Product already in wishlist") {
          showToast("محصول در لیست سبد خرید بعدی موجود است ", (type = "danger"));
          setTimeout(() => {
            hideLoading($this);
          }, 1500);
        } else {
          showToast("محصول به سبد خرید بعدی اضافه شد . ", (type = "success"));
          setTimeout(() => {
            $cart_data.load(location.href + " .cart-data > *");
          }, 1500);
        }
      },
      error: function (response) {
        showToast("خطایی در هنگام اضافه کردن به سبد خرید رخ داد", "danger");
      },
    });
  });

  $(document).on("click", ".delete-wishlist", function (e) {
    e.preventDefault();
    const $this = $(this);
    const product_id = $("#product-id").val();
    const $cart_data = $(".cart-data");

    showLoading($this);

    if (!isAuthenticated) {
      showToast("برای حذف از سبد بعدی ابتدا وارد حساب کاربری شوید", "danger");
      setTimeout(() => {
        window.location.href = loginRedirectUrl;
        hideLoading($this);
      }, 2500);
      return;
    }

    $.ajax({
      type: "POST",
      url: "/delete-wishlist/",
      data: {
        product_id: product_id,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        showToast("محصول از لیست حذف شد . ", (type = "success"));
        setTimeout(() => {
          $cart_data.load(location.href + " .cart-data > *");
        }, 1500);
      },
      error: function (response) {
        showToast("خطایی در هنگام حذف رخ داد", "danger");
      },
    });
  });
});
