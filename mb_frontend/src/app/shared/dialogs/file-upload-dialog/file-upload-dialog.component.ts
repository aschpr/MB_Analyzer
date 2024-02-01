import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FileUploader } from 'ng2-file-upload';

@Component({
  selector: 'app-file-upload-dialog',
  templateUrl: './file-upload-dialog.component.html',
  styleUrls: ['./file-upload-dialog.component.css']
})
export class FileUploadDialogComponent implements OnInit {

  public uploader: FileUploader = new FileUploader({ url: 'http://127.0.0.1:3333/' });
  public hasBaseDropZoneOver = false;

  constructor(@Inject(MAT_DIALOG_DATA) public data: any) {

  }

  public ngOnInit(): void {
    this.uploader.onAfterAddingFile = (file) => { file.withCredentials = false; };
  }

  fileOverBase(e: any): void {
    this.hasBaseDropZoneOver = e;
  }

  uploadFile() {
    this.uploader.uploadAll();
  }

  clearQueue() {
    this.uploader.clearQueue();
  }

}
