const fs = require('fs');
const path = require('path');

function File (path) {
}

File.get = get = function (filePath, callback) {
  console.log('file path: '+filePath);
  fs.readFile (filePath, callback);
}

File.getExt = function (fileName) {
  return path.extname(fileName)
}

File.mimes = {
    ".html" : "text/html",
    ".js": "application/javascript",
    ".db": "application/json",
    ".css": "text/css",
    ".txt": "text/plain",
    ".jpg": "image/jpeg",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".png": "image/png",
    ".woff": "application/font-woff",
    ".woff2": "application/font-woff2"
}

module.exports = {File:File};
