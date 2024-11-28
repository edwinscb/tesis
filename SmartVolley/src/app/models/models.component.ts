import { Component, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { io } from 'socket.io-client';

declare class ImageCapture {
  constructor(videoTrack: MediaStreamTrack);
  grabFrame(): Promise<ImageBitmap>;
}
@Component({
  selector: 'app-models',
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.scss']
})
export class ModelsComponent {
  title: string = 'Pruebas';
  
  private socket: any;
  private stream: MediaStream | null = null;
  private currentCameraId: number = 0;
  public  isTrack: boolean = false;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    if (isPlatformBrowser(this.platformId)) {
      this.socket = io(); // Conecta al servidor Socket.IO
      this.initializeCamera(this.currentCameraId);
    }
  }

  async getCameras(): Promise<MediaDeviceInfo[]> {
    if (isPlatformBrowser(this.platformId)) {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.filter(device => device.kind === 'videoinput');
      } catch (err) {
        console.error("Error al obtener las cámaras:", err);
        return [];
      }
    } else {
      console.warn("API de dispositivos no disponible en el servidor.");
      return [];
    }
  }

  async initializeCamera(cameraId: number): Promise<void> {
    if (isPlatformBrowser(this.platformId)) {
      try {
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
        }
        const videoDevices = await this.getCameras();
        if (videoDevices.length === 0) {
          console.error("No se detectaron cámaras.");
          alert("No se encontraron cámaras en este dispositivo.");
          return;
        }
        const constraints = { video: { deviceId: videoDevices[cameraId].deviceId } };
        this.stream = await navigator.mediaDevices.getUserMedia(constraints);
        this.captureAndSendFrames(this.stream);
      } catch (err) {
        console.error("Error al acceder a la cámara:", err);
      }
    }
  }

  async changeCamera(): Promise<void> {
    const cameras = await this.getCameras();
    if (cameras.length > 1) {
      this.currentCameraId = (this.currentCameraId + 1) % cameras.length;
      this.initializeCamera(this.currentCameraId);
    } else {
      console.warn("Solo se detectó una cámara.");
    }
  }

  captureAndSendFrames(stream: MediaStream): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const videoTrack = stream.getVideoTracks()[0];
    const imageCapture = new ImageCapture(videoTrack);
    let errorCount = 0;
    const maxErrors = 5;

    const captureFrame = async () => {
      try {
        const imageBitmap = await imageCapture.grabFrame();
        const base64Frame = this.convertFrameToBase64(imageBitmap);

        if (base64Frame) {
          this.socket.emit('start_video', { frame: base64Frame });
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
        setTimeout(captureFrame, 500 * errorCount);
      }
    };

    captureFrame();
  }

  convertFrameToBase64(imageBitmap: ImageBitmap): string {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = imageBitmap.width;
    tempCanvas.height = imageBitmap.height;

    const tempCtx = tempCanvas.getContext('2d');
    tempCtx?.drawImage(imageBitmap, 0, 0);

    return tempCanvas.toDataURL('image/jpeg');
  }

  toggleModel(): void {
    this.isTrack = !this.isTrack;
    this.socket.emit('model_toggle', { isTrack: this.isTrack });
  }

  toggleFullscreen(canvas?: HTMLCanvasElement): void {
    if (!canvas) {
      console.error('Canvas no proporcionado');
      return;
    }
  
    if (canvas.requestFullscreen) {
      canvas.requestFullscreen();
    } else if ((canvas as any).mozRequestFullScreen) {
      (canvas as any).mozRequestFullScreen();
    } else if ((canvas as any).webkitRequestFullscreen) {
      (canvas as any).webkitRequestFullscreen();
    } else if ((canvas as any).msRequestFullscreen) {
      (canvas as any).msRequestFullscreen();
    }
  }
  
}
