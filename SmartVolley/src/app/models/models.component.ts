import { Component, OnInit, AfterViewInit } from '@angular/core';

@Component({
  selector: 'app-models',
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.scss']
})
export class ModelsComponent implements OnInit, AfterViewInit {
  videoElement!: HTMLVideoElement;
  title: string = 'Detección';
  videoStream: MediaStream | null = null;
  currentCamera: number = 0;

  constructor() {}

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    if (typeof document !== 'undefined') {
      this.startCamera();
    }
  }

  startCamera(deviceId: string = ''): void {
    this.videoElement = <HTMLVideoElement>document.querySelector('video');
    this.videoElement.setAttribute('autoplay', 'true');
    this.videoElement.setAttribute('playsinline', 'true');

    const constraints: MediaStreamConstraints = {
      video: deviceId ? { deviceId: { exact: deviceId } } : true
    };

    navigator.mediaDevices.getUserMedia(constraints)
      .then((stream) => {
        if (this.videoStream) {
          this.videoStream.getTracks().forEach(track => track.stop());
        }
        this.videoStream = stream;
        this.videoElement.srcObject = stream;
      })
      .catch((err) => {
        console.error('Error al acceder a la cámara: ', err);
      });
  }

  switchCamera(): void {
    navigator.mediaDevices.enumerateDevices()
      .then(devices => {
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        if (videoDevices.length > 1) {
          this.currentCamera = (this.currentCamera + 1) % videoDevices.length;
          this.startCamera(videoDevices[this.currentCamera].deviceId);
        }
      })
      .catch(err => {
        console.error('Error al obtener dispositivos: ', err);
      });
  }

  toggleFullScreen(): void {
    const videoElement = this.videoElement as any;
    if (videoElement.requestFullscreen) {
      videoElement.requestFullscreen();
    } else if (videoElement.mozRequestFullScreen) {
      videoElement.mozRequestFullScreen();
    } else if (videoElement.webkitRequestFullscreen) {
      videoElement.webkitRequestFullscreen();
    } else if (videoElement.msRequestFullscreen) {
      videoElement.msRequestFullscreen();
    }
  }

  toggleTitle(): void {
    this.title = this.title === 'Detección' ? 'Seguimiento' : 'Detección';
  }
}
