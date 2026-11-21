// Exercise set 05, part B — reference solution.
// Usage: node stats.mjs path/to/leads.json
import { readFile } from "node:fs/promises";

const path = process.argv[2] ?? "leads.json";
const leads = JSON.parse(await readFile(path, "utf-8"));

const byCourse = {};
for (const lead of leads) {
  const course = lead.course ?? "(unknown)";
  byCourse[course] = (byCourse[course] ?? 0) + 1;
}

console.log(`${leads.length} leads\n`);
for (const [course, count] of Object.entries(byCourse).sort((a, b) => b[1] - a[1])) {
  console.log(`${course.padEnd(26)} ${count}`);
}

const multiChannel = leads.filter((lead) => lead.sources.length > 1).length;
console.log(`\nEnquired through more than one channel: ${multiChannel}`);
