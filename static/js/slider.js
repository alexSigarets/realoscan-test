// =====================
// 📁 SLIDER.JS
// Управление слайдером фотографий в карточке квартиры
// =====================

// Логика переключения фотографий
export function setupSlider(card) {
    const photos = card.querySelectorAll(".photo-slider img");
    let currentIndex = 0;

    const showPhoto = (index) => {
        photos.forEach((img, i) => {
            img.style.display = i === index ? "block" : "none";
        });
    };

    const prevBtn = card.querySelector(".prev-btn");
    const nextBtn = card.querySelector(".next-btn");

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener("click", () => {
            currentIndex = (currentIndex - 1 + photos.length) % photos.length;
            showPhoto(currentIndex);
        });

        nextBtn.addEventListener("click", () => {
            currentIndex = (currentIndex + 1) % photos.length;
            showPhoto(currentIndex);
        });
    }
}
