import { renderApartments } from "./apartments.js";
import { fetchFavoriteIds } from "./favorites.js";
import { updateApartmentCount, showToast} from "./utils.js";



// Запрос данныз с сервера (избранное)
export async function fetchApartmentsFavorite() {
    
    try {
        const response = await fetch("/favorite/apartments");
        const data = await response.json();
        const favoriteIds = await fetchFavoriteIds();

        if(response.status === 429){
            showToast('Byl překročen limit požadavků', 'error');
            renderApartments(data, favoriteIds, response); // Выдаем карточку с ошибкой
            return
        }

        
        
        renderApartments(data, favoriteIds);
        updateApartmentCount(data.length); // <--- вызываем обновление счетчика
        
    } catch (error) {
        console.error("Ошибка загрузки квартир:", error);
    }
}


// Запуск при загрузке страницы
document.addEventListener("DOMContentLoaded", async () => {
    
    fetchApartmentsFavorite();
    
});