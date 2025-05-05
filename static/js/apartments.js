// =====================
// 📁 APARTMENTS.JS
// Отрисовка карточек квартир + иконка избранного
// =====================

import { setupSlider } from "./slider.js";
import { handleFavoriteButton } from "./favorites.js";

export async function renderApartments(apartments, favoriteIds = [], response = 0) {
    const container = document.getElementById("properties");
    container.innerHTML = "";

    const noResultsEl = document.getElementById("no-results");
    if (apartments.length === 0 || response.status === 429) {
        noResultsEl.classList.remove("hidden");
        return;
    } else {
        noResultsEl.classList.add("hidden");
    }

    for (const apartment of apartments) {
        const card = document.createElement("div");
        const isFavorited = favoriteIds.includes(apartment.id);
        card.className = "property-card";

        card.dataset.activity = apartment.Activity || "";
        card.dataset.realityType = apartment.RealityType || "";
        card.dataset.regionId = apartment.RegionID || "";
        card.dataset.districtId = apartment.DistrictId || "";
        card.dataset.pragueId = apartment.PragueLocalityId || "";

        let photos = [];
        try {
            const photoResponse = await fetch(`get_photos/${apartment.id}`);
            photos = await photoResponse.json();
        } catch (error) {
            console.error("Ошибка загрузки фотографий:", error);
        }

        if (photos.length === 0) {
            photos = ["/static/RealoScan - nophoto.png"];
        }

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

        handleFavoriteButton(card, apartment.id, isFavorited);
    }
}
