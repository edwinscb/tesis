let currentStream;
let videoElement = document.getElementById('video');
let currentDeviceId = null; // Mantener el ID de la cámara actual

// Función para obtener las cámaras disponibles
function getDevices() {
    navigator.mediaDevices.enumerateDevices()
        .then(devices => {
            let videoDevices = devices.filter(device => device.kind === 'videoinput');
            if (videoDevices.length > 0) {
                currentDeviceId = videoDevices[0].deviceId; // Iniciar con la primera cámara disponible
                startVideo(currentDeviceId);
            } else {
                alert("No cameras found");
            }
        })
        .catch(err => {
            console.error("Error getting devices: ", err);
        });
}

// Función para iniciar el video con el dispositivo seleccionado
function startVideo(deviceId) {
    // Detener el stream actual si existe
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
    }

    // Acceder a la cámara seleccionada
    navigator.mediaDevices.getUserMedia({
        video: { deviceId: { exact: deviceId } }
    })
    .then(stream => {
        currentStream = stream;
        videoElement.srcObject = stream;
    })
    .catch(error => {
        console.error("Error accessing camera: ", error);
    });
}

// Función para cambiar de cámara
function switchCamera() {
    navigator.mediaDevices.enumerateDevices()
        .then(devices => {
            let videoDevices = devices.filter(device => device.kind === 'videoinput');
            let currentIndex = videoDevices.findIndex(device => device.deviceId === currentDeviceId);
            let nextIndex = (currentIndex + 1) % videoDevices.length; // Cambiar al siguiente dispositivo
            currentDeviceId = videoDevices[nextIndex].deviceId;
            startVideo(currentDeviceId); // Iniciar el video con la nueva cámara
        })
        .catch(err => {
            console.error("Error switching camera: ", err);
        });
}

// Iniciar la primera cámara disponible al cargar la página
window.onload = getDevices;
