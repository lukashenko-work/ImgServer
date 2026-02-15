DELETE_ICON = "&#128465;";
CAMERA_ICON = "&#128247;";
CAMERA_WITH_FLASH_ICON = "&#128248;";
VIDEO_ICON = "&#127909;";

async function deleteImageById(delete_url) {
    try {
        const response = await fetch(delete_url);
        const data = await response.json();

        console.log(data);

        if (response.ok) {
            showStatus(data.message, 'success');
            getImagesFromAPI();
        } else {
            message = data.error;
            showStatus(message, 'error');
        }
    } catch (error) {
        console.log(error);
        showStatus(error.message, 'error');
    } // Обработка ошибок
    
    // const item = document.querySelector(`[data-id="${id}"]`);
    // if (item) {
    //     item.style.display = 'none';
    // }
    // TODO  Тогда надо проверять есть ли еще картинки и показывать пустой список, нет смысла

    //deleteImage(id);
}

async function getImagesFromAPI() {
    // fetch('http://localhost:8000/api/images')
    // TODO replace '/api/images' with environment variable
    try {
        const response = await fetch('/api/images');
        const data = await response.json();

        console.log(data);

        if (response.ok) {
            showImagesListAPI(data)
        } else {
            message = data.error;
            showStatus(message, 'error');
        }
    } catch (error) {
        console.log(error);
        showStatus(error.message, 'error');
    } // Обработка ошибок
}

function showEmptyBlock(show) {
    const empty = document.getElementById("emptyState");
    if (show) {
        empty.style.display = "block";
    } else {
        empty.style.display = "none";
    }
}

function showStatus(message, type) {
    const status = document.getElementById("statusBlock");
    if (!status) return;

    status.textContent = message;
    status.className = `status-block-${type}`;
    status.style.display = 'block';

    if (type === "success") {
        setTimeout(() => {status.style.display = 'none'}, 5000);
    }
}

function showImagesListAPI(data_obj) {
    const list = document.getElementById("imagesList");
    list.innerHTML = "";
    if (!data_obj) {
        showEmptyBlock(true);
        return;
    }

    const images = data_obj.images;
    
    if (images.length === 0) {
        showEmptyBlock(true);
        return;
    }
    
    showEmptyBlock(false);

    const delete_url = data_obj.delete_url;
    const download_url = data_obj.url;

    images.forEach(image => {
        image.url = download_url;
        image.delete_url = delete_url;
        list.appendChild(createImageItemAPI(image));
    });
}

// Создание элемента изображения
function createImageItemAPI(image) {
    const item = document.createElement("div");
    item.className = 'image-item';
    item.dataset.id = image.id;
    
    const shortName = cutLongName(image.original_name, 29);
    // const url = image.url + image.filename;
    const url = image.url + image.filename;
    const delete_url = image.delete_url + image.id;
    const shortUrl = cutLongName(url, 39);
    const original_name = image.original_name;


    // const icon = getFileIconAPI(image.file_type);
    // <span class="image-icon">${icon}</span>

    item.innerHTML = `
    <div class="image-name">
        <span class="image-icon"><img src="images/photo.png" alt="Photo"></span>
        <span title="${original_name}">${shortName}</span>
    </div>
    <div class="image-url-wrapper">
        <a href="${url}" class="image-url" target="_blank" title="${original_name}" download="${original_name}">${shortName}</a>
    </div>
    <div class="image-size">
        <span title="${image.size}">${image.size.toLocaleString('ru-RU', {maximumFractionDigits: 0})}</span>
    </div>
    <div class="image-delete">
        <img src="images/delete.png" class="delete-button" alt="Delete image" title="Delete image ${original_name}" onclick="deleteImageById('${delete_url}');">
    </div>
    `
    // <a href="deleteImageById(${delete_url})" class="delete-image-url" title="Delete image ${original_name}"><img src="images/delete.png" alt="Delete image"></a>
    // <button class="delete-button" onclick="deleteImageById(${image.id}, '${image.original_name}')" title="Delete">${DELETE_ICON}</button>
    // <a href="${delete_url}" class="delete-image-url" title="${url}">${DELETE_ICON}</a>
    
    return item;
}

document.addEventListener("DOMContentLoaded", getImagesFromAPI);