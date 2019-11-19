const fs = require("fs");

const f = fs.readFileSync("visited.json");

const json = JSON.parse(f);
console.log(json);

const length = Object.keys(json).length;
console.log(length);