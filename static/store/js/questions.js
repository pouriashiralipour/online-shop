$(document).ready(function () {
  function showLoading(button) {
    const originalText = button.text();
    button.data("original-text", originalText);
    button.prop("disabled", true);
    button.html(
      '<div class="spinner-border spinner-border-sm text-light" role="status"></div>',
    );
  }

  function hideLoading(button) {
    const originalText = button.data("original-text");
    button.prop("disabled", false);
    button.html(originalText);
  }

  function showToast(message, type = "success") {
    const $toastEl = $("#toast-message");
    if ($toastEl.length) {
      $toastEl
        .removeClass("bg-success bg-danger")
        .addClass(type === "success" ? "bg-success" : "bg-danger")
        .find(".toast-body")
        .text(message);
      const toast = new bootstrap.Toast($toastEl[0]);
      toast.show();
    } else {
      console.log("Toast element not found");
    }
  }

  $("#question_id").on("submit", function (e) {
    e.preventDefault();
    const $form = $(this);
    const $button = $form.find(".send");
    const $textField = $form.find('textarea[name="text"]');
    let $errorContainer = $textField.next(".text-danger.fs-7.mt-1");

    if (!$errorContainer.length) {
      $errorContainer = $(
        '<div class="text-danger fs-7 mt-1"></div>',
      ).insertAfter($textField);
    }

    if (!$textField.val().trim()) {
      $errorContainer.text("لطفاً متن پرسش را وارد کنید.");
      return;
    } else {
      $errorContainer.text("");
    }
    showLoading($button);
    $.ajax({
      url: $form.attr("action"),
      method: "POST",
      data: new FormData($form[0]),
      processData: false,
      contentType: false,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .done(function (data) {
        if (data.success) {
          showToast("پس از بررسی پرسش شما در سایت نمایش داده می‌شود");
          setTimeout(() => {
            hideLoading($button);
            $form[0].reset();
          }, 2000);
        } else {
          $errorContainer.text(
            data.error || "خطایی رخ داد. لطفاً دوباره تلاش کنید.",
          );
        }
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        hideLoading($button);
        $errorContainer.text("خطایی رخ داد. لطفاً دوباره تلاش کنید.");
        console.error("Error:", errorThrown);
      });
  });

  $("form#answer_id").on("submit", function (e) {
    e.preventDefault();
    const $form = $(this);
    const $button = $form.find(".send-answer");
    const $textField = $form.find('textarea[name="text"]');
    let $errorContainer = $textField.next(".text-danger.fs-7.mt-1");

    if (!$errorContainer.length) {
      $errorContainer = $(
        '<div class="text-danger fs-7 mt-1"></div>',
      ).insertAfter($textField);
    }

    if (!$textField.val().trim()) {
      $errorContainer.text("لطفاً متن پاسخ را وارد کنید.");
      return;
    } else {
      $errorContainer.text("");
    }
    showLoading($button);
    $.ajax({
      url: $form.attr("action"),
      method: "POST",
      data: new FormData($form[0]),
      processData: false,
      contentType: false,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .done(function (data) {
        if (data.success) {
          showToast("پس از بررسی پاسخ شما در سایت نمایش داده می‌شود");
          setTimeout(() => {
            hideLoading($button);
            $form[0].reset();
            const $collapse = $form.closest(".collapse");
            bootstrap.Collapse.getInstance($collapse[0]).hide();
          }, 2000);
        } else {
          $errorContainer.text(
            data.error || "خطایی رخ داد. لطفاً دوباره تلاش کنید.",
          );
        }
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        hideLoading($button);
        $errorContainer.text("خطایی رخ داد. لطفاً دوباره تلاش کنید.");
        console.error("Error:", errorThrown);
      });
  });

  $(document).on("click", ".answer-like, .answer-dislike", function () {
    const $button = $(this);
    const $answerContainer = $button.closest("[data-answer-id]");
    const answerId = $answerContainer.data("answer-id");
    const action = $button.hasClass("answer-like") ? "like" : "dislike";

    if (!answerId) {
      showToast("شناسه پاسخ یافت نشد.");
      return;
    }

    $.ajax({
      url: `/products/answer/${answerId}/${action}/`,
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/json",
      },
    })
      .done(function (data) {
        if (data.success) {
          const $commentFooter = $button.closest(".comment-footer");
          const $likeBtn = $commentFooter.find(".answer-like");
          const $dislikeBtn = $commentFooter.find(".answer-dislike");
          const $likeCountSpan = $likeBtn.next("span");
          const $dislikeCountSpan = $dislikeBtn.next("span");

          $likeCountSpan.text(data.likes);
          $dislikeCountSpan.text(data.dislikes);

          if (action === "like") {
            $likeBtn.addClass("active").prop("disabled", true);
            $dislikeBtn.removeClass("active").prop("disabled", true);
          } else {
            $dislikeBtn.addClass("active").prop("disabled", true);
            $likeBtn.removeClass("active").prop("disabled", true);
          }
        } else {
          showToast(data.error || "خطایی رخ داده است");
        }
      })
      .fail(function () {
        showToast("خطایی در ارتباط با سرور رخ داده است");
      });
  });

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
});
