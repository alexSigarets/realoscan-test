// =====================
// 📁 UTILS.JS
// Утилиты: прелоадер, проверка роли, обновление счётчика
// =====================



// Прелоадер
export function showPreloader() {
    document.getElementById("preloader").classList.remove("hidden");
}

export function hidePreloader() {
    document.getElementById("preloader").classList.add("hidden");
}

// Проверка роли пользователя при загрузки страницы 
export function checkRole(){
    const role = localStorage.getItem("role");
    const adminBtn = document.getElementById("adminRegisterBtn");

    if (role !== "admin" && adminBtn) {
        adminBtn.style.display = "none";
    }
}

// Колличество обхектов в базе
export function updateApartmentCount(count) {
    const countElement = document.getElementById("apartment-count");
    if (countElement) {
        countElement.textContent = `Nalezeno: ${count} nemovitostí`;
    }
}



// Показываем всплывющее окно: 
export function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    const container = document.getElementById("toast-container");
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000);
}