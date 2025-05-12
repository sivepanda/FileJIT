<script lang="ts">
    import { copyFile, BaseDirectory, rename, exists, create, mkdir } from '@tauri-apps/plugin-fs';
    import { getCurrentWebview, Webview } from "@tauri-apps/api/webview";
    import { join } from '@tauri-apps/api/path';
    import { getCurrentWindow } from '@tauri-apps/api/window';
    import * as path from '@tauri-apps/api/path';
  
    let draggedOver = $state(false);
    let selectedFile: File | null = $state(null);
    let status = $state('');
    let filestat= $state('');


     getCurrentWindow().onDragDropEvent( async (event) => {
        if (event.payload.type === 'over') {

            filestat = "over"
            draggedOver = true;
        } else if (event.payload.type === 'drop') {
            filestat = "User drop";
            // create data dir if it dosen't already (should be during setup)
            const appDataDir = await path.resolve(await path.appDataDir())
            filestat = appDataDir 

            // filestat = await exists(appDataDir) ? "t" : "f"

            // await mkdir(appDataDir, {recursive: true});


            filestat = "Uploading file";
            const y = event.payload.paths[0].split(path.sep());
            const filename = y[y.length - 1];
            filestat = "User drop" + filename + " " + appDataDir;

            if (! await exists(appDataDir) ) {
                await mkdir(appDataDir)
            }

            await rename(event.payload.paths[0], await path.resolve(appDataDir, filename)).then(() => {
              // draggedOver = false;
            })
            filestat = ""; 
            draggedOver = false;
        } else {
            console.log('File drop cancelled');
            draggedOver = false;
        }
    })
  </script>
  
  
  <div
    class="drop-zone {draggedOver ? "dragged" : "hidden"}"
  />
  
  <main>
    <h1>Welcome to <span>FileJIT</span></h1>
    <p>Drag and drop a file anywhere on the page. {filestat}</p>
  
  </main>

  <style>
    main {
        height: 95vh;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-items: center;
        justify-content: center;
    }

    span {
        color: coral;
    }

    .drop-zone {
      position: fixed;
      inset: 0;
      border: 3px dashed #aaa;
      background-color: rgba(0, 0, 0, 0.03);
      display: flex;
      align-items: center;
      justify-content: center;
      pointer-events: none;
      z-index: 10;
    }
  
    .dragged {
      border-color: #007bff;
      background-color: rgba(0, 123, 255, 0.1);
    }
  
    .hidden {
      display: none;
    }
  
  </style>