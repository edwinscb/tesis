const socket = io();

// Elementos del DOM
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const changeCameraButton = document.getElementById("change-camera");
const cameraList = document.getElementById("camera-list");
const fullscreenButton = document.getElementById("fullscreenButton");
const modelButton = document.getElementById("modelButton");
const title = document.querySelector("h1");

// Variables globales
let currentCameraId = 0;
let stream;
let isTrack = false;

// Obtiene la lista de cámaras disponibles
async function getCameras() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.filter(device => device.kind === 'videoinput'); // Filtra solo las cámaras
    } catch (err) {
        console.error("Error al obtener las cámaras:", err);
        return [];
    }
}

// Inicializa la cámara seleccionada
async function initializeCamera(cameraId) {
    try {
        // Detiene el flujo anterior si existe
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        const videoDevices = await getCameras();
        const constraints = { video: { deviceId: videoDevices[cameraId].deviceId } };
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        captureAndSendFrames(stream); // Captura y envía los fotogramas
    } catch (err) {
        console.error("Error al acceder a la cámara:", err);
    }
}

// Actualiza la lista de cámaras disponibles en el menú desplegable
async function updateCameraList() {
    const cameras = await getCameras();
    cameraList.innerHTML = ''; // Limpiar lista actual

    cameras.forEach((camera, index) => {
        const cameraItem = document.createElement("li");
        const cameraLink = document.createElement("a");
        cameraLink.classList.add("dropdown-item");
        cameraLink.href = "#";
        cameraLink.textContent = camera.label;

        // Si la cámara está activa, se marca con fondo verde y se desactiva la selección
        if (index === currentCameraId) {
            cameraLink.classList.add("active-camera");
            cameraLink.style.backgroundColor = "#28a745"; // Fondo verde
            cameraLink.style.pointerEvents = "none"; // Deshabilitar la selección de la cámara activa
        } else {
            cameraLink.addEventListener("click", () => {
                currentCameraId = index;
                initializeCamera(currentCameraId); // Cambiar a la cámara seleccionada
                updateCameraList(); // Actualizar lista
            });
        }

        cameraItem.appendChild(cameraLink);
        cameraList.appendChild(cameraItem);
    });
}

// Muestra la lista de cámaras disponibles en el menú desplegable
async function showAvailableCameras() {
    const cameras = await getCameras();
    cameraList.innerHTML = "";  // Limpiar la lista de cámaras disponibles

    cameras.forEach((camera, index) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.classList.add("dropdown-item");
        a.href = "#";
        a.textContent = camera.label;

        // Si la cámara está activa, se marca con fondo verde y se deshabilita la opción
        if (index === currentCameraId) {
            a.classList.add("active-camera");
            a.style.backgroundColor = "#28a745";  // Fondo verde
            a.style.color = "white";  // Texto en blanco
            a.style.pointerEvents = "none";  // Deshabilitar la selección
        }

        // Al hacer clic en una cámara, se cambia a esa cámara
        a.addEventListener("click", () => {
            currentCameraId = index;
            initializeCamera(currentCameraId);
            const dropdown = new bootstrap.Dropdown(changeCameraButton);
            dropdown.hide(); // Cerrar el menú desplegable al seleccionar una cámara
        });

        li.appendChild(a);
        cameraList.appendChild(li);
    });
}

// Cambia la cámara activa y muestra la lista de cámaras disponibles
async function changeCamera() {
    showAvailableCameras();
}

// Captura los fotogramas de la cámara y los envía al servidor
function captureAndSendFrames(stream) {
    const imageCapture = new ImageCapture(stream.getVideoTracks()[0]);
    let errorCount = 0;
    const maxErrors = 5;
    const baseRetryDelay = 500;

    const captureFrame = async () => {
        try {
            const imageBitmap = await imageCapture.grabFrame();
            const base64Frame = convertFrameToBase64(imageBitmap);

            if (base64Frame) {
                socket.emit('start_video', { frame: base64Frame }); // Envía el fotograma al servidor
                errorCount = 0; // Resetea el contador de errores
            }

            setTimeout(captureFrame, 100); // Captura el siguiente fotograma después de 100ms
        } catch (err) {
            console.error("Error al capturar fotograma:", err);
            errorCount++;

            if (errorCount > maxErrors) {
                console.warn("Límite de intentos fallidos alcanzado. Deteniendo captura.");
                return;
            }

            const retryDelay = baseRetryDelay * errorCount;
            console.log(`Reintentando en ${retryDelay} ms...`);
            setTimeout(captureFrame, retryDelay); // Reintenta capturar después de un retraso
        }
    };

    captureFrame(); // Comienza la captura de fotogramas
}

// Convierte un fotograma en formato base64 para enviarlo al servidor
function convertFrameToBase64(imageBitmap) {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = imageBitmap.width;
    tempCanvas.height = imageBitmap.height;

    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.scale(-1, 1); // Voltea el fotograma horizontalmente
    tempCtx.drawImage(imageBitmap, -imageBitmap.width, 0);

    return tempCanvas.toDataURL('image/jpeg'); // Convierte el fotograma a base64
}

// Muestra un fotograma procesado en el canvas
function displayProcessedFrame(base64Frame) {
    const img = new Image();
    img.src = `data:image/jpeg;base64,${base64Frame}`;

    img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Limpia el canvas
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height); // Dibuja el fotograma procesado
        ctx.restore();
    };
}

// Cambia el estado entre detección y seguimiento
modelButton.addEventListener("click", () => {
    isTrack = !isTrack;
    title.textContent = isTrack ? "Seguimiento" : "Detección"; // Actualiza el título
    socket.emit('model_toggle', { isTrack }); // Notifica al servidor sobre el cambio de modelo
});

// Activa el modo pantalla completa en el canvas
function toggleFullscreen() {
    if (canvas.requestFullscreen) {
        canvas.requestFullscreen();
    } else if (canvas.mozRequestFullScreen) { 
        canvas.mozRequestFullScreen();
    } else if (canvas.webkitRequestFullscreen) { 
        canvas.webkitRequestFullscreen();
    } else if (canvas.msRequestFullscreen) { 
        canvas.msRequestFullscreen();
    }
}

// Recibe fotogramas procesados desde el servidor y los muestra en el canvas
socket.on('video_frame', (data) => {
    if (data.frame) {
        displayProcessedFrame(data.frame); // Muestra el fotograma recibido
    } else {
        console.warn("Fotograma vacío recibido del servidor");
    }
});

// Inicializa la cámara y la lista de cámaras disponibles
initializeCamera(currentCameraId);
updateCameraList();

// Asocia los eventos de los botones
changeCameraButton.addEventListener("click", changeCamera);
fullscreenButton.addEventListener("click", toggleFullscreen);
