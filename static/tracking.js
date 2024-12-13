// Asegurarse de que el DOM está cargado antes de trabajar con los elementos
document.addEventListener('DOMContentLoaded', () => {
    // Seleccionar el input de archivo y el botón de envío
    const videoInput = document.getElementById('videoFile');
    const submitButton = document.getElementById('submitButton');

    // Verificar que los elementos existen en el DOM
    if (videoInput && submitButton) {
        // Escuchar el evento 'change' en el input de archivo
        videoInput.addEventListener('change', () => {
            // Habilitar o deshabilitar el botón de envío según si hay un archivo seleccionado
            if (videoInput.files.length > 0) {
                submitButton.disabled = false;
            } else {
                submitButton.disabled = true;
            }
        });
    } else {
        // En caso de que los elementos no se encuentren
        console.error("No se encontraron los elementos HTML con los IDs 'videoFile' o 'submitButton'.");
    }
});
