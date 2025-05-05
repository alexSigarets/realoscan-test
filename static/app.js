import { Activita, RealityType, RegionId, DistrictId } from './contants.js'; // относительный путь

let allApartments = [] // глобальная переменная со списокм квартир

// Запрос данныз с сервера 
async function fetchApartments() {
    showPreloader();
    try {
        const response = await fetch("http://192.168.1.202:8000/apartments/");
        const data = await response.json();
        
        renderApartments(data);
        updateApartmentCount(data.length); // <--- вызываем обновление счетчика
        renderActivityFilter(data); // <---- вызыввем заполнение фильтров (Activity)
        renderRealityTypeFilter(data); // <---- вызыввем заполнение фильтров (RealityType)
        renderRegionTypeFilter(data); // <---- вызыввем заполнение фильтров (RegionType)
        allApartments = data
    } catch (error) {
        console.error("Ошибка загрузки квартир:", error);
    }finally{
        hidePreloader();
    }
}

// Колличество обхектов в базе
function updateApartmentCount(count) {
    const countElement = document.getElementById("apartment-count");
    if (countElement) {
        countElement.textContent = `(Nalezeno: ${count} nemovitostí)`;
    }
}


// Обработка и структурирование квартир
async function renderApartments(apartments) {
    const container = document.getElementById("properties");
    container.innerHTML = ""; // Очистить перед новым рендером

    const noResultsEl = document.getElementById("no-results");
    if (apartments.length === 0) {
        noResultsEl.classList.remove("hidden");
        return;
    } else {
        noResultsEl.classList.add("hidden");
    }

    for (const apartment of apartments) {
        const card = document.createElement("div");
        card.className = "property-card";

        // Добавляем атрибуты data-* на карточку
        card.dataset.activity = apartment.Activity || "";
        card.dataset.realityType = apartment.RealityType || "";
        card.dataset.regionId = apartment.RegionID || "";
        card.dataset.districtId = apartment.DistrictId || "";
        card.dataset.pragueId = apartment.PragueLocalityId || "";
        

        // Загружаем фотографии для этой квартиры
        let photos = [];
        try {
            const photoResponse = await fetch(`http://192.168.1.202:8000/get_photos/${apartment.id}`);
            photos = await photoResponse.json();
        } catch (error) {
            console.error("Ошибка загрузки фотографий:", error);
        }

        // Если фото нет — используем заглушку
        if (photos.length === 0) {
            photos = ["/static/RealoScan - nophoto.png"];
        }

        // Генерируем HTML для слайдера
        const sliderHtml = `
            <div class="photo-slider">
                ${photos.map((photo, index) => `
                    <img src="${photo}" style="display: ${index === 0 ? 'block' : 'none'};" alt="Foto bytu">
                `).join('')}
                ${photos.length > 1 ? `
                    <button class="prev-btn">&#10094;</button>
                    <button class="next-btn">&#10095;</button>
                ` : ''}
            </div>
        `;

        card.innerHTML = `
            ${sliderHtml}
            <div class="info">
                <div>
                    <h3>${apartment.AdvandName || "Bez názvu"}</h3>
                    
                    <p><strong>Cena:</strong> ${apartment.price ? apartment.price.toLocaleString("cs-CZ") + " Kč" : "Neuvedeno"}</p>
                    <p><strong>Lokace:</strong> ${apartment.LocalityName || "Neuvedeno"}</p>
                    <br>
                    <p><strong>Popis:</strong> ${apartment.AdvertText || "Bez popisu"}</p>
                    <br>
                    <p><strong>Jméno:</strong> ${apartment.Jmeno || "Neuvedeno"} </p>
                    <p><strong>Telefon:</strong> ${apartment.Telefon || "Neuvedeno"} ${apartment.TelephoneServerCount ? "<strong>(inzeroval " + apartment.TelephoneServerCount +"x)</strong>": ""}</p>
                    <p><strong>Email:</strong> ${apartment.Email || "Neuvedeno"} ${apartment.EmailServerCount ? "<strong>(inzeroval " + apartment.EmailServerCount +"x)</strong>": ""}</p>
                </div>
                <br>
                <a href="${apartment.link}" class="detail-btn" target="_blank">Detaily</a>
            </div>

            <div class="actions">
                <button class="favorite-btn" data-id="${apartment.id}" data-active="false">
                    <img src="/static/icons/icon-bookmark-defult.png" alt="Oblíbené" class="heart-icon">
                </button>
            </div>
        `;

        container.appendChild(card);

        if (photos.length > 1) {
            setupSlider(card);
        }

        // Обработка кнопки избранного через data-active и добавление в базу
        const favoriteBtn = card.querySelector(".favorite-btn");
        const favoriteImg = favoriteBtn.querySelector("img");

        favoriteBtn.addEventListener("click", async () => {
            const isActive = favoriteBtn.dataset.active === "true";
            const apartmentId = favoriteBtn.dataset.id;
            const token = localStorage.getItem("token"); // ← поправили
        
            if (!token) {
                alert("Вы не авторизованы");
                return;
            }
        
            try {
                const response = await fetch("http://192.168.1.202:8000/favorite", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(parseInt(apartmentId)) // если без Pydantic
                });
        
                if (!response.ok) {
                    const data = await response.json();
                    alert(`Ошибка: ${data.detail || "Не удалось добавить в избранное"}`);
                    return;
                }
        
                favoriteImg.src = isActive
                    ? "/static/icons/icon-bookmark-defult.png"
                    : "/static/icons/icon-bookmark-action.png";
                favoriteBtn.dataset.active = (!isActive).toString();
            } catch (error) {
                console.error("Ошибка при добавлении в избранное:", error);
            }
        });

        
    }
}


// Логика переключения фотографий
function setupSlider(card) {
    const photos = card.querySelectorAll(".photo-slider img");
    let currentIndex = 0;

    const showPhoto = (index) => {
        photos.forEach((img, i) => {
            img.style.display = i === index ? "block" : "none";
        });
    };

    const prevBtn = card.querySelector(".prev-btn");
    const nextBtn = card.querySelector(".next-btn");

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener("click", () => {
            currentIndex = (currentIndex - 1 + photos.length) % photos.length;
            showPhoto(currentIndex);
        });

        nextBtn.addEventListener("click", () => {
            currentIndex = (currentIndex + 1) % photos.length;
            showPhoto(currentIndex);
        });
    }
}




// Заполнение фильтров
function renderActivityFilter(apartments) {
    const activitySelect = document.getElementById("aktivita");
    activitySelect.innerHTML = '<option value="0">Nezáleží</option>';

    const uniqueActivities = new Set();

    apartments.forEach(apartment => {
        if (apartment.Activity !== null && apartment.Activity !== undefined) {
            uniqueActivities.add(apartment.Activity);
        }
    });

    // Преобразуем Set в массив и сортируем по значению из словаря Activita
    Array.from(uniqueActivities)
        .sort((a, b) => {
            const labelA = Activita[a] || `Typ ${a}`;
            const labelB = Activita[b] || `Typ ${b}`;
            return labelA.localeCompare(labelB, "cs"); // сортировка с учётом чешского алфавита
        })
        .forEach(activityValue => {
            const option = document.createElement("option");
            option.value = activityValue;
            option.textContent = Activita[activityValue] || `Typ ${activityValue}`;
            activitySelect.appendChild(option);
        });
}


function renderRealityTypeFilter(apartments) {
    const realityTypeSelect = document.getElementById("druh");
    realityTypeSelect.innerHTML = '<option value="0">Nezáleží</option>';

    const uniqueRealityTypes = new Set();

    apartments.forEach(apartment => {
        if (apartment.RealityType !== null && apartment.RealityType !== undefined) {
            uniqueRealityTypes.add(apartment.RealityType);
        }
    });

    Array.from(uniqueRealityTypes)
        .sort((a, b) => {
            const labelA = RealityType[a] || `Typ ${a}`;
            const labelB = RealityType[b] || `Typ ${b}`;
            return labelA.localeCompare(labelB, "cs");
        })
        .forEach(typeValue => {
            const option = document.createElement("option");
            option.value = typeValue;
            option.textContent = RealityType[typeValue] || `Typ ${typeValue}`;
            realityTypeSelect.appendChild(option);
        });
}


function renderRegionTypeFilter(apartments) {
    const regionSelect = document.getElementById("kraj");
    regionSelect.innerHTML = '<option value="0">Nezáleží</option>';

    const uniqueRegions = new Set();

    apartments.forEach(apartment => {
        if (apartment.RegionID !== null && apartment.RegionID !== undefined) {
            uniqueRegions.add(apartment.RegionID);
        }
    });

    Array.from(uniqueRegions)
        .sort((a, b) => {
            const labelA = RegionId[a] || `Region ${a}`;
            const labelB = RegionId[b] || `Region ${b}`;
            return labelA.localeCompare(labelB, "cs");
        })
        .forEach(regionValue => {
            const option = document.createElement("option");
            option.value = regionValue;
            option.textContent = RegionId[regionValue] || `Region ${regionValue}`;
            regionSelect.appendChild(option);
        });
}




// Слушаем Select для выбора края и заполнения okres
document.getElementById("kraj").addEventListener("change", () => {
    const krajValue = document.getElementById("kraj").value;
    const prahaCheckboxes = document.getElementById("praha-checkboxes");
    const checkboxes = prahaCheckboxes.querySelectorAll("input[type='checkbox']");
    const okresSelect = document.getElementById("okres");

    // Управление видимостью Praha-checkboxes
    if (krajValue === "1") {
        prahaCheckboxes.style.opacity = "1";
        prahaCheckboxes.style.pointerEvents = "auto";
    } else {
        prahaCheckboxes.style.opacity = "0";
        prahaCheckboxes.style.pointerEvents = "none";
        checkboxes.forEach(cb => cb.checked = false);
    }

    // Очистить okres
    okresSelect.innerHTML = '<option value="0">Nezáleží</option>';

    // Заполнить okres, если выбран Středočeský kraj
    if (krajValue === "8") {
        const okresSet = new Set();
        allApartments.forEach(apartment => {
            if (apartment.RegionID == "8" && apartment.DistrictId && DistrictId[apartment.DistrictId]) {
                okresSet.add(apartment.DistrictId);
            }
        });

        Array.from(okresSet).sort((a, b) => {
            return DistrictId[a].localeCompare(DistrictId[b]);
        }).forEach(districtId => {
            const option = document.createElement("option");
            option.value = districtId;
            option.textContent = DistrictId[districtId];
            okresSelect.appendChild(option);
        });
    }
});




// Применение фильтров: (не вызывается)




// Новая фильтрация (серверная):
async function fetchFilteredApartments() {
    const params = new URLSearchParams();

    // Чтение фильтров
    const activity = document.getElementById("aktivita").value;
    const realityType = document.getElementById("druh").value;
    const region = document.getElementById("kraj").value;
    const district = document.getElementById("okres").value;

    const pragueCheckboxes = document.querySelectorAll("#praha-checkboxes input[type='checkbox']:checked");
    const praguePart = pragueCheckboxes.length > 0 ? pragueCheckboxes[0].dataset.pragueid : null;

    // Добавляем параметры только если они реально выбраны
    if (activity && activity !== "0") {
        params.set("activity", activity);
    }

    if (realityType && realityType !== "0") {
        params.set("reality_type", realityType);
    }

    if (region && region !== "0") {
        params.set("region_id", region);
    }

    if (district && district !== "0" && district !== "" && district !== null) {
        params.set("district_id", district);
    }

    if (region === "1" && pragueCheckboxes.length > 0) {
        Array.from(pragueCheckboxes)
            .map(cb => cb.dataset.pragueid)
            .filter(Boolean)
            .forEach(id => {
                params.append("prague_id", id); // ⬅️ append вместо set + join
            });
    }

    try {
        showPreloader();
        const response = await fetch(`http://192.168.1.202:8000/apartments/?${params.toString()}`);
        const data = await response.json();

        renderApartments(data);
        updateApartmentCount(data.length);

        // обновить URL в браузере
        const newUrl = new URL(window.location.href);
        newUrl.search = params.toString();
        window.history.replaceState({}, '', newUrl);
    } catch (error) {
        console.error("Ошибка загрузки фильтрованных квартир:", error);
    }finally{
        hidePreloader();
    }
}


// Сброс фильтров:
function resetFilters() {
    // Сброс всех select'ов
    ["stari", "aktivita", "druh", "kraj", "okres"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "0";
    });

    // Сброс всех чекбоксов "Část Prahy"
    document.querySelectorAll("#praha-checkboxes input[type='checkbox']").forEach(cb => {
        cb.checked = false;
    });

    // Скрыть блок с чекбоксами Праги
    const prahaBox = document.getElementById("praha-checkboxes");
    prahaBox.style.opacity = "0";
    prahaBox.style.pointerEvents = "none";

    // Очистить URL от параметров фильтра
    const newUrl = new URL(window.location.href);
    newUrl.search = ""; // сброс query string
    window.history.replaceState({}, "", newUrl);

    // Заново загрузить все квартиры
    fetchApartments();
}






// Восстановление фильтров при перезагрузке:
function restoreFiltersFromURL() {
    const params = new URLSearchParams(window.location.search);

    if (params.has("activity")) {
        document.getElementById("aktivita").value = params.get("activity");
    }

    if (params.has("reality_type")) {
        document.getElementById("druh").value = params.get("reality_type");
    }

    if (params.has("region_id")) {
        const regionEl = document.getElementById("kraj");
        const regionValue = params.get("region_id");
        regionEl.value = regionValue;

        regionEl.dispatchEvent(new Event("change"));

        // Если Прага — восстанавливаем prague_id чекбоксы
        if (regionValue === "1") {
            const selectedIds = params.getAll("prague_id");
            const checkboxes = document.querySelectorAll("#praha-checkboxes input[type='checkbox']");
            checkboxes.forEach(cb => {
                if (selectedIds.includes(cb.dataset.pragueid)) {
                    cb.checked = true;
                }
            });
        }
    }

    // Всегда применяем фильтры один раз (после восстановления значений)
    // fetchFilteredApartments();
}




// Новая активация фильтра(Сервер)
document.getElementById("filter-btn").addEventListener("click", fetchFilteredApartments);

// Активация сброса фильтров
document.getElementById("reset-btn").addEventListener("click", resetFilters);


// Переход на страницу регистрации (для админа):
document.getElementById("adminRegisterBtn").addEventListener("click", () => {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Chybí token! Přihlašte se nejprve jako administrátor.");
        return;
    }

    // Обязательно продублируем запись в cookie
    document.cookie = `token=${token}; path=/`;

    // Перейдём на страницу
    window.location.href = "/admin/register";
});

// Проверка роли пользователя при загрузки страницы 
function checkRole(){
    const role = localStorage.getItem("role");
    const adminBtn = document.getElementById("adminRegisterBtn");

    if (role !== "admin" && adminBtn) {
        adminBtn.style.display = "none";
    }
}


// Прелоадер
function showPreloader() {
    document.getElementById("preloader").classList.remove("hidden");
}

function hidePreloader() {
    document.getElementById("preloader").classList.add("hidden");
}






// Запустить при загрузке страницы
document.addEventListener("DOMContentLoaded", async () => {
    

    checkRole();

    // 1. Загружаем все квартиры для построения фильтров
    const response = await fetch("http://192.168.1.202:8000/apartments/");
    const data = await response.json();
    allApartments = data;

    // 2. Отрисовываем фильтры
    renderActivityFilter(data);
    renderRealityTypeFilter(data);
    renderRegionTypeFilter(data);

    // 3. Восстанавливаем значения select и чекбоксов
    restoreFiltersFromURL();

    // 4. Применяем фильтр, если фильтры есть
    const hasFilters =
        window.location.search.includes("region_id") ||
        window.location.search.includes("activity") ||
        window.location.search.includes("reality_type") ||
        window.location.search.includes("district_id") ||
        window.location.search.includes("prague_id");


    if (hasFilters) {
        await fetchFilteredApartments(); // получаем нужные квартиры
    } else {
        renderApartments(data); // показываем все
        updateApartmentCount(data.length);
    }

    
});