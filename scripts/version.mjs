import {createHash} from 'node:crypto';
import {readdir,readFile} from 'node:fs/promises';
import path from 'node:path';
export async function appVersion(root){const names=['index.html'];async function walk(dir){for(const e of await readdir(path.join(root,dir),{withFileTypes:true})){const name=dir+'/'+e.name;if(e.isDirectory())await walk(name);else if(e.isFile())names.push(name);}}for(const dir of ['css','js','data','fonts'])await walk(dir);const hash=createHash('sha256');for(const name of names.sort()){hash.update(name);hash.update('\0');hash.update(await readFile(path.join(root,name)));hash.update('\0');}return hash.digest('hex');}
