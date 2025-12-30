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
    const originalText = button.data('original-text');
    button.prop('disabled', false);
    button.html(originalText);
  }

  function showToast(message, type = 'success') {
    const $toastEl = $('#toast-message');
    if ($toastEl.length) {
      $toastEl
        .removeClass('bg-success bg-danger')
        .addClass(type === 'success' ? 'bg-success' : 'bg-danger')
        .find('.toast-body')
        .text(message);
      const toast = new bootstrap.Toast($toastEl[0]);
      toast.show();
    } else {
      console.log('Toast element not found');
    }
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  $(document).on('submit', '.contact-us-form', function (e) {
    e.preventDefault();
    const $this = $(this);
    const $button = $this.find('.sign-form-contact .btn');

    showLoading($button);

    const formData = new FormData(this);
    formData.append('csrfmiddlewaretoken', csrftoken);

    $.ajax({
      url: '/contact-us/',
      method: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      dataType: 'json',
      success: function (response) {
        if (response.success) {
          showToast(
            'پیام شما با موفقیت ارسال شد و در حال بررسی است.',
            'success'
          );
          $this[0].reset();
        } else {
          showToast(
            response.message || 'خطایی در ارسال پیام رخ داد.',
            'danger'
          );
        }
        hideLoading($button);
      },
      error: function (xhr) {
        let errorMessage = 'خطایی در ارسال پیام رخ داد.';
        if (xhr.responseJSON && xhr.responseJSON.errors) {
          errorMessage = Object.values(xhr.responseJSON.errors).join(' ');
        }
        showToast(errorMessage, 'danger');
        hideLoading($button);
      },
    });
  });
});
