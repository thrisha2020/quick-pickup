const fs = require('fs');
const path = require('path');

const vscodeDir = path.join(__dirname, '.vscode');
const settingsPath = path.join(vscodeDir, 'settings.json');
const settings = {
    "css.lint.unknownAtRules": "ignore",
    "editor.quickSuggestions": {
        "strings": true
    },
    "tailwindCSS.emmetCompletions": true,
    "editor.quickSuggestions": {
        "strings": true
    },
    "files.associations": {
        "*.html": "html"
    }
};

// Create .vscode directory if it doesn't exist
if (!fs.existsSync(vscodeDir)) {
    fs.mkdirSync(vscodeDir);
}

// Write settings to file
fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 4));

console.log('✅ VS Code settings have been configured successfully!');
console.log('Please restart VS Code for the changes to take effect.');
