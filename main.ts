// Entry for make.fun news-image-20261121: "Sum up 21 November's world news
// in one image". The front page is rendered by build_front.py into entry.png
// (a JPEG under 1 MiB, 1024x1024). This program copies it to /output/entry.png
// after checking the bytes are a whole 1024x1024 JPEG, so both of the
// grader's runs write exactly the same file.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   python3 build_front.py && mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const src = new URL('./entry.png', import.meta.url);
const bytes = readFileSync(src);
if (bytes.length < 2 || bytes[0] !== 0xff || bytes[1] !== 0xd8) {
  throw new Error('entry.png is not a JPEG');
}
if (bytes[bytes.length - 2] !== 0xff || bytes[bytes.length - 1] !== 0xd9) {
  throw new Error('entry.png is not a whole JPEG (no end marker)');
}
if (bytes.length > 1048576) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB gate`);
}
// Walk the JPEG markers to the frame header (SOF0/SOF2) and read its size.
let i = 2;
let width = 0;
let height = 0;
while (i + 9 < bytes.length) {
  if (bytes[i] !== 0xff) throw new Error('entry.png has a broken JPEG marker');
  const marker = bytes[i + 1];
  const len = bytes.readUInt16BE(i + 2);
  if (marker === 0xc0 || marker === 0xc2) {
    height = bytes.readUInt16BE(i + 5);
    width = bytes.readUInt16BE(i + 7);
    break;
  }
  i += 2 + len;
}
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
copyFileSync(src, join(outDir, 'entry.png'));
if (statSync(join(outDir, 'entry.png')).size !== bytes.length) {
  throw new Error('copied entry.png differs in size from the source');
}
