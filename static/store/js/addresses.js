$(document).ready(function () {
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

  function showLoading(button) {
    const originalText = button.text();
    button.data("original-text", originalText);
    button.prop("disabled", true);
    button.html(`<div class="spinner-border spinner-border-sm text-light" role="status"></div>`);
    setTimeout(() => {
      hideLoading(button);
    }, 2000);
  }

  function hideLoading(button) {
    const originalText = button.data("original-text");
    button.prop("disabled", false);
    button.html(originalText);
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

  // Validation
  function validateForm(form) {
    const data = form.serializeArray();
    let errors = [];

    const requiredFields = [
      { name: "recipient_name", label: "نام گیرنده" },
      { name: "recipient_last_name", label: "نام خانوادگی گیرنده" },
      { name: "province", label: "استان" },
      { name: "city", label: "شهر" },
      { name: "mobile", label: "شماره موبایل" },
      { name: "postal_code", label: "کد پستی" },
      { name: "full_address", label: "آدرس کامل" },
    ];

    requiredFields.forEach((field) => {
      const fieldData = data.find((item) => item.name === field.name);
      if (!fieldData || !fieldData.value.trim()) {
        errors.push(`${field.label} الزامی است.`);
      }
    });

    const mobile = form.find('[name="mobile"]').val();
    if (mobile && !/^09\d{9}$/.test(mobile)) {
      errors.push("شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود.");
    }

    const postalCode = form.find('[name="postal_code"]').val();
    if (postalCode && !/^\d{10}$/.test(postalCode)) {
      errors.push("کد پستی باید ۱۰ رقم و بدون خط تیره باشد.");
    }

    return errors;
  }

  const $addressData = $(".address-data");

  function resetForm(form) {
    form[0].reset();
    form.find(".select2").val(null).trigger("change");
  }

  // Initialize Select2
  $(".select2").select2({
    placeholder: "انتخاب کنید",
    allowClear: true,
    width: "100%",
    language: "fa",
  });

  // Load provinces from JSON
  $.getJSON("/static/store/js/data/iran_cities.json", function (data) {
    console.log("first");
    const provinceSelect = $("#province-select");
    const citySelect = $("#city-select");
    const editProvinceSelect = $("#edit-province-select");
    const editCitySelect = $("#edit-city-select");

    // Populate provinces
    data.provinces.forEach(function (province) {
      provinceSelect.append(new Option(province.name, province.name));
      editProvinceSelect.append(new Option(province.name, province.name));
    });

    // Handle province change
    provinceSelect.on("change", function () {
      const selectedProvince = $(this).val();
      citySelect.empty().append(new Option("ابتدا یک استان انتخاب کنید", ""));
      citySelect.prop("disabled", true);

      if (selectedProvince) {
        const provinceData = data.provinces.find((p) => p.name === selectedProvince);
        if (provinceData) {
          provinceData.cities.forEach(function (city) {
            citySelect.append(new Option(city, city));
          });
          citySelect.prop("disabled", false);
        }
      }
      citySelect.trigger("change");
    });

    // Handle province change for edit modal
    editProvinceSelect.on("change", function () {
      const selectedProvince = $(this).val();
      editCitySelect.empty().append(new Option("ابتدا یک استان انتخاب کنید", ""));
      editCitySelect.prop("disabled", true);

      if (selectedProvince) {
        const provinceData = data.provinces.find((p) => p.name === selectedProvince);
        if (provinceData) {
          provinceData.cities.forEach(function (city) {
            editCitySelect.append(new Option(city, city));
          });
          editCitySelect.prop("disabled", false);
        }
      }
      editCitySelect.trigger("change");
    });
  });

  // Handle form submissions with AJAX
  $("#submit-address").click(function (e) {
    e.preventDefault();
    const form = $("#add-address-form");
    const errors = validateForm(form);
    const $modal = $(`[data-remodal-id="add-address-modal"]`);
    $this = $(this);

    showLoading($this);

    if (errors.length > 0) {
      showToast(errors.join(" "), "error");
      hideLoading($this);
      return;
    }

    $.ajax({
      url: "/users/address/add/",
      type: "POST",
      data: form.serialize(),
      headers: { "X-CSRFToken": csrftoken },
      success: function (response) {
        if (response.success) {
          showToast(response.message || "آدرس با موفقیت اضافه شد.", "success");
          setTimeout(() => {
            $addressData.load(location.href + " .address-data > *");
            resetForm(form);
            $("[data-remodal-id='add-address-modal']").remodal().close();
          }, 1000);
        } else {
          showToast(response.error || "خطایی رخ داد.", "error");
          hideLoading($this);
        }
      },
      error: function () {
        showToast("خطایی در ارتباط با سرور رخ داد.", "error");
        hideLoading($this);
      },
    });
  });

  $(document).on("click", "#submit-edit-address", function (e) {
    e.preventDefault();
    $this = $(this);
    const form = $("#edit-address-form");
    const errors = validateForm(form);

    showLoading($this);

    if (errors.length > 0) {
      showToast(errors.join(" "), "error");
      hideLoading($this);
      return;
    }

    const addressId = form.find('[name="address_id"]').val();
    if (!addressId || isNaN(addressId)) {
      showToast("شناسه آدرس نامعتبر است.", "error");
      hideLoading($this);
      return;
    }

    $.ajax({
      url: "/users/address/edit/",
      type: "POST",
      data: form.serialize(),
      headers: { "X-CSRFToken": csrftoken },
      success: function (response) {
        if (response.success) {
          showToast(response.message || "آدرس با موفقیت ویرایش شد.", "success");
          setTimeout(() => {
            $addressData.fadeOut(200, function () {
              $(this).load(location.href + " .address-data > *", function () {
                $(this).fadeIn(200);
                $("[data-remodal-id='edit-address-modal']").remodal().close();
                resetForm(form);
                if ($(".remodal-overlay").length) {
                  console.warn("Overlay still present, removing manually");
                  $(".remodal-overlay").remove();
                }
              });
            });
          }, 1500);
        } else {
          showToast(response.error || "خطایی رخ داد.", "error");
          hideLoading($this);
        }
      },
      error: function () {
        showToast("خطایی در ارتباط با سرور رخ داد.", "error");
        hideLoading($this);
      },
    });
  });

  $(document).on("click", '[data-remodal-target="remove-from-addresses-modal"]', function () {
    const addressId = $(this).data("address-id");
    console.log("Opening delete modal with addressId:", addressId);12
    if (!addressId || isNaN(addressId)) {
      showToast("شناسه آدرس نامعتبر است.", "error");
      return;
    }
    $("#confirm-delete-address").attr("data-address-id", addressId);
  });

  $("#confirm-delete-address").click(function () {
    const $this = $(this);
    const addressId = $this.attr("data-address-id");
    console.log("Confirm delete with addressId:", addressId);

    if (!addressId || isNaN(addressId)) {
      showToast("شناسه آدرس نامعتبر است.", "error");
      return;
    }

    showLoading($this);
    $this.prop("disabled", true);

    $.ajax({
      url: "/users/address/delete/",
      type: "POST",
      data: { address_id: addressId },
      headers: { "X-CSRFToken": csrftoken },
      success: function (response) {
        console.log("Delete response:", response);
        if (response.success) {
          showToast(response.message || "آدرس با موفقیت حذف شد.", "success");
          setTimeout(() => {
            $addressData.load(location.href + " .address-data > *", function () {
              $("[data-remodal-id='remove-from-addresses-modal']").remodal().close();
              $this.prop("disabled", false);
              $this.removeAttr("data-address-id");
            });
          }, 1500);
        } else {
          showToast(response.error || "خطایی رخ داد.", "error");
          hideLoading($this);
          $this.prop("disabled", false);
        }
      },
      error: function (xhr) {
        console.error("Delete AJAX error:", xhr.responseText);
        showToast("خطایی در ارتباط با سرور رخ داد.", "error");
        hideLoading($this);
        $this.prop("disabled", false);
      },
    });
  });

  $("[data-remodal-id='remove-from-addresses-modal']").on("closed", function () {
    $("#confirm-delete-address").removeAttr("data-address-id");
    console.log("Delete modal closed, cleared addressId");
  });

  // Populate edit form
  $(document).on("click", '[data-remodal-target="edit-address-modal"]', function (e) {
    e.preventDefault();
    const addressId = $(this).data("address-id");

    if (!addressId || isNaN(addressId)) {
      showToast("شناسه آدرس نامعتبر است.", "error");
      return;
    }

    $.ajax({
      url: "/users/address/get/",
      type: "GET",
      data: { address_id: addressId },
      success: function (response) {
        if (response.success) {
          const form = $("#edit-address-form");

          form.find('[name="address_id"]').val(response.address.id);
          form.find('[name="recipient_name"]').val(response.address.recipient_name);
          form.find('[name="recipient_last_name"]').val(response.address.recipient_last_name);
          form.find('[name="mobile"]').val(response.address.mobile);
          form.find('[name="postal_code"]').val(response.address.postal_code);
          form.find('[name="full_address"]').val(response.address.full_address);
          form.find('[name="is_default"]').prop("checked", response.address.is_default);

          const provinceSelect = form.find('[name="province"]');
          const citySelect = form.find('[name="city"]');
          provinceSelect.val(response.address.province).trigger("change");
          setTimeout(() => {
            citySelect.val(response.address.city).trigger("change");
          }, 300);
        } else {
          showToast(response.error || "خطایی رخ داد.", "error");
        }
      },
      error: function () {
        showToast("خطایی در دریافت اطلاعات آدرس رخ داد.", "error");
      },
    });
  });
});
