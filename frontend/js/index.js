const imageElement = document.getElementById('image');
let index = 0;
let images = [];

// Меняет изображение в слайдшоу
function changeImage() {
    if (images.length === 0) return;
    imageElement.style.opacity = 0;
    setTimeout(() => {
        imageElement.src = images[index];
        imageElement.style.opacity = 1;
        index = (index + 1) % images.length;
    }, 800);
}

// Запускает слайдшоу после загрузки изображений
function startSlideShow() {
    if (images.length === 0) {
        return;
    }
    changeImage();
    setInterval(changeImage, 5000);
}

// Загружает статические изображения (из списка в images.json)
async function loadStaticImages() {
    try {
        const response = await fetch('images.json');
        const data = await response.json();

        if (response.ok) {
            images = data;
        }
    } catch (error) {
        console.log(error);
    }
}

// Определяет источник изображений bd/static и запускает слайдшоу
async function showSlideImages() {
    const data = await getRandomImages();
    const images_temp = data.images;
    const downloadUrl = data.url;
    if (images_temp.length > 0) {
        for (const img of images_temp) {
            images.push(downloadUrl + img.filename);
        }
    } else {
        await loadStaticImages();
    }
    startSlideShow()
}

showSlideImages();
