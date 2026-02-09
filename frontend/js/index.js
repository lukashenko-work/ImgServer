const imageElement = document.getElementById('image');
let index = 0;
let images = [];

function changeImage() {
    if (images.length === 0) return;
    imageElement.style.opacity = 0;
    setTimeout(() => {
        imageElement.src = images[index];
        imageElement.style.opacity = 1;
        index = (index + 1) % images.length;
    }, 800);
}

function startSlideShow() {
    if (images.length === 0) {
        return;
    }
    changeImage();
    setInterval(changeImage, 5000);
}

function loadStaticImages() {
    return;
}

// Показывает изображения с диска
function showStaticImages() {
    fetch('images.json')
    .then(response => response.json())
    .then(data => {
        images = data
        startSlideShow()
    })
    .catch(startSlideShow());
}

// Показываем изображения из LocalStorage
function showStoredImages() {
    const image = images[0];
    alert(image.name);
    let blob = new Blob(image.base64, {type: 'image/gif'});
    // Создаем URL для Blob и присваиваем тегу img
    const imgUrl = URL.createObjectURL(blob);
    alert(imgUrl);
    imageElement.src = imgUrl;
}

// TODO добавить отображение сохраненных изображений
//images = getAllImages();

if (images.length > 0) {
    showStoredImages();
} else {
    showStaticImages();
}