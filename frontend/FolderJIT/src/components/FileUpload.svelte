<script>
// @ts-nocheck

    import { writeFile, removeFile, BaseDirectory } from '@tauri-apps/plugin-fs';
    import { appDataDir } from '@tauri-apps/api/path';
  
    let droppedFile = null;
    let targetDir = BaseDirectory.Document; // Change this if needed
    let message = '';
  
    // Triggered by file input or drop
    async function handleFileInput(event) {
      const file = event.target?.files?.[0] || event.dataTransfer?.files?.[0];
      if (!file) return;
  
      droppedFile = file;
  
      try {
        const arrayBuffer = await file.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
  
        const newPath = file.name;
  
        await writeFile(newPath, uint8Array, { baseDir: targetDir });
  
        message = `File "${file.name}" moved to ${targetDir}`;
      } catch (err) {
        console.error('Error moving file:', err);
        message = 'Error moving file';
      }
    }
  
    function handleDrop(event) {
      event.preventDefault();
      handleFileInput(event);
    }
  
    function handleDragOver(event) {
      event.preventDefault();
    }
  </script>
  
  <style>
    .dropzone {
      border: 2px dashed #aaa;
      padding: 2rem;
      text-align: center;
      border-radius: 8px;
      cursor: pointer;
    }
  </style>
  
  <!-- Dropzone UI -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="dropzone" on:drop={handleDrop} on:dragover={handleDragOver}>
    <p>Drag & drop a file here or click to select one</p>
    <input type="file" on:change={handleFileInput} style="display: none" bind:this={fileInput} />
  </div>
  
  <p>{message}</p>
  
