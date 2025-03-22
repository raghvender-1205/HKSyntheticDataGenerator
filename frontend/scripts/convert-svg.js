import fs from 'fs';
import path from 'path';
import sharp from 'sharp';

// Path to SVG file
const svgPath = path.resolve('static/flow-diagram.svg');
const outputPath = path.resolve('static/flow-diagram.png');

// Read SVG file
const svgBuffer = fs.readFileSync(svgPath);

// Convert SVG to PNG
sharp(svgBuffer)
  .png()
  .toFile(outputPath)
  .then(() => {
    console.log(`Successfully converted ${svgPath} to ${outputPath}`);
  })
  .catch(err => {
    console.error('Error converting SVG to PNG:', err);
  }); 