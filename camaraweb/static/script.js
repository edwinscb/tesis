// Conexión al servidor usando Socket.IO
const socket = io();

// Elementos del DOM
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const changeCameraButton = document.getElementById("change-camera");
const fullscreenButton = document.getElementById("fullscreenButton");
const modelButton = document.getElementById("modelButton");
const title = document.querySelector("h1");

// Variables globales
let currentCameraId = 0; // Índice de la cámara activa
let stream;             // Flujo de video actual
let isTrack = false;    // Estado del modelo (Detección o Seguimiento)

// Obtiene todas las cámaras disponibles
async function getCameras() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.filter(device => device.kind === 'videoinput');
    } catch (err) {
        console.error("Error al obtener las cámaras:", err);
        return [];
    }
}

// Inicializa la cámara seleccionada
async function initializeCamera(cameraId) {
    try {
        // Detener cualquier flujo de video previo
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        // Obtener dispositivos de video y configurar el flujo
        const videoDevices = await getCameras();
        const constraints = { video: { deviceId: videoDevices[cameraId].deviceId } };
        stream = await navigator.mediaDevices.getUserMedia(constraints);

        // Capturar y enviar fotogramas al servidor
        captureAndSendFrames(stream);
    } catch (err) {
        console.error("Error al acceder a la cámara:", err);
    }
}

// Cambia entre cámaras disponibles
async function changeCamera() {
    const cameras = await getCameras();
    currentCameraId = (currentCameraId + 1) % cameras.length; // Selección cíclica
    initializeCamera(currentCameraId);
}

// Captura y envía fotogramas al servidor
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
                socket.emit('start_video', { frame: base64Frame });
                errorCount = 0; // Reiniciar contador de errores tras éxito
            }

            setTimeout(captureFrame, 70);
        } catch (err) {
            console.error("Error al capturar fotograma:", err);
            errorCount++;

            if (errorCount > maxErrors) {
                console.warn("Límite de intentos fallidos alcanzado. Deteniendo captura.");
                return;
            }

            const retryDelay = baseRetryDelay * errorCount;
            console.log(`Reintentando en ${retryDelay} ms...`);
            setTimeout(captureFrame, retryDelay);
        }
    };

    captureFrame();
}

// Convierte un fotograma a base64
function convertFrameToBase64(imageBitmap) {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = imageBitmap.width;
    tempCanvas.height = imageBitmap.height;

    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(imageBitmap, 0, 0);

    return tempCanvas.toDataURL('image/jpeg');
}

// Muestra un fotograma procesado en el canvas
function displayProcessedFrame(base64Frame) {
    const img = new Image();
    img.src = `data:image/jpeg;base64,${base64Frame}`;

    img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Aplicar el efecto espejo
        ctx.save(); // Guardar el estado actual del contexto
        ctx.scale(-1, 1); // Escalar en el eje X
        ctx.translate(-canvas.width, 0); // Mover la imagen al lado visible
        
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        ctx.restore(); // Restaurar el estado del contexto
    };
}

// Alterna entre los modelos de Detección y Seguimiento
modelButton.addEventListener("click", () => {
    isTrack = !isTrack; // Cambiar estado
    title.textContent = isTrack ? "Seguimiento" : "Detección";
    socket.emit('model_toggle', { isTrack });
});

// Activa el modo pantalla completa
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

// Escucha el evento 'video_frame' del servidor para mostrar los fotogramas procesados
socket.on('video_frame', (data) => {
    if (data.frame) {
        displayProcessedFrame(data.frame);
    } else {
        console.warn("Fotograma vacío recibido del servidor");
    }
});

// Inicializa la cámara al cargar la página
initializeCamera(currentCameraId);

// Añade eventos a los botones
changeCameraButton.addEventListener("click", changeCamera);
fullscreenButton.addEventListener("click", toggleFullscreen);
