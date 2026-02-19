DELETE_ICON = "&#128465;";
CAMERA_ICON = "&#128247;";
CAMERA_WITH_FLASH_ICON = "&#128248;";
VIDEO_ICON = "&#127909;";

async function deleteImageById(deleteUrl) {
    try {
        const response = await fetch(deleteUrl);
        const data = await response.json();

        console.log(data);

        if (response.ok) {
            showStatus(data.message, 'success');
            displayImagesList();
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

// async function getImagesFromAPI(page) {
//     // fetch('http://localhost:8000/api/images')
//     // TODO replace '/api/images' with environment variable
//     let response;
//     if (page && page > 0) {
//         response = await fetch(`/api/images/${page}`);
//     } else {
//         response = await fetch('/api/images');
//     }
//     const data = await response.json();

//     console.log(data);

//     if (response.ok) {
//         return data;
//     } else {
//         message = data.error;
//         throw new Error(message);
//     }
// }

function showEmptyBlock(show) {
    const empty = document.getElementById("emptyState");
    if (show) {
        empty.style.display = "block";
    } else {
        empty.style.display = "none";
    }
}


function hideStatus() {
    const status = document.getElementById("statusBlock");
    if (!status) {
        return;
    } else {
        status.style.display = 'none';
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

    toggleImagesPaging(data_obj);
}

function toggleImagesPaging(data) {
    const page = data.page;
    const perPage = data.images_per_page;
    const firstImg = page * perPage + 1;
    let lastImg = firstImg + perPage - 1;
    const total = data.total;
    if (lastImg > total) {
        lastImg = total;
    }
    const pagingElm = document.getElementById("imagesPaging");
    if (perPage >= total) {
        pagingElm.style.display = "none";
        return;
    }
    let prev = '';
    if (page > 0) {
        prev = `<span class="images-paging-prev" title="Previous page" id="imagesPagingPrev" onclick="showPage(${page-1});"><<</span>`;
    }
    const pagingImages = `images ${firstImg}..${lastImg} of ${total}`;
    let next = '';
    if (total > lastImg) {
        next = `<span class="images-paging-next" title="Next page" id="imagesPagingNext" onclick="showPage(${page+1});">>></span>`;
    }
    pagingElm.innerHTML = prev + pagingImages + next;
    pagingElm.style.display = "block";
}

// Создание элемента изображения
function createImageItemAPI(image) {
    const item = document.createElement("div");
    item.className = 'image-item';
    item.dataset.id = image.id;
    
    const originalName = image.original_name;
    const shortName = cutLongName(originalName, 29);
    // const url = image.url + image.filename;
    const url = image.url + image.filename;
    const deleteUrl = image.delete_url + image.id;
    const shortUrl = cutLongName(url, 39);

    // const icon = getFileIconAPI(image.file_type);
    // <span class="image-icon">${icon}</span>

    item.innerHTML = `
    <div class="image-name">
        <span class="image-icon"><img src="images/photo.png" alt="Photo"></span>
        <span title="${originalName}">${shortName}</span>
    </div>
    <div class="image-url-wrapper">
        <a href="${url}" class="image-url" target="_blank" title="${originalName}" download="${originalName}">${shortName}</a>
    </div>
    <div class="image-size">
        <span title="${image.size}">${image.size.toLocaleString('ru-RU', {maximumFractionDigits: 0})}</span>
    </div>
    <div class="image-delete">
        <img src="images/delete.png" class="delete-button" alt="Delete image" title="Delete image ${originalName}" onclick="deleteImageById('${deleteUrl}');">
    </div>
    `
    // <a href="deleteImageById(${delete_url})" class="delete-image-url" title="Delete image ${original_name}"><img src="images/delete.png" alt="Delete image"></a>
    // <button class="delete-button" onclick="deleteImageById(${image.id}, '${image.original_name}')" title="Delete">${DELETE_ICON}</button>
    // <a href="${delete_url}" class="delete-image-url" title="${url}">${DELETE_ICON}</a>
    
    return item;
}

// Paging functions
function showPage(page) {
    displayImagesList(page);
}

async function displayImagesList(page) {
    try {
        const data = await getImagesFromAPI(page);
        showImagesListAPI(data);
        hideStatus();
    } catch (error) {
        console.log(error);
        showStatus(error.message, 'error');
    } // Обработка ошибок
}

document.addEventListener("DOMContentLoaded", displayImagesList);