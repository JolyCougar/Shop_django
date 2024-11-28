const slides = document.querySelectorAll('.slide');
const sliderContainer = document.querySelector('.slider-container');
const prevSlideBtn = document.querySelector('.prev-slide');
const nextSlideBtn = document.querySelector('.next-slide');

let currentIndex = 0;

// Показ слайда
function showSlide(index) {
    if (index < 0) {
        currentIndex = slides.length - 1; // Если текущий первый, перейти к последнему
    } else if (index >= slides.length) {
        currentIndex = 0; // Если текущий последний, перейти к первому
    } else {
        currentIndex = index;
    }

    // Сдвиг слайдов
    sliderContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
}

// Кнопки навигации
prevSlideBtn.addEventListener('click', () => showSlide(currentIndex - 1));
nextSlideBtn.addEventListener('click', () => showSlide(currentIndex + 1));

// Автоматическая смена
setInterval(() => {
    showSlide(currentIndex + 1);
}, 5000);

// Переход по клику на слайд
slides.forEach(slide => {
    slide.addEventListener('click', () => {
        const link = slide.getAttribute('data-link');
        if (link) {
            window.location.href = link;
        }
    });
});
