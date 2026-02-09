DELETE_ICON = "&#128465;";
CAMERA_ICON = "&#128247;";
CAMERA_WITH_FLASH_ICON = "&#128248;";
VIDEO_ICON = "&#127909;";


// Получим иконку для файла
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {'jpg': CAMERA_ICON, 'jpeg': CAMERA_ICON, 'png': CAMERA_WITH_FLASH_ICON, 'gif': VIDEO_ICON};

    return icons[ext] || '📦';
}

// Создание элемента изображения
function createImageItem(image) {
    const item = document.createElement("div");
    item.className = 'image-item';
    item.dataset.id = image.id;
    
    const shortName = cutLongName(image.name, 34);
    const url = image.url;
    const shortUrl = cutLongName(url, 40);

    const icon = getFileIcon(image.name);

    item.innerHTML = `
    <div class="image-name">
        <span class="image-icon">${icon}</span>
        <span title="${image.name}">${shortName}</span>
    </div>
    <div class="image-url-wrapper">
        <a href="${image.url}" class="image-url" target="_blank@ title="${image.url}">${shortUrl}</a>
    </div>
    <div class="image-delete">
        <button class="delete-button" onclick="deleteImageById(${image.id}, '${image.name}')" title="Delete">${DELETE_ICON}</button>
    </div>
    `

    return item;
}

function showImagesList() {
    const images = getAllImages();
    const list = document.getElementById("imagesList");
    const empty = document.getElementById("emptyState");
    
    list.innerHTML = ""

    if (images.length === 0) {
        empty.style.display = "block";
        return
    }

    empty.style.display = "none";
    images.forEach(image => {
        list.appendChild(createImageItem(image));
    });
}

function deleteImageById(id, name) {
    // const item = document.querySelector(`[data-id="${id}"]`);
    // if (item) {
    //     item.style.display = 'none';
    // }
    // TODO  Тогда надо проверять есть ли еще картинки и показывать пустой список, нет смысла

    deleteImage(id);
    showImagesList();
}

document.addEventListener("DOMContentLoaded", showImagesList());