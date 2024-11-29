const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:4200", // Origen de tu aplicación Angular
    methods: ["GET", "POST"],
    allowedHeaders: ["my-custom-header"],
    credentials: true
  }
});

io.on('connection', (socket) => {
  console.log('Cliente conectado');
  
  socket.on('frame', (data) => {
    console.log('Fotograma recibido', data); // Aquí puedes procesar o almacenar el fotograma recibido
    // Por ejemplo, puedes guardarlo en un archivo o procesarlo en otro formato
  });

  socket.on('disconnect', () => {
    console.log('Cliente desconectado');
  });
});

server.listen(3000, () => {
  console.log('Servidor corriendo en http://localhost:3000');
});
