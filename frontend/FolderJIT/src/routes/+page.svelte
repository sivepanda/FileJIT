<script lang="ts">
  import { open } from "@tauri-apps/plugin-dialog";
  import FolderSelector from "../components/FolderSelector.svelte";

  async function selectFile() {
    const selected = await open({
      multiple: false,
      directory: true,
    });

    if (selected === null) {
      console.log("No file selected");
    } else {
      console.log("Selected file:", selected);
    }
  }
</script>

<main class="container">
  <h1>Welcome to <span class="highlht">FolderJIT</span></h1>

  <FolderSelector />
  



</main>

<style>
  .highlht {
    color: #e67f53;
  }
  
  :root {
    font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 24px;
    font-weight: 400;

    color: #9b8484;
    background-color: #534848;

    font-synthesis: none;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    -webkit-text-size-adjust: 100%;
  }

  .container {
    margin: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
  }

  h1 {
    text-align: center;
  }

  @media (prefers-color-scheme: dark) {
    :root {
      color: #f6f6f6;
      background-color: #222422;
    }

    
  }
</style>
