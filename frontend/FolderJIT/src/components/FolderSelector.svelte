<script lang="ts">
    import { onMount } from 'svelte';
    import { open } from '@tauri-apps/plugin-dialog';
    import { getFolderPath, setFolderPath } from '$lib/store';
  
    let folderPath: string | null = null;
  
    onMount(async () => {
      folderPath = await getFolderPath();
      if (!folderPath) {
        const selected = await open({ directory: true });
        if (selected && typeof selected === 'string') {
          folderPath = selected;
          await setFolderPath(folderPath);
        }
      }
    });
    
    async function selectFolder() {
      const selected = await open({ directory: true });
      if (selected && typeof selected === 'string') {
        folderPath = selected;
        setFolderPath(folderPath);
      }
    }
  </script>

  {#if folderPath}
    <p>Selected folder: {folderPath}</p>
  {:else}
    <p>No folder selected.</p>
  {/if}


<style>
  input,
  button {
    border-radius: 12px;
    border: 1px solid transparent;
    width: 50%;
    align-self: center;
    padding: 0.6em 1.2em;
    font-size: 1em;
    font-weight: 500;
    font-family: inherit;
    color: #0f0f0f;
    background-color: #ffffff;
    transition: border-color 0.25s;
    box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2);
  }

  button {
    cursor: pointer;
  }

  button:hover {
    border-color: #396cd8;
  }
  button:active {
    border-color: #396cd8;
    background-color: #e8e8e8;
  }

  input,
  button {
    outline: none;
  }
</style>
  