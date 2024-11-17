const slides = document.querySelectorAll('.slide');
const sliderContainer = document.querySelector('.slider-container');
const prevSlideBtn = document.querySelector('.prev-slide');
const nextSlideBtn = document.querySelector('.next-slide');

let currentIndex = 0;

// Переключение слайдов
function showSlide(index) {
    if (index < 0) {
        currentIndex = slides.length - 1; // Если на первом слайде, переходим к последнему
    } else if (index >= slides.length) {
        currentIndex = 0; // Если на последнем слайде, переходим к первому
    } else {
        currentIndex = index;
    }
    sliderContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
}

// Кнопки навигации
prevSlideBtn.addEventListener('click', () => showSlide(currentIndex - 1));
nextSlideBtn.addEventListener('click', () => showSlide(currentIndex + 1));

// Автоматическое переключение
setInterval(() => {
    showSlide(currentIndex + 1);
}, 5000); // Смена каждые 5 секунд

// Переход по клику на слайд
slides.forEach(slide => {
    slide.addEventListener('click', () => {
        const link = slide.getAttribute('data-link');
        if (link) {
            window.location.href = link;
        }
    });
});
