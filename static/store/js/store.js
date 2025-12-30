$(document).ready(function () {
  // افزودن نقاط قوت
  $(".js-advantages-list").on("click", ".js-icon-form-remove", function () {
    $(this).parent().remove();
  });

  $("#advantages .js-icon-form-add").on("click", function () {
    var input = $("#advantage-input").val().trim();
    if (input) {
      $(".js-advantages-list").append(
        '<span class="comment-dynamic-label"><span class="text">' +
          input +
          '</span><button type="button" class="js-icon-form-remove"><i class="ri-close-line"></i></button></span>',
      );
      $("#advantage-input").val("");
    }
  });

  // افزودن نقاط ضعف
  $(".js-disadvantages-list").on("click", ".js-icon-form-remove", function () {
    $(this).parent().remove();
  });

  $("#disadvantages .js-icon-form-add").on("click", function () {
    var input = $("#disadvantage-input").val().trim();
    if (input) {
      $(".js-disadvantages-list").append(
        '<span class="comment-dynamic-label"><span class="text">' +
          input +
          '</span><button type="button" class="js-icon-form-remove"><i class="ri-close-line"></i></button></span>',
      );
      $("#disadvantage-input").val("");
    }
  });

  // ارسال فرم نظر
  $(".add-comment-product").on("submit", function (e) {
    e.preventDefault();
    var form = $(this);
    var advantages = [];
    var disadvantages = [];
    $(".js-advantages-list .comment-dynamic-label .text").each(function () {
      advantages.push($(this).text());
    });
    $(".js-disadvantages-list .comment-dynamic-label .text").each(function () {
      disadvantages.push($(this).text());
    });

    $.ajax({
      url: form.attr("action"),
      type: "POST",
      data: {
        title: form.find('input[name="title"]').val(),
        text: form.find("textarea").val(),
        advantages: advantages,
        disadvantages: disadvantages,
        build_quality: $("#ex19").val(),
        value_for_price: $("#ex20").val(),
        innovation: $("#ex21").val(),
        features: $("#ex22").val(),
        ease_of_use: $("#ex23").val(),
        design: $("#ex24").val(),
        csrfmiddlewaretoken: "{{ csrf_token }}",
      },
      success: function (response) {
        if (response.success) {
          iziToast.success({ message: response.message });
          form[0].reset();
          $(".js-advantages-list, .js-disadvantages-list").empty();
        } else {
          iziToast.error({ message: response.error });
        }
      },
      error: function () {
        iziToast.error({ message: "خطایی رخ داد!" });
      },
    });
  });
});
