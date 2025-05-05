// =====================
// 📁 MAIN.JS
// Главный вход: загрузка, фильтры, отрисовка, роли
// =====================

import {
    renderActivityFilter,
    renderRealityTypeFilter,
    renderRegionTypeFilter,
    restoreFiltersFromURL,
    fetchFilteredApartments,
    resetFilters
} from "./filters.js";
import { renderApartments } from "./apartments.js";
import { showPreloader, hidePreloader, updateApartmentCount, checkRole, showToast  } from "./utils.js";
import { DistrictId } from './constants.js'; // относительный путь
import { fetchFavoriteIds } from "./favorites.js";

let allApartments = [];

// Запрос данныз с сервера 
export async function fetchApartments(favoriteIds) {
    
    try {
        const response = await fetch("apartments/");
        const data = await response.json();
        
        renderApartments(data, favoriteIds);
        updateApartmentCount(data.length); // <--- вызываем обновление счетчика
        renderActivityFilter(data); // <---- вызыввем заполнение фильтров (Activity)
        renderRealityTypeFilter(data); // <---- вызыввем заполнение фильтров (RealityType)
        renderRegionTypeFilter(data); // <---- вызыввем заполнение фильтров (RegionType)
        allApartments = data
    } catch (error) {
        console.error("Ошибка загрузки квартир:", error);
    }
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





// Новая активация фильтра(Сервер)
document.getElementById("filter-btn").addEventListener("click", async () => {
    const favoriteIds = await fetchFavoriteIds();
    fetchFilteredApartments(favoriteIds)
});

// Активация сброса фильтров
document.getElementById("reset-btn").addEventListener("click", async () =>{
    const favoriteIds = await fetchFavoriteIds();
    resetFilters(favoriteIds)
});




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



// Запустить при загрузке страницы
document.addEventListener("DOMContentLoaded", async () => {
    

    checkRole();

    // 1. Загружаем все квартиры для построения фильтров
    const response = await fetch("apartments/");
    const data = await response.json();
    allApartments = data;

    const favoriteIds = await fetchFavoriteIds();

    if(response.status === 429){
        showToast('Byl překročen limit požadavků', 'error');
        renderApartments(data, favoriteIds, response); // Выдаем карточку с ошибкой
        return
    }
    
    // 2. Отрисовываем фильтры
    renderActivityFilter(data, response);
    renderRealityTypeFilter(data, response);
    renderRegionTypeFilter(data, response);

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
        
        await fetchFilteredApartments(favoriteIds); // получаем нужные квартиры
    } else {
        
        
        renderApartments(data, favoriteIds, response); // показываем все
        updateApartmentCount(data.length);
    }

    
});
