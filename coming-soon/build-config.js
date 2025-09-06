// Build script to generate config.js from environment variables
// This script can be run during Dokploy deployment

const fs = require('fs');
const path = require('path');

// Get environment variables or use defaults
const progressPercentage = process.env.PROGRESS_PERCENTAGE || process.env.DEVELOPMENT_PROGRESS || 25;
const statusMessage = process.env.STATUS_MESSAGE || "Under Development";
const maintenanceMode = process.env.MAINTENANCE_MODE === 'true' || false;

// Generate config.js content
const configContent = `// Auto-generated config file
// Generated at: ${new Date().toISOString()}

window.PROGRESS_PERCENTAGE = ${parseInt(progressPercentage)};
window.DEVELOPMENT_PROGRESS = ${parseInt(progressPercentage)};
window.STATUS_MESSAGE = "${statusMessage}";
window.MAINTENANCE_MODE = ${maintenanceMode};

console.log('Config loaded: Progress = ${progressPercentage}%');
`;

// Write config.js file
fs.writeFileSync(path.join(__dirname, 'config.js'), configContent);
console.log(`Config generated: Progress = ${progressPercentage}%`);
