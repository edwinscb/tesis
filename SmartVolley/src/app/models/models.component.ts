import { Component, OnInit, AfterViewInit } from '@angular/core';

@Component({
  selector: 'app-models',
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.scss']
})
export class ModelsComponent implements OnInit, AfterViewInit {
  videoElement!: HTMLVideoElement;

  constructor() {}

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    // Comprobar si estamos en el navegador antes de ejecutar el código relacionado con el DOM
    if (typeof document !== 'undefined') {
      this.startCamera();
    }
  }

  startCamera(): void {
    // Seleccionamos el video usando el template reference variable #videoElement
    this.videoElement = <HTMLVideoElement>document.querySelector('video');

    this.videoElement.setAttribute('autoplay', 'true');
    this.videoElement.setAttribute('playsinline', 'true');

    // Acceder a la cámara
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        this.videoElement.srcObject = stream;
      })
      .catch((err) => {
        console.error('Error al acceder a la cámara: ', err);
      });
  }
}
