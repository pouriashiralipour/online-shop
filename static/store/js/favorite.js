$(document).ready(function () {
  function initializeRemodals() {
    $("[data-remodal-id]").each(function () {
      const $modal = $(this);
      if (!$modal.data("remodal")) {
        $modal.remodal({
          hashTracking: false,
        });
      }
    });
  }
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

  $(document).on("click", ".favorite-action", function (e) {
    e.preventDefault();
    const $this = $(this);
    const product_id = $(this).data("product-id");
    const isInFavorite = $this.hasClass("remove-favorite-list");
    const actionUrl = isInFavorite ? "/delete-favoritelist/" : "/add-to-favorite/";
    // const $product_favorite = $(".product-favorite");
    const $favorite_header_data = $(".favorite-header-data");

    if (!isAuthenticated) {
      showToast("برای افزودن به علاقه‌مندی ابتدا وارد حساب کاربری شوید", "danger");
      setTimeout(() => {
        window.location.href = loginRedirectUrl;
        hideLoading($this);
      }, 2500);
      return;
    }

    $.ajax({
      type: "POST",
      url: actionUrl,
      data: {
        product_id: product_id,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        if (isInFavorite) {
          showToast("محصول از لیست علاقه‌مندی حذف شد.", "success");
          $this.removeClass("remove-favorite-list").addClass("add-favorite-home");
          $this.find("i").removeClass("ri-heart-3-fill text-danger").addClass("ri-heart-3-line");
        } else {
          showToast("محصول به لیست علاقه‌مندی اضافه شد.", "success");
          $this.removeClass("add-favorite-home").addClass("remove-favorite-list");
          $this.find("i").removeClass("ri-heart-3-line").addClass("ri-heart-3-fill text-danger");
        }
        $favorite_header_data.load(location.href + " .favorite-header-data > *");
      },
      error: function (response) {
        showToast("خطایی در هنگام اضافه کردن به سبد خرید رخ داد", "danger");
      },
    });
  });

  $(document).on("click", ".add-favorite, .remove-favorite-list", function (e) {
    e.preventDefault();
    const $this = $(this);
    const product_id = $this.data("product-id");
    const $product_favorite = $(".product-favorite");
    const $favorite_header_data = $(".favorite-header-data");
    const isRemove = $this.hasClass("remove-favorite-list");
    const actionUrl = isRemove ? "/delete-favoritelist/" : "/add-to-favorite/";

    if (!isAuthenticated) {
      showToast("برای افزودن/حذف از علاقه‌مندی ابتدا وارد حساب کاربری شوید", "danger");
      setTimeout(() => {
        window.location.href = loginRedirectUrl;
      }, 2500);
      return;
    }

    // showLoading($this, "dark");

    $.ajax({
      type: "POST",
      url: actionUrl,
      data: {
        product_id: product_id,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        if (isRemove) {
          showToast("محصول از لیست علاقه‌مندی حذف شد.", "success");
        } else {
          showToast("محصول به لیست علاقه‌مندی اضافه شد.", "success");
        }
        setTimeout(() => {
          $product_favorite.load(location.href + " .product-favorite > *");
          $favorite_header_data.load(location.href + " .favorite-header-data > *");
        }, 1500);
      },
      error: function () {
        showToast("خطایی رخ داد. لطفاً دوباره تلاش کنید.", "danger");
      },
    });
  });

  $(document).on("click", "[data-remodal-target^='remove-from-favorite-modal-']", function (e) {
    e.preventDefault();
    const productId = $(this).data("product-id");
    console.log("Opening favorite delete modal with productId:", productId);
    if (!productId || isNaN(productId)) {
      showToast("شناسه محصول نامعتبر است.", "error");
      return;
    }
    $(`[data-remodal-id="remove-from-favorite-modal-${productId}"] .remove-favorite`).attr("data-product-id", productId);
  });

  $(document).on("click", ".remove-favorite", function (e) {
    e.preventDefault();
    const $this = $(this);
    const productId = $this.data("product-id");
    const modal = $(`[data-remodal-id="remove-from-favorite-modal-${productId}"]`);
    const $favorite_header_data = $(".favorite-header-data");
    const $favorite_data = $(".favorite-data");

    if (!productId || isNaN(productId)) {
      showToast("شناسه محصول نامعتبر است.", "error");
      return;
    }

    if (!modal.length) {
      showToast("مودال حذف پیدا نشد.", "error");
      return;
    }

    showLoading($this, "light");
    $this.prop("disabled", true);

    if (!isAuthenticated) {
      showToast("برای حذف از علاقه‌مندی ابتدا وارد شوید", "danger");
      setTimeout(() => {
        window.location.href = loginRedirectUrl;
      }, 2500);
      return;
    }

    $.ajax({
      type: "POST",
      url: "/delete-favoritelist/",
      data: {
        product_id: productId,
        csrfmiddlewaretoken: csrftoken,
      },
      dataType: "json",
      success: function (response) {
        showToast("محصول از لیست علاقه‌مندی حذف شد.", "success");
        setTimeout(() => {
          $favorite_header_data.load(location.href + " .favorite-header-data > *", function () {
            initializeRemodals();
          });
          $favorite_data.load(location.href + " .favorite-data > *", function () {
            $this.prop("disabled", false);
            $this.removeAttr("data-product-id");
            initializeRemodals();
            try {
              const remodalInstance = modal.data("remodal");
              if (remodalInstance) {
                remodalInstance.close();
              } else {
                modal.hide();
              }
            } catch (error) {
              modal.hide();
            }
          });
        }, 1500);
      },
      error: function (xhr) {
        console.error("Delete favorite AJAX error:", xhr.responseText);
        showToast("خطایی در هنگام حذف رخ داد", "danger");
        hideLoading($this);
        $this.prop("disabled", false);
      },
    });
  });

  $(document).on("closed", "[data-remodal-id^='remove-from-favorite-modal-']", function () {
    const productId = $(this).find(".remove-favorite").data("product-id");
    if (productId) {
      $(this).find(".remove-favorite").removeAttr("data-product-id");
      console.log("Favorite delete modal closed, cleared productId:", productId);
    }
  });
});
