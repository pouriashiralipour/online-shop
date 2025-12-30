$(document).ready(function () {
  function showLoading(button) {
    const originalText = button.text();
    button.data('original-text', originalText);
    button.prop('disabled', true);
    button.html(
      '<div class="spinner-border spinner-border-sm text-light" role="status"></div>'
    );
  }

  function hideLoading(button) {
    const originalText = button.data('original-text') || 'ادامه';
    button.prop('disabled', false);
    button.html(originalText);
  }

  function showToast(message, type = 'success') {
    const toastEl = $('#toast-message');
    if (toastEl.length) {
      toastEl
        .removeClass('bg-success bg-danger')
        .addClass(type === 'success' ? 'bg-success' : 'bg-danger');
      toastEl.find('.toast-body').text(message);
      const toast = new bootstrap.Toast(toastEl[0]);
      toast.show();
    } else {
      console.log('Toast element not found');
    }
  }

  $('#logout-link').click(function (e) {
    e.preventDefault();
    showToast('در حال خروج...');
    setTimeout(() => {
      window.location.href = '/users/logout/';
    }, 2000);
  });

  $('.auth-form').on('submit', function (e) {
    e.preventDefault();
    $('.form-error').remove();

    const form = $(this);
    const button = form.find('button');

    if (form.find("input[name='mobile']").length > 0) {
      const mobile = form.find("input[name='mobile']").val();
      if (!/^09\d{9}$/.test(mobile)) {
        form
          .find("input[name='mobile']")
          .after(
            '<div class="form-error text-danger mt-2">شماره موبایل نامعتبر است</div>'
          );
        return;
      }

      showLoading(button);

      $.ajax({
        url: form.attr('action') || window.location.href,
        method: 'POST',
        data: form.serialize(),
        headers: {
          'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val(),
        },
        success: function () {
          showToast('کد تایید ارسال شد');
          setTimeout(() => {
            window.location.href = '/users/verify/';
          }, 2000);
        },
        error: function (xhr) {
          hideLoading(button);
          const response = xhr.responseJSON;
          showToast(response?.error || 'خطا در ارسال شماره موبایل', 'danger');
        },
      });
    }

    if (form.find("input[name='otp']").length > 0) {
      const otp = form.find("input[name='otp']").val();
      if (!/^\d{5}$/.test(otp)) {
        form
          .find("input[name='otp']")
          .after(
            '<div class="form-error text-danger mt-2">کد تایید باید ۵ رقمی باشد</div>'
          );
        return;
      }

      showLoading(button);

      $.ajax({
        url: form.attr('action') || window.location.href,
        method: 'POST',
        data: form.serialize(),
        headers: {
          'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val(),
        },
        success: function (response) {
          showToast('با موفقیت وارد شدید');
          setTimeout(() => {
            window.location.href = response.redirect_url;
          }, 2000);
        },
        error: function (xhr) {
          hideLoading(button);
          const response = xhr.responseJSON;
          const message = response?.error || 'کد اشتباه است';

          form
            .find("input[name='otp']")
            .after(
              '<div class="form-error text-danger mt-2">' + message + '</div>'
            );
        },
      });
    }
  });

  function startCountdown(seconds = 60) {
    let counter = seconds;
    const timerElement = $('#timer--verify-code');
    timerElement.text(
      `${Math.floor(counter / 60)}:${String(counter % 60).padStart(2, '0')}`
    );

    const interval = setInterval(() => {
      counter--;
      if (counter <= 0) {
        clearInterval(interval);
        $('.send-again').addClass('d-inline-block');
        timerElement.text('00:00');
      } else {
        timerElement.text(
          `${Math.floor(counter / 60)}:${String(counter % 60).padStart(2, '0')}`
        );
      }
    }, 1000);
  }

  $('.send-again').on('click', function (e) {
    e.preventDefault();
    $(this).removeClass('d-inline-block');
    showToast('در حال ارسال دوباره کد تایید...');

    $.ajax({
      url: '/users/verify/resent/',
      method: 'POST',
      data: { phone_number: $('#mobile').val() },
      headers: {
        'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val(),
      },
      success: function (response) {
        showToast(response.message, 'success');
        startCountdown();
      },
      error: function (xhr) {
        const errorMessage = xhr.responseJSON?.error || 'خطا در ارسال کد تایید';
        showToast(errorMessage, 'danger');
      },
    });
  });
});
