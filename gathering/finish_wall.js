// Preserve the verified ancestor outside the image tool's new small motif.
// Run once after generation, while wall.png is the verified round-24 ancestor.
'use strict';
const fs = require('node:fs');
const zlib = require('node:zlib');
const crypto = require('node:crypto');
const {decode, thumbnail} = require('./thumbnail.js');
const oldBytes = fs.readFileSync('artifacts/gathering/wall.png');
const ancestor = 'e7a3fd8ca98f132c65b60585e268f685a9b9823183c986037463581666975880';
if (crypto.createHash('sha256').update(oldBytes).digest('hex') !== ancestor)
  throw new Error('wall.png must still be the verified round-24 ancestor');
const old = decode(oldBytes);
const generatedBytes = fs.readFileSync('artifacts/gathering/wall-v5.png');
const generatedHash = crypto.createHash('sha256').update(generatedBytes).digest('hex');
const fresh = decode(generatedBytes);
if (old.width !== fresh.width || old.height !== fresh.height || old.channels !== 3)
  throw new Error('image tool output must match the inherited wall dimensions');
const out = Buffer.from(old.pixels);
const bounds = [215, 225, 425, 340];
let changed = 0;
let box = [old.width, old.height, -1, -1];
for (let y = bounds[1]; y <= bounds[3]; y++) for (let x = bounds[0]; x <= bounds[2]; x++) {
  const alpha = Math.min(1, Math.min(x-bounds[0], bounds[2]-x, y-bounds[1], bounds[3]-y)/8);
  const p = (y*old.width+x)*3;
  const q = (y*fresh.width+x)*fresh.channels;
  for (let c=0;c<3;c++) out[p+c] = Math.round(old.pixels[p+c]*(1-alpha)+fresh.pixels[q+c]*alpha);
}
let outside = 0;
for (let y=0;y<old.height;y++) for (let x=0;x<old.width;x++) {
  const p=(y*old.width+x)*3;
  if (out[p] !== old.pixels[p] || out[p+1] !== old.pixels[p+1] || out[p+2] !== old.pixels[p+2]) {
    changed++;
    box=[Math.min(box[0],x),Math.min(box[1],y),Math.max(box[2],x),Math.max(box[3],y)];
    if(x<bounds[0]||x>bounds[2]||y<bounds[1]||y>bounds[3]) outside++;
  }
}
if (!changed || outside) throw new Error('new mark absent or preservation failed');
function crc32(bytes) {
  let crc=0xffffffff;
  for(const v of bytes){crc^=v;for(let b=0;b<8;b++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}
  return (crc^0xffffffff)>>>0;
}
function chunk(name,data) {
  const kind=Buffer.from(name),length=Buffer.alloc(4),crc=Buffer.alloc(4);
  length.writeUInt32BE(data.length);crc.writeUInt32BE(crc32(Buffer.concat([kind,data])));
  return Buffer.concat([length,kind,data,crc]);
}
const ihdr=Buffer.alloc(13);
ihdr.writeUInt32BE(old.width);ihdr.writeUInt32BE(old.height,4);ihdr[8]=8;ihdr[9]=2;
const stride=old.width*3,scan=Buffer.alloc(old.height*(stride+1));
for(let y=0;y<old.height;y++)out.copy(scan,y*(stride+1)+1,y*stride,(y+1)*stride);
const png=Buffer.concat([Buffer.from('89504e470d0a1a0a','hex'),chunk('IHDR',ihdr),
  chunk('IDAT',zlib.deflateSync(scan,{level:9})),chunk('IEND',Buffer.alloc(0))]);
fs.writeFileSync('artifacts/gathering/wall-v5.png',png);
fs.writeFileSync('artifacts/gathering/wall.png',png);
const jpeg=thumbnail(png,512,75);
if(jpeg.length>=100000)throw new Error('JPEG exceeds file size budget');
fs.writeFileSync('dist/gathering/25.jpg',jpeg);
const result={ancestor_sha256:ancestor,generated_sha256:generatedHash,
  png:{path:'artifacts/gathering/wall-v5.png',format:'PNG',mode:'RGB',dimensions:[old.width,old.height],
    bytes:png.length,sha256:crypto.createHash('sha256').update(png).digest('hex')},
  jpeg:{path:'dist/gathering/25.jpg',format:'JPEG',dimensions:[512,512],bytes:jpeg.length},
  preservation:{rectangle:bounds,changed_pixels:changed,changed_bounds:box,outside_rectangle_changed_pixels:outside},
  visual_review_required:true};
fs.writeFileSync('gathering/image-checks25.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
