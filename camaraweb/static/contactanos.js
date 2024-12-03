// Inicializa EmailJS con tu User ID
emailjs.init("BN_dWP3VxEMJ8-8WB"); // Reemplaza "TU_USER_ID" con el ID que obtuviste en el panel de EmailJS

// Selecciona el formulario
const form = document.getElementById('contact-form');

// Agrega un evento al formulario para interceptar el envío
form.addEventListener('submit', function(event) {
    event.preventDefault(); // Evita el comportamiento por defecto del formulario

    const serviceID = 'smartVolley'; // Cambia con tu Service ID
    const templateID = 'SmartVolley2024v1'; // Cambia con tu Template ID

    // Envía el formulario usando EmailJS
    emailjs.sendForm(serviceID, templateID, this)
        .then(() => {
            alert('¡Mensaje enviado con éxito! Nos pondremos en contacto contigo pronto.');
            form.reset(); // Resetea el formulario
        }, (err) => {
            alert('Hubo un problema al enviar el mensaje: ' + JSON.stringify(err));
        });
});
