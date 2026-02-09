const STORAGE_KEY = "uploadedImages"

function cutLongName(name, maxLen) {
    if (!name) return "";
    if (maxLen <= 3) return name.substring(0, maxLen);  // Если меньше 3 просто обрезаем
    if (name.length > maxLen) {
        return name.substring(0, maxLen - 3) + "...";
    } else {
        return name;
    }
}
 
function getAllImages() {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    })
}

//const success = saveImage(file.name, base64, file.size);
function saveImage(filename, url, base64, fileSize) {
    try {
        const images = getAllImages();
        const newImage = {
            id: Date.now(),
            name: filename,
            url: url,
            data: base64,
            size: fileSize,
            date: new Date().toISOString()
        }

        images.push(newImage);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(images));
        return true;
    }
    catch (error) {
        if (error.name === "QuotaExceededError") {
            alert("Not enough storage space, delete images first.");
        } else {
            alert(error);
        }
        return false;
    }
}

function deleteImage(imageId) {
    const images = getAllImages();
    const filtered = images.filter(img => img.id !== imageId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
}