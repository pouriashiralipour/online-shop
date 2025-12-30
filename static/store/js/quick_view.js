$(document).on("click", ".quick-view-btn", function (e) {
  e.preventDefault();
  const productId = $(this).data("product-id");

  $.ajax({
    url: `/quick-view/${productId}/`,
    method: "GET",
    success: function (res) {
      if (res.success) {
        const p = res.product;
        const modal = $('[data-remodal-id="quick-view-modal"]');

        modal.find(".product-title").text(p.title);
        modal.find(".product-en span").text(p.english_title);

        modal.find(".comments-link").html(`${p.comments_count || 0} دیدگاه کاربران`);
        modal.find(".questions-link").html(`${p.questions_and_answers_count || 0} پرسش و پاسخ`);
        modal.find(".text-muted").html(`(${p.comments_count || 0})`);
        modal.find(".product-rating").html(p.average_rating);

        let colorHtml = "";
        if (p.colors && p.colors.length > 0) {
          p.colors.forEach((c, index) => {
            const isChecked = index === 0 ? "checked" : "";
            colorHtml += `
              <div class="product-variant-item">
                <div class="custom-radio-circle">
                  <input type="radio" class="custom-radio-circle-input"
                         name="productColor" id="productColor${index}" ${isChecked}>
                  <label for="productColor${index}" class="custom-radio-circle-label"
                         data-variant-label="${c.name}">
                    <span class="color" style="background-color: ${c.hex};"
                          data-bs-toggle="tooltip" data-bs-placement="bottom"
                          title="${c.name}"></span>
                  </label>
                </div>
              </div>
            `;
          });
          modal.find(".product-variants").html(colorHtml);

          modal.find(".product-variant-selected").text(p.colors[0]?.name || "بدون انتخاب");

          $('[data-bs-toggle="tooltip"]').tooltip();

          modal.find(".custom-radio-circle-input").on("change", function () {
            const selectedColor = $(this).siblings("label").data("variant-label");
            modal.find(".product-variant-selected").text(selectedColor);
          });
        } else {
          modal.find(".product-variants").html("<span>بدون رنگ</span>");
          modal.find(".product-variant-selected").text("بدون رنگ");
        }

        let breadcrumbHtml = "";
        if (p.tags && p.tags.length > 0) {
          p.tags.forEach((tag, index) => {
            breadcrumbHtml += `
      <li class="breadcrumb-item">
        <a href="/products/tags/${tag.slug}/">${tag.name}</a>
      </li>
    `;
          });
        } else {
          breadcrumbHtml = '<li class="breadcrumb-item"><a href="#">بدون تگ</a></li>';
        }
        modal.find(".breadcrumb").html(breadcrumbHtml);

        let attributesHtml = "";
        if (p.attributes && p.attributes.length > 0) {
          p.attributes.forEach((attr) => {
            attributesHtml += `
              <li>
                <span class="label">${attr.key}:</span>
                <span class="title">${attr.value}</span>
              </li>
            `;
          });
          modal.find(".product-params").html(`<ul>${attributesHtml}</ul>`);
        } else {
          modal.find(".product-params").html("<p>بدون مشخصات</p>");
        }

        const galleryMain = modal.find("#gallery-slider-wrapper");
        const galleryThumbs = modal.find("#gallery-thumbs-wrapper");
        galleryMain.html("");
        galleryThumbs.html("");

        p.gallery.forEach((url) => {
          galleryMain.append(`
            <div class="swiper-slide">
              <div class="gallery-img"><img src="${url}" alt=""></div>
            </div>
          `);
          galleryThumbs.append(`
            <div class="swiper-slide">
              <div class="gallery-thumb"><img src="${url}" alt=""></div>
            </div>
          `);
        });

        modal.find(".remodal-footer a.btn-primary").attr("href", `/products/${p.slug}`);
        modal.find("a.comments-link").attr("href", `/products/${p.slug}`);
        modal.find("a.questions-link").attr("href", `/products/${p.slug}`);

        new Swiper(".gallery-swiper-slider", {
          navigation: { nextEl: ".swiper-button-next", prevEl: ".swiper-button-prev" },
        });
        new Swiper(".gallery-thumbs-swiper-slider", {
          slidesPerView: 4,
          spaceBetween: 10,
        });

        modal.remodal().open();
      } else {
        alert("محصول یافت نشد");
      }
    },
    error: function () {
      alert("خطا در دریافت اطلاعات محصول");
    },
  });
});
