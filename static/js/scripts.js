document.addEventListener("DOMContentLoaded", () => {
    const slides = document.querySelectorAll('.categories-slider .slide');
    const sliderContainer = document.querySelector('.categories-slider .slider-container');

    let currentIndex = 0;

    // Функция для показа слайда
    function showSlide(index) {
        if (index < 0) {
            currentIndex = slides.length - 1;
        } else if (index >= slides.length) {
            currentIndex = 0;
        } else {
            currentIndex = index;
        }

        sliderContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    // Обработчики для кнопок "Prev" и "Next" на каждом слайде
    slides.forEach((slide, index) => {
        const prevButton = slide.querySelector('.prev-slide');
        const nextButton = slide.querySelector('.next-slide');

        prevButton.addEventListener('click', () => {
            showSlide(currentIndex - 1);
        });

        nextButton.addEventListener('click', () => {
            showSlide(currentIndex + 1);
        });
    });

    // Автоматическое переключение слайдов каждые 5 секунд
    setInterval(() => {
        showSlide(currentIndex + 1);
    }, 5000);

    // Показать первый слайд при загрузке страницы
    showSlide(currentIndex);
});
