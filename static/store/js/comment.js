document.addEventListener('DOMContentLoaded', function () {
  let advantages = [];
  let disadvantages = [];
  let addAdvantagesButton = document.getElementById('add-advantages');
  let addDisadvantagesButton = document.getElementById('add-disadvantages');

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

  if (addAdvantagesButton) {
    document
      .getElementById('add-advantages')
      .addEventListener('click', function () {
        addAdvantages();
      });
  }

  if (addDisadvantagesButton) {
    document
      .getElementById('add-disadvantages')
      .addEventListener('click', function () {
        addDisadvantages();
      });
  }

  function updateAdvantages() {
    let advantagesField = document.getElementById('id_advantages');
    advantagesField.value = JSON.stringify(advantages);

    let advantagesList = document.getElementById('advantages-list');
    advantagesList.innerHTML = '';
    advantages.forEach(function (advantage) {
      let div = document.createElement('div');
      div.textContent = advantage;
      div.classList.add('comment-dynamic-label', 'advantage-item');
      advantagesList.appendChild(div);
    });
  }

  function updateDisadvantages() {
    let disadvantagesField = document.getElementById('id_disadvantages');
    disadvantagesField.value = JSON.stringify(disadvantages);

    let disadvantagesList = document.getElementById('disadvantages-list');
    disadvantagesList.innerHTML = '';
    disadvantages.forEach(function (disadvantage) {
      let div = document.createElement('div');
      div.textContent = disadvantage;
      div.classList.add('comment-dynamic-label', 'disadvantage-item');
      disadvantagesList.appendChild(div);
    });
  }

  function addAdvantages() {
    let advantageInput = document.getElementById('advantage-input');
    let advantageValue = advantageInput.value.trim();
    if (advantageValue) {
      advantages.push(advantageValue);
      updateAdvantages();
      advantageInput.value = '';
    }
  }

  function addDisadvantages() {
    let disadvantageInput = document.getElementById('disadvantages-input');
    let disadvantageValue = disadvantageInput.value.trim();
    if (disadvantageValue) {
      disadvantages.push(disadvantageValue);
      updateDisadvantages();
      disadvantageInput.value = '';
    }
  }

  $(document).on('click', '.comments-like, .comments-dislike', function () {
    const $button = $(this);
    const $commentContainer = $button.closest('[data-comment-id]');
    const commentId = $commentContainer.data('comment-id');
    const action = $button.hasClass('comments-like') ? 'like' : 'dislike';

    if (!commentId) {
      showToast('شناسه دیدگاه یافت نشد.');
      return;
    }

    $.ajax({
      url: `/products/comment/${commentId}/${action}/`,
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
      },
    })
      .done(function (data) {
        if (data.success) {
          const $commentFooter = $button.closest('.comment-footer');
          const $likeBtn = $commentFooter.find('.comments-like');
          const $dislikeBtn = $commentFooter.find('.comments-dislike');
          const $likeCountSpan = $likeBtn.next('span');
          const $dislikeCountSpan = $dislikeBtn.next('span');
          $likeCountSpan.text(data.likes);
          $dislikeCountSpan.text(data.dislikes);
          if (action === 'like') {
            $likeBtn.addClass('active').prop('disabled', true);
            $dislikeBtn.removeClass('active').prop('disabled', true);
          } else {
            $dislikeBtn.addClass('active').prop('disabled', true);
            $likeBtn.removeClass('active').prop('disabled', true);
          }
        } else {
          showToast(data.error || 'خطایی رخ داده است');
        }
      })
      .fail(function () {
        showToast('خطایی در ارتباط با سرور رخ داده است');
      });
  });
});
