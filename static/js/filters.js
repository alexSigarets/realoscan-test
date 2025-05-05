// =====================
// 📁 FILTERS.JS
// Работа с фильтрами: рендер, сброс, восстановление
// =====================

import { Activita, RealityType, RegionId } from "./constants.js";
import { showPreloader, hidePreloader, updateApartmentCount} from "./utils.js";
import { renderApartments } from './apartments.js'
import { fetchApartments} from './main.js'



// Заполнение фильтров
export function renderActivityFilter(apartments, response) {
    const activitySelect = document.getElementById("aktivita");
    activitySelect.innerHTML = '<option value="0">Nezáleží</option>';

    if(response.status === 429){
        return
    }

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


export function renderRealityTypeFilter(apartments, response) {
    const realityTypeSelect = document.getElementById("druh");
    realityTypeSelect.innerHTML = '<option value="0">Nezáleží</option>';

    if(response.status === 429){
        return
    }

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


export function renderRegionTypeFilter(apartments, response) {
    const regionSelect = document.getElementById("kraj");
    regionSelect.innerHTML = '<option value="0">Nezáleží</option>';

    if(response.status === 429){
        return
    }

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



// Новая фильтрация (серверная):
export async function fetchFilteredApartments(favoriteIds) {
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
        const response = await fetch(`apartments/?${params.toString()}`);
        const data = await response.json();

        renderApartments(data, favoriteIds);
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
export function resetFilters(favoriteIds) {
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
    fetchApartments(favoriteIds);
}





// Восстановление фильтров при перезагрузке:
export function restoreFiltersFromURL() {
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