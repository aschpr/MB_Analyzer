import { AfterViewInit, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { PointCloudOctree, Potree } from 'potree-core';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { PCDLoader } from 'three/examples/jsm/loaders/PCDLoader.js';
import { GUI } from 'three/examples/jsm/libs/lil-gui.module.min.js';
import { generateUUID } from 'three/src/math/MathUtils';
import { HttpHandlerService } from 'src/app/services/http-handler.service';
import {MatDialog,} from '@angular/material/dialog';
import { FileUploadDialogComponent } from '../dialogs/file-upload-dialog/file-upload-dialog.component';
import { ScriptSettings } from 'src/app/models';

@Component({
  selector: 'app-potree-data-viewer',
  templateUrl: './potree-data-viewer.component.html',
  styleUrls: ['./potree-data-viewer.component.css']
})
export class PotreeDataViewerComponent implements AfterViewInit {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private controls: OrbitControls;

  public FILE_SERVER_URL = 'http://127.0.0.1:3333/';

  public fileLoading: {filename: string, status: "loading" | "ready" | "error", size: number, percentage: number}[] = [];

  @ViewChild('rendererContainer') rendererContainer: ElementRef;

  public allScripts: string[] = [];
  public selectedLODFile: string;

  constructor(private httpHandler: HttpHandlerService, public dialog: MatDialog) { }

  public fileLODNameList: string[] = [];
  public fileRawNameList: string[] = [];

  public selectFileForProcessing: string = "";
  public isFileProcessing: boolean = false;

  public ngOnInit(): void {

    this.refreshFileList();
  }
  
  ngAfterViewInit() {
    this.initThreeJs();
    this.render();

  }

  public refreshFileList() {
    this.httpHandler.getFileLODNameList().subscribe((fileNames: string[]) => {
      this.fileLODNameList = fileNames;
    });

    this.httpHandler.getFileRawNameList().subscribe((fileNames: string[]) => {
      this.fileRawNameList = fileNames;
    });
  }

  private initThreeJs() {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(60, 1, 0.1, 10000);

    // set camera render distance
    this.camera.far = 500000;

    this.renderer = new THREE.WebGLRenderer({
        canvas: this.rendererContainer.nativeElement,
        alpha: true,
        logarithmicDepthBuffer: false,
        precision: 'highp',
        premultipliedAlpha: true,
        antialias: true,
        preserveDrawingBuffer: false,
        powerPreference: 'high-performance'
    });
    // set renderer size
    this.renderer.setSize(window.innerWidth, window.innerHeight);

    // set background color
    this.renderer.setClearColor(0x000000);

    const geometry_box = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    const cube = new THREE.Mesh(geometry_box, material);
    this.scene.add(cube);

    this.controls = new OrbitControls(this.camera, this.rendererContainer.nativeElement);
    this.camera.position.z = 10;

    // add grid to scene
    let grid = new THREE.GridHelper();
    grid.position.y = -5;
    this.scene.add(grid);

    this.managePointCloudRequest("mb_raw")

  }


  private managePointCloudRequest(filename: string) {
    // remove all children from scene
    this.scene.clear();

    // load point cloud
    const loader = new PCDLoader();
    let promises: Promise<THREE.Points<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.PointsMaterial>>[] = [];
    this.getFileNameLODVariation(filename + ".pcd").forEach((fileVariation: string) => {
      console.log(`LOD Level: ${fileVariation} from -> ${this.FILE_SERVER_URL + fileVariation}`);
      promises.push(this.loadPCDFile(loader, this.FILE_SERVER_URL + fileVariation));
    });

    const lod = new THREE.LOD();
    this.scene.add(lod);

    Promise.all(promises).then((points: THREE.Points<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.PointsMaterial>[]) => {
      points.forEach((pointCloud: THREE.Points<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.PointsMaterial>, i: number) => {
        let lodLevel: number = i === 0 ? 0 : i === 1 ? 300 : i === 2 ? 500 : 3;
        lod.addLevel(pointCloud, i * 300 );
      });
    });
  }

  private loadPCDFile(loader: PCDLoader, url: string): Promise<THREE.Points<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.PointsMaterial>> {
    let pointNameArray = url.split('/');
    let name = pointNameArray[pointNameArray.length - 1];

    this.fileLoading.push({filename: name, status: "loading", size: 0, percentage: 0});

    return new Promise((resolve, reject) => {
      loader.load(url, (points) => {
        
        let newPoints = this.managePointCloudRenderSettings(points);
        newPoints.name = name;

        this.fileLoading.forEach((file) => {
          if(file.filename === name) {
            file.status = "ready";
          }
        });

        resolve(newPoints);
      }, (xhr) => {

        this.fileLoading.forEach((file) => {
          if(file.filename === name) {
            file.status = "loading";
            file.size = xhr.total;
            file.percentage = xhr.loaded / xhr.total * 100;
          }
        });
      }, (error) => {
        console.log('An error happened');
        console.error(error);
        reject(error);
      }
      );
    });
  }

  private managePointCloudRenderSettings(points: THREE.Points<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.PointsMaterial>): THREE.Points<THREE.BufferGeometry<THREE.NormalBufferAttributes>, THREE.PointsMaterial> {
    points.geometry.center(); // Center the geometry


    // Set the position of the point cloud to (0, 0, 0)
    points.position.set(0, 0, 0);
    points.scale.set(0.1, 0.1, 0.1);
    // set the color for each vertex of the point cloud
    let minHeight = Number.POSITIVE_INFINITY;
    let maxHeight = Number.NEGATIVE_INFINITY;


    for (let i = 0; i < points.geometry.attributes["position"].count; i++) {
      const height = points.geometry.attributes["position"].getY(i);

      // Update min and max heights
      if (height < minHeight) {
        minHeight = height;
      }
      if (height > maxHeight) {
        maxHeight = height;
      }
    }


    const colors = [];

    for (let i = 0; i < points.geometry.attributes["position"].count; i++) {
      const height = points.geometry.attributes["position"].getY(i);
      const color_array = this.getBathymetryColor(height, minHeight, maxHeight);
      const color = new THREE.Color(color_array[0] / 255, color_array[1] / 255, color_array[2] / 255);
      colors.push(color.r, color.g, color.b);
    }

    points.geometry.setAttribute('color', new THREE.Float32BufferAttribute(new Float32Array(colors), 3));
    const material = new THREE.PointsMaterial({ size: 0.1, vertexColors: true });

    points.material = material;
    return points;
  }

  /**
   * Renders the scene and updates the controls.
   */
  private render() {
    /**
     * Animates the scene and updates the controls.
     */
    const animate = () => {
      // Update controls
      this.controls.update();

      this.renderer.render(this.scene, this.camera);
      requestAnimationFrame(animate);
    };

    animate();
  }

  /**
   * Returns the color corresponding to the given height based on the defined color ramp.
   * @param height The height value for which to determine the color.
   * @param minHeight The minimum height value in the color ramp.
   * @param maxHeight The maximum height value in the color ramp.
   * @returns An array representing the RGB color values [red, green, blue].
   */
  private getBathymetryColor(height: number, minHeight: number, maxHeight: number): number[] {
    // Define your color ramp based on bathymetry levels
    const colorRamp = [
      { height: minHeight, color: "#000080" },  // Dark Blue
      { height: minHeight/2, color: "#0000FF" },  // Blue
      { height: 0, color: "#ADD8E6" },      // Light Blue
      { height: maxHeight/2, color: "#FFFF00" },   // Yellow
      { height: maxHeight, color: "#ff0000" },   // Red-Orange
    ];

    // Clamp the height value to be within the specified range
    const clampedHeight = Math.max(Math.min(height, maxHeight), minHeight);

    // Interpolate the color based on the height
    for (let i = 0; i < colorRamp.length - 1; i++) {
      const currentLevel = colorRamp[i];
      const nextLevel = colorRamp[i + 1];

      if (clampedHeight >= currentLevel.height && clampedHeight <= nextLevel.height) {
        const t = (clampedHeight - currentLevel.height) / (nextLevel.height - currentLevel.height);
        const interpolatedColor = this.interpolateColor(currentLevel.color, nextLevel.color, t);
        return interpolatedColor;
      }
    }

    // If the height is outside the defined range, return a default color
    return [255/255, 17/255, 0/255]; // Gray
  }

 
  /**
   * Interpolates between two colors based on a given parameter.
   * @param color1 - The first color in hexadecimal format.
   * @param color2 - The second color in hexadecimal format.
   * @param t - The parameter determining the interpolation between the two colors.
   * @returns An array representing the interpolated color in RGB format.
   */
  private interpolateColor(color1: string, color2: string, t: number): number[] {
    const hex = (c: number) => {
      const hexValue = Math.round(c).toString(16);
      return hexValue.length === 1 ? "0" + hexValue : hexValue;
    };

    const r1 = parseInt(color1.slice(1, 3), 16);
    const g1 = parseInt(color1.slice(3, 5), 16);
    const b1 = parseInt(color1.slice(5, 7), 16);

    const r2 = parseInt(color2.slice(1, 3), 16);
    const g2 = parseInt(color2.slice(3, 5), 16);
    const b2 = parseInt(color2.slice(5, 7), 16);

    const r = r1 + (r2 - r1) * t;
    const g = g1 + (g2 - g1) * t;
    const b = b1 + (b2 - b1) * t;

    return [r, g, b];
  }

  private getFileNameLODVariation(filename: string): string[] {  
    // let lodSizes: number[] = [5000000, 2000000, 1000000];
    let lodSizes: number[] = [1000000];

    let variations = lodSizes.map((size) => {
      return filename.replace('.pcd', `_lod_${size}.pcd`);
    });
    return variations;
  }

  openFileUploadDialog() {
    const dialogRef = this.dialog.open(FileUploadDialogComponent, {
      width: '75%',
      height: '75%', 
      data: {name: "test"},
      disableClose: true,

    });

    dialogRef.afterClosed().subscribe(result => {
      console.log(`Dialog result: ${result}`);
    });
  }

  onRawFileSelectChange(event: any) {
    this.selectFileForProcessing = event.target.value;
  }

  public processFile() {

    this.isFileProcessing = true;
    this.httpHandler.postFileProcessing({
      filename: this.selectFileForProcessing,
      sep: document.getElementById("sep")["value"],
      to_utm: document.getElementById("to_utm")["checked"]
    }).subscribe((result: boolean) => {
      this.isFileProcessing = false;
      this.refreshFileList();
    });
  }

  public onScriptChange(el: string) {
    if(!this.allScripts.includes(el)) {
      this.allScripts.push(el);
    } else {
      this.allScripts.splice(this.allScripts.indexOf(el), 1);
    }

    console.log(this.allScripts);
  } 

  public onExecutePressed() {
    if(this.selectedLODFile === undefined) {
      return;
    }
    let scriptSettings: ScriptSettings = {
      stat_based: this.allScripts.includes("stat_based"),
      k_means: this.allScripts.includes("k_means"),
      ml: this.allScripts.includes("ml"),
      filename: this.selectedLODFile
    };

    if(scriptSettings.stat_based || scriptSettings.k_means || scriptSettings.ml) {
      this.httpHandler.postExecuteScripts(scriptSettings).subscribe((result: boolean) => {
        console.log(result);
      });
    }
  }

  public onLODFileChange(name: any) {
    this.selectedLODFile = name.target.value;

    this.managePointCloudRequest(this.selectedLODFile);
  }

  public onFileDelete() {
    if(this.selectFileForProcessing === '') {
      return;
    }

    this.httpHandler.deleteFile(this.selectFileForProcessing).subscribe((result: boolean) => {
      console.log(result);
      this.refreshFileList();
    });
  }
}
