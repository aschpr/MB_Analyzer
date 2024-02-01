import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PotreeDataViewerComponent } from './potree-data-viewer/potree-data-viewer.component';
import {MatProgressBarModule} from '@angular/material/progress-bar';  
import {MatDialogModule} from '@angular/material/dialog'; 
import { FileUploadModule } from 'ng2-file-upload';
import { FileUploadDialogComponent } from './dialogs/file-upload-dialog/file-upload-dialog.component';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner'; 

@NgModule({
  imports: [
    CommonModule,
    MatProgressBarModule,
    MatDialogModule,
    FileUploadModule,
    MatProgressSpinnerModule
  ],
  exports: [ PotreeDataViewerComponent],
  declarations: [PotreeDataViewerComponent, FileUploadDialogComponent]
})
export class SharedModule { }
