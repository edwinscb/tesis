import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './Components/navbar/navbar.component';
import { ModelsComponent } from './models/models.component';
import { SocketService } from './Services/socket.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet,NavbarComponent,ModelsComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'SmartVolley';
}
