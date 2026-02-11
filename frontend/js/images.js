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

function getFileIconAPI(file_ext) {
    const icons = {'jpg': CAMERA_ICON, 'jpeg': CAMERA_ICON, 'png': CAMERA_WITH_FLASH_ICON, 'gif': VIDEO_ICON};

    return icons[file_ext] || '📦';
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

function getImagesFromAPI() {
    // fetch('http://localhost:8000/api/images')
    fetch('/api/images')
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сети'); // Проверка статуса
        return response.json(); // Парсинг JSON
    })
    .then(data => {
        showImagesListAPI(data)
        console.log(data);
        alert(data[0].total);
        // alert(data[0]['images'][0]['filename']);
        // alert(data[0]['images'][1]['filename']);
    }) // Работа с данными
    .catch(error => alert('Ошибка:' + error)); // Обработка ошибок
}

function showImagesListAPI(data_obj) {
    const images = data_obj[0].images;
    delete_url = data_obj[0].delete_url;
    download_url = data_obj[0].url;
    const list = document.getElementById("imagesList");
    const empty = document.getElementById("emptyState");
    
    //list.innerHTML = ""

    if (images.length === 0) {
        empty.style.display = "block";
        return
    }

    empty.style.display = "none";
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
    
    const shortName = cutLongName(image.original_name, 34);
    // const url = image.url + image.filename;
    const url = image.url + image.filename;
    const delete_url = image.delete_url + image.id;
    const shortUrl = cutLongName(url, 39);

    // const icon = getFileIconAPI(image.file_type);
    // <span class="image-icon">${icon}</span>

    item.innerHTML = `
    <div class="image-name">
        <span class="image-icon"><img src="images/photo.png" alt="Photo"></span>
        <span title="${image.original_name}">${shortName}</span>
    </div>
    <div class="image-url-wrapper">
        <a href="${url}" class="image-url" target="_blank" title="${image.original_name}" download="${image.original_name}">${shortName}</a>
    </div>
    <div class="image-delete">
        <a href="${delete_url}" class="delete-image-url" title="Delete image"><img src="images/delete.png" alt="Delete image"></a>
    </div>
    `
    // <button class="delete-button" onclick="deleteImageById(${image.id}, '${image.original_name}')" title="Delete">${DELETE_ICON}</button>
    // <a href="${delete_url}" class="delete-image-url" title="${url}">${DELETE_ICON}</a>
    
    return item;
}

document.addEventListener("DOMContentLoaded", getImagesFromAPI());