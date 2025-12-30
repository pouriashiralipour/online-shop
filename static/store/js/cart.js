$(document).ready(function () {
  function showInputLoading(inputContainer) {
    inputContainer.addClass("loading-red-border");
    inputContainer.find(".in-num").prop("disabled", true);
    inputContainer.append('<div class="spinner-border spinner-border-sm text-danger loading-spinner" role="status"></div>');
  }

  function showLoading(button, style) {
    const originalText = button.text();
    button.data("original-text", originalText);
    button.prop("disabled", true);
    button.html(`<div class="spinner-border spinner-border-sm text-${style}" role="status"></div>`);
  }

  function hideLoading(button) {
    const originalText = button.data("original-text");
    button.prop("disabled", false);
    button.html(originalText);
  }

  function showToast(message, type = "success") {
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

  $(document).on("click", "#add-to-cart-home", function (e) {
    e.preventDefault();
    const $this = $(this);
    const _index = $this.attr("data-index");
    const product_id = $(".product-id-" + _index).val();
    const $cart_header_data = $(".cart-header-data");
    const $cart_header_data_responsive = $(".cart-header-data-responsive");

    $.ajax({
      type: "POST",
      url: "/add-to-cart/",
      data: {
        id: product_id,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        showToast(response.message, response.success ? "success" : "danger");
        $cart_header_data.load(location.href + " .cart-header-data > *");
        $cart_header_data_responsive.load(location.href + " .cart-header-data-responsive > *");
        $this.find("i").removeClass("ri-shopping-cart-line").addClass("ri-shopping-cart-fill text-danger");
      },
      error: function (xhr) {
        console.log(xhr);
        showToast("خطایی در هنگام اضافه کردن به سبد خرید رخ داد", "danger");
      },
    });
  });

  $(document).on("click", "#add-to-cart", function (e) {
    e.preventDefault();
    const $this = $(this);
    const product_id = $(this).data("product-id");
    const $product_data = $(".product-data");
    const $product_mini_data = $(".product-mini-data");
    const $cart_data = $(".cart-data");
    const $cart_header_data = $(".cart-header-data");
    const $cart_header_data_responsive = $(".cart-header-data-responsive");

    showLoading($this, "light");

    $.ajax({
      type: "POST",
      url: "/add-to-cart/",
      data: {
        id: product_id,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        showToast(response.message, response.success ? "success" : "danger");
        setTimeout(() => {
          $product_data.load(location.href + " .product-data > *");
          $product_mini_data.load(location.href + " .product-mini-data > *");
          $cart_header_data.load(location.href + " .cart-header-data > *");
          $cart_header_data_responsive.load(location.href + " .cart-header-data-responsive > *");
          $cart_data.load(location.href + " .cart-data > *");
          $("#add-to-cart").hide();

          $("#input-add-minus").show();
          $("#input-add-minus .in-num").val(1);
        }, 1000);
      },
      error: function (xhr) {
        console.log(xhr);
        showToast("خطایی در هنگام اضافه کردن به سبد خرید رخ داد", "danger");
      },
    });
  });

  $(document).on("click", "#add-to-cart-mini-cart", function (e) {
    e.preventDefault();
    const $this = $(this);
    const product_id = $(this).data("product-id");
    const $product_data = $(".product-data");
    const $product_mini_data = $(".product-mini-data");
    const $cart_data = $(".cart-data");
    const $cart_header_data = $(".cart-header-data");
    const $cart_header_data_responsive = $(".cart-header-data-responsive");

    showLoading($this, "light");

    $.ajax({
      type: "POST",
      url: "/add-to-cart/",
      data: {
        id: product_id,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        showToast(response.message, response.success ? "success" : "danger");
        setTimeout(() => {
          $product_mini_data.load(location.href + " .product-mini-data > *");
          $product_data.load(location.href + " .product-data > *");
          $cart_header_data.load(location.href + " .cart-header-data > *");
          $cart_header_data_responsive.load(location.href + " .cart-header-data-responsive > *");
          $cart_data.load(location.href + " .cart-data > *");
          $("#add-to-cart").hide();

          $("#input-add-minus").show();
          $("#input-add-minus .in-num").val(1);
        }, 1000);
      },
      error: function (xhr) {
        console.log(xhr);
        showToast("خطایی در هنگام اضافه کردن به سبد خرید رخ داد", "danger");
      },
    });
  });

  $(document).on("click", ".plus", function (e) {
    e.preventDefault();
    const $this = $(this);
    const product_id = $this.data("product-id");
    const $inputContainer = $this.closest(".num-in");
    const $input = $inputContainer.find(".in-num");
    const $product_data = $(".product-data");
    const $cart_data = $(".cart-data");
    const $cart_header_data = $(".cart-header-data");
    const $cart_header_data_responsive = $(".cart-header-data-responsive");
    let quantity = parseInt($input.val());

    showInputLoading($inputContainer);

    $.ajax({
      type: "POST",
      url: "/update-cart-item/",
      data: {
        product_id: product_id,
        quantity: quantity + 1,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        if (response.success) {
          showToast("تعداد محصول به‌روزرسانی شد", "success");
          setTimeout(() => {
            if (quantity > 1) {
              $("#minus-trash").hide();
              $("#minus-span").show();
            }
            $cart_header_data.load(location.href + " .cart-header-data > *");
            $cart_header_data_responsive.load(location.href + " .cart-header-data-responsive > *");
            $product_data.load(location.href + " .product-data > *");
            $cart_data.load(location.href + " .cart-data > *");
            $input.val(response.quantity);
          }, 1000);
        } else {
          showToast(response.message, "danger");
        }
      },
      error: function () {
        showToast("خطایی رخ داد", "danger");
      },
    });
  });

  $(document).on("click", ".minus", function (e) {
    e.preventDefault();
    const $this = $(this);
    const product_id = $this.data("product-id");
    const $inputContainer = $this.closest(".num-in");
    const $input = $inputContainer.find(".in-num");
    const $product_data = $(".product-data");
    const $cart_data = $(".cart-data");
    const $cart_header_data = $(".cart-header-data");
    const $cart_header_data_responsive = $(".cart-header-data-responsive");
    let quantity = parseInt($input.val());

    showInputLoading($inputContainer);

    $.ajax({
      type: "POST",
      url: "/update-cart-item/",
      data: {
        product_id: product_id,
        quantity: quantity - 1,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        if (response.success) {
          showToast(response.message, "success");
          setTimeout(() => {
            if (quantity === 1) {
              $("#minus-trash").show();
              $("#minus-span").hide();
            }
            $cart_header_data.load(location.href + " .cart-header-data > *");
            $cart_header_data_responsive.load(location.href + " .cart-header-data-responsive > *");
            $product_data.load(location.href + " .product-data > *");
            $cart_data.load(location.href + " .cart-data > *");
            $input.val(response.quantity);
          }, 1000);
        } else {
          showToast(response.message, "danger");
        }
      },
      error: function () {
        showToast("خطایی رخ داد", "danger");
      },
    });
  });

  $(document).on("click", ".btn-delete-cart-item", function (e) {
    e.preventDefault();
    const $this = $(this);
    const product_id = $this.data("product-id");
    const $inputContainer = $this.closest(".num-in");
    const $cart_data = $(".cart-data");
    const $product_mini_data = $(".product-mini-data");
    const $product_data = $(".product-data");
    const $cart_header_data = $(".cart-header-data");
    const $cart_header_data_responsive = $(".cart-header-data-responsive");

    showInputLoading($inputContainer);

    $.ajax({
      type: "POST",
      url: "/delete-cart-item/",
      data: {
        product_id: product_id,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        hideLoading($this);
        if (response.success) {
          showToast(response.message, "success");
          setTimeout(() => {
            $("#input-add-minus").hide();
            $("#add-to-cart").show();
            $cart_header_data.load(location.href + " .cart-header-data > *");
            $cart_header_data_responsive.load(location.href + " .cart-header-data-responsive > *");
            $product_data.load(location.href + " .product-data > *");
            $product_mini_data.load(location.href + " .product-mini-data > *");
            $cart_data.load(location.href + " .cart-data > *");
            $("#cart-icon").removeClass("ri-shopping-cart-fill").addClass("ri-shopping-cart-line");
          }, 1000);
        } else {
          showToast(response.message, "danger");
        }
      },
      error: function () {
        hideLoading($this);
        showToast("خطایی رخ داد", "danger");
      },
    });
  });
});
