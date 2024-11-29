const socket = io();


const canvas = document.getElementById("canvas");

const ctx = canvas.getContext("2d");
const changeCameraButton = document.getElementById("change-camera");
const fullscreenButton = document.getElementById("fullscreenButton");
const modelButton = document.getElementById("modelButton");
const title = document.querySelector("h1");

let currentCameraId = 0;
let stream;
let isTrack = false;

async function getCameras() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.filter(device => device.kind === 'videoinput');
    } catch (err) {
        console.error("Error al obtener las cámaras:", err);
        return [];
    }
}

async function initializeCamera(cameraId) {
    try {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        const videoDevices = await getCameras();
        const constraints = { video: { deviceId: videoDevices[cameraId].deviceId } };
        stream = await navigator.mediaDevices.getUserMedia(constraints);

        captureAndSendFrames(stream);
    } catch (err) {
        console.error("Error al acceder a la cámara:", err);
    }
}

async function changeCamera() {
    const cameras = await getCameras();
    currentCameraId = (currentCameraId + 1) % cameras.length;
    initializeCamera(currentCameraId);
}

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
                errorCount = 0;
            }

            setTimeout(captureFrame, 100);
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

function convertFrameToBase64(imageBitmap) {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = imageBitmap.width;
    tempCanvas.height = imageBitmap.height;

    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(imageBitmap, 0, 0);

    return tempCanvas.toDataURL('image/jpeg');
}

function displayProcessedFrame(base64Frame) {
    const img = new Image();
    img.src = `data:image/jpeg;base64,${base64Frame}`;

    img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
}
modelButton.addEventListener("click", () => {
    if (isTrack) {
        title.textContent = "Detección";
    } else {
        title.textContent = "Seguimiento";
    }
    isTrack = !isTrack;
    socket.emit('model_toggle', { isTrack });

});
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

socket.on('video_frame', (data) => {
    if (data.frame) {
        displayProcessedFrame(data.frame);
    } else {
        console.warn("Fotograma vacío recibido del servidor");
    }
});

initializeCamera(currentCameraId);
changeCameraButton.addEventListener("click", changeCamera);
fullscreenButton.addEventListener("click", toggleFullscreen);
