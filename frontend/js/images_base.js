async function getImagesFromAPI(page) {
    // fetch('http://localhost:8000/api/images')
    // TODO replace '/api/images' with environment variable
    let response;
    if (page && page > 0) {
        response = await fetch(`/api/images/${page}`);
    } else {
        response = await fetch('/api/images');
    }
    const data = await response.json();

    console.log(data);

    if (response.ok) {
        return data;
    } else {
        message = data.error;
        throw new Error(message);
    }
}

async function getRandomImages() {
    // fetch('http://localhost:8000/api/random')
    // TODO replace '/api/random' with environment variable
    response = await fetch(`/api/random`);
    const data = await response.json();

    console.log(data);

    if (response.ok) {
        return data;
    } else {
        message = data.error;
        throw new Error(message);
    }
}

function cutLongName(name, maxLen) {
    if (!name) return "";
    if (maxLen <= 3) return name.substring(0, maxLen);  // Если меньше 3 просто обрезаем
    if (name.length > maxLen) {
        return name.substring(0, maxLen - 3) + "...";
    } else {
        return name;
    }
}