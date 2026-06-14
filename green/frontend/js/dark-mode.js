// ===== Modo noche — exclusivo de Green (v2) =====
(function () {
  // Crear el botón flotante
  const boton = document.createElement("button");
  boton.id = "btn-modo-noche";
  document.addEventListener("DOMContentLoaded", function () {
    document.body.appendChild(boton);
    aplicarEstadoGuardado();
  });

  // Activar/desactivar al hacer clic
  boton.addEventListener("click", function () {
    document.body.classList.toggle("dark-mode");
    const activo = document.body.classList.contains("dark-mode");
    localStorage.setItem("modoNoche", activo ? "on" : "off");
    actualizarIcono(activo);
  });

  function aplicarEstadoGuardado() {
    const activo = localStorage.getItem("modoNoche") === "on";
    if (activo) document.body.classList.add("dark-mode");
    actualizarIcono(activo);
  }

  function actualizarIcono(activo) {
    boton.textContent = activo ? "☀️" : "🌙";
  }
})();
