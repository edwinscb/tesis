const videoElement = document.getElementById('video');
const switchCameraButton = document.getElementById('switch-camera');

let currentStream = null;
let videoDevices = [];
let currentDeviceIndex = 0;

// Inicia la cámara seleccionada
async function startCamera(deviceId = null) {
    if (currentStream) {
        // Detener el stream actual
        currentStream.getTracks().forEach(track => track.stop());
    }

    try {
        const constraints = {
            video: deviceId ? { deviceId: { exact: deviceId } } : true,
        };

        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        videoElement.srcObject = currentStream;
    } catch (error) {
        console.error("Error al acceder a la cámara:", error);
        alert("No se puede acceder a la cámara. Por favor, permite el acceso en la configuración de tu navegador.");
    }
}

// Cambiar entre cámaras
function switchCamera() {
    if (videoDevices.length > 1) {
        currentDeviceIndex = (currentDeviceIndex + 1) % videoDevices.length;
        const nextDeviceId = videoDevices[currentDeviceIndex].deviceId;
        startCamera(nextDeviceId);
    } else {
        alert("No hay más cámaras disponibles.");
    }
}

// Obtener las cámaras disponibles
async function getVideoDevices() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    videoDevices = devices.filter(device => device.kind === 'videoinput');
}

// Inicializar
async function initialize() {
    await getVideoDevices();
    if (videoDevices.length > 0) {
        startCamera(videoDevices[currentDeviceIndex].deviceId);
    } else {
        alert("No se encontraron cámaras disponibles.");
    }
}

// Eventos
window.onload = initialize;
switchCameraButton.addEventListener('click', switchCamera);
