import { load } from '@tauri-apps/plugin-store';

const store = await load('settings.json', { autoSave: false });


export async function getFolderPath(): Promise<string | null> {
  return await store.get<string>('default_folder') || null;
}

export async function setFolderPath(path: string): Promise<void> {
  await store.set('default_folder', path);
  await store.save();
}
