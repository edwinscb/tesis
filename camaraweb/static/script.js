// Conexión al servidor de WebSocket
const socket = io();

// Obtiene la referencia a los elementos del DOM
const videoElement = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const fpsDisplay = document.getElementById("fps");

// Configura la cámara
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        videoElement.srcObject = stream;
        // Enviar el video al servidor
        sendVideoFrames(stream);
    })
    .catch(err => {
        console.error("Error al acceder a la cámara: ", err);
    });

// Enviar fotogramas al servidor
function sendVideoFrames(stream) {
    const track = stream.getVideoTracks()[0];
    const imageCapture = new ImageCapture(track);

    // Función para capturar y enviar los fotogramas al servidor
    function captureFrame() {
        imageCapture.grabFrame()
            .then(imageBitmap => {
                if (!imageBitmap) {
                    console.error("Error: Fotograma vacío");
                    return;
                }
                
                // Convierte la imagen en un canvas
                ctx.drawImage(imageBitmap, 0, 0, canvas.width, canvas.height);

                // Convierte el canvas a base64
                const base64Frame = canvas.toDataURL('image/jpeg');

                // Envia el fotograma al servidor
                socket.emit('start_video', { frame: base64Frame });

                // Llama nuevamente a la función para enviar el siguiente fotograma
                requestAnimationFrame(captureFrame);
            })
            .catch(err => {
                console.error("Error al capturar el fotograma: ", err);
            });
    }

    captureFrame();
}

// Recibir el fotograma procesado del servidor
socket.on('video_frame', data => {
    console.log("Recibiendo fotograma procesado (escala de grises)");
    
    // Decodifica el fotograma y lo dibuja en el canvas
    const img = new Image();
    img.src = 'data:image/jpeg;base64,' + data.frame;
    img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
});



// Mostrar el FPS (opcional)
let lastTime = 0;
let frameCount = 0;

function updateFPS() {
    const currentTime = performance.now();
    const deltaTime = (currentTime - lastTime) / 1000;
    lastTime = currentTime;

    if (deltaTime > 0) {
        const fps = (1 / deltaTime).toFixed(2);
        fpsDisplay.textContent = `FPS: ${fps}`;
    }

    requestAnimationFrame(updateFPS);
}

updateFPS();
