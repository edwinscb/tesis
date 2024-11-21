// Establece conexión al servidor mediante WebSocket
const socket = io();

// Referencias a elementos del DOM
const videoElement = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

// Configura la cámara y comienza la transmisión
async function initializeCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElement.srcObject = stream;
        captureAndSendFrames(stream); // Inicia la captura y envío de fotogramas
    } catch (err) {
        console.error("Error al acceder a la cámara:", err);
    }
}

// Captura y envía fotogramas al servidor
function captureAndSendFrames(stream) {
    const imageCapture = new ImageCapture(stream.getVideoTracks()[0]);
    
    const captureFrame = async () => {
        try {
            const imageBitmap = await imageCapture.grabFrame();
            if (!imageBitmap) throw new Error("Fotograma vacío");

            // Convertir fotograma a Base64
            const base64Frame = convertFrameToBase64(imageBitmap);
            if (base64Frame) socket.emit('start_video', { frame: base64Frame });

            setTimeout(captureFrame, 100); // Repite cada 100 ms
        } catch (err) {
            console.error("Error al capturar fotograma:", err);
        }
    };

    captureFrame(); // Llama por primera vez
}

// Convierte un fotograma (ImageBitmap) en una cadena Base64
function convertFrameToBase64(imageBitmap) {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = imageBitmap.width;
    tempCanvas.height = imageBitmap.height;

    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(imageBitmap, 0, 0);

    return tempCanvas.toDataURL('image/jpeg');
}

// Dibuja un fotograma procesado en el canvas
function displayProcessedFrame(base64Frame) {
    const img = new Image();
    img.src = `data:image/jpeg;base64,${base64Frame}`;

    img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Limpia el canvas
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height); // Dibuja la nueva imagen
    };
}

// Escucha los fotogramas procesados desde el servidor
socket.on('video_frame', (data) => {
    if (data.frame) {
        displayProcessedFrame(data.frame);
    } else {
        console.warn("Fotograma vacío recibido del servidor");
    }
});

// Inicializa la cámara al cargar el script
initializeCamera();
