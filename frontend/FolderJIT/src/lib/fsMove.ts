// import { writeTextFile, readTextFile, exists, BaseDirectory, rename } from '@tauri-apps/plugin-fs';
// import { join } from '@tauri-apps/api/path';
// import { openPath } from '@tauri-apps/plugin-opener';

// const DEST_CONFIG_FILE = 'dest.txt';

// export async function setDefaultFolder() {
//   const folder = await openPath({ directory: true });
//   if (typeof folder === 'string') {
//     await writeTextFile(DEST_CONFIG_FILE, folder, {
//       baseDir: BaseDirectory.AppConfig,
//     });
//     return folder;
//   }
//   return null;
// }

// export async function getDefaultFolder(): Promise<string | null> {
//   const configExists = await exists(DEST_CONFIG_FILE, {
//     baseDir: BaseDirectory.AppConfig,
//   });
//   if (!configExists) return null;

//   return await readTextFile(DEST_CONFIG_FILE, {
//     baseDir: BaseDirectory.AppConfig,
//   });
// }

// export async function moveFileToDefaultFolder() {
//   const defaultFolder = await getDefaultFolder();
//   if (!defaultFolder) throw new Error('No default folder set.');

//   const source = await openPath({ multiple: false });
//   if (!source || typeof source !== 'string') return;

//   const filename = source.split('/').pop();
//   if (!filename) return;

//   const destination = await join(defaultFolder, filename);

//   await rename(source, destination, {
//     fromPathBaseDir: undefined,
//     toPathBaseDir: undefined,
//   });
// }

import { open } from '@tauri-apps/plugin-dialog';

async function selectFile() {
  const selected = await open({
    multiple: false,
    directory: false,
    filters: [
      {
        name: 'Images',
        extensions: ['png', 'jpg', 'jpeg'],
      },
    ],
  });

  if (selected === null) {
    console.log('No file selected');
  } else {
    console.log('Selected file:', selected);
  }
}

selectFile();
