import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MBEntry, ProcessingSettings, ScriptSettings } from '../models';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class HttpHandlerService {

  public readonly BASE_URL = 'http://127.0.0.1:8001/';

  constructor(private http: HttpClient) { }

  public getFileLODNameList(): Observable<string[]> {
    return this.http.get<string[]>(this.BASE_URL + 'get-lod-file-names');
  }

  public getFileRawNameList(): Observable<string[]> {
    return this.http.get<string[]>(this.BASE_URL + 'get-raw-file-names');
  }

  public postFileProcessing(fileConf: ProcessingSettings): Observable<boolean> {
    return this.http.post<boolean>(this.BASE_URL + 'post-process-file/', fileConf);
  }

  public postExecuteScripts(scripts: ScriptSettings): Observable<boolean> {
    return this.http.post<boolean>(this.BASE_URL + 'post-execute-script/', scripts);
  }
  
  public deleteFile(file_name:string): Observable<boolean> {
    return this.http.post<boolean>(this.BASE_URL + 'post-file-delete/', {file_name: file_name});
  }
}

