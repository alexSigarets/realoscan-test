// =====================
// 📁 FAVORITES.JS
// Добавление в избранное, загрузка ID избранных квартир
// =====================

import { showToast } from './utils.js';

export function handleFavoriteButton(card, apartmentId, isFavorited = false) {
    const btn = card.querySelector(".favorite-btn");
    const img = btn.querySelector("img");
    const token = localStorage.getItem("token");

    // Установка стартового состояния
    btn.dataset.active = isFavorited.toString();
    img.src = isFavorited
        ? "/static/icons/icon-bookmark-action.png"
        : "/static/icons/icon-bookmark-defult.png";

    btn.addEventListener("click", async () => {
        if (!token) return showToast("Nejste přihlášeni", "error");

        try {
            const res = await fetch("http://192.168.1.202:8000/favorite", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(parseInt(apartmentId))
            });

            const data = await res.json();

            if (!res.ok) {
                showToast(`Chyba: ${data.detail || "Akce se nezdařila"}`, 'error');
                return;
            }

            const isNowActive = data.status === "added";

            btn.dataset.active = isNowActive.toString();
            img.src = isNowActive
                ? "/static/icons/icon-bookmark-action.png"
                : "/static/icons/icon-bookmark-defult.png";

            showToast(`${data.message}`);
        } catch (err) {
            console.error("Chyba při komunikaci se serverem:", err);
            showToast("Chyba spojení se serverem", "error");
        }
    });
}



export async function fetchFavoriteIds() {
    const token = localStorage.getItem("token");
    if (!token) return [];

    try {
        const res = await fetch("http://192.168.1.202:8000/favorite/ids", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        return res.ok ? await res.json() : [];
    } catch {
        return [];
    }
}
