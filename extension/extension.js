// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const workspace = require('vscode').workspace;
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
let customTerminal = vscode.window.createTerminal('smartcallhierarchy Terminal'); // Declare a variable to store the terminal
const textPath = path.join(__dirname, './doc2cli.txt');
const { chat } = require('vscode');

class FunctionCodeLensProvider {
    provideCodeLenses(document, token) {
        console.log("provideCodeLenses called for document:", document.uri.toString());
        const codeLenses = [];
        const regex = /def\s+\w+/g; // Adjust this regex based on the language and function patterns
        const text = document.getText();
        let matches;
        while ((matches = regex.exec(text)) !== null) {
            console.log("Function match found:", matches[0]); // Log each match found
            
            const match = matches[0];
            const line = document.lineAt(document.positionAt(matches.index).line);
            const position = new vscode.Position(line.lineNumber, 0);
            const range = new vscode.Range(position, position);
            const command = {
                title: "Show Call Hierarchy",
                command: "extension.generateCallHierarchy", // Command to trigger Show Call Hierarchy
                arguments: [document.uri.fsPath]
            };
            codeLenses.push(new vscode.CodeLens(range, command));
        }
        return codeLenses;
    }
}


class ChatProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;

        this.chatMessages = [];
    }

    getTreeItem(element) {
        return new vscode.TreeItem(element.content);
    }

    getChildren(element) {
        if (!element) {
            return this.chatMessages;
        }
        return [];
    }

    // Method to add a new message
    addMessage(content) {
        const newMessage = { id: this.chatMessages.length + 1, content };
        this.chatMessages.push(newMessage);
        this._onDidChangeTreeData.fire();
    }
}


function findFilesByPattern(startPath, filter) {
    return new Promise((resolve, reject) => {
        if (!fs.existsSync(startPath)) {
            console.log("Directory not found:", startPath);
            return reject("Directory not found");
        }
		console.log('Directory found:', startPath);
        let filenames = [];
        const files = fs.readdirSync(startPath);
        files.forEach(file => {
            const filename = path.join(startPath, file);
            const stat = fs.lstatSync(filename);
            if (stat.isDirectory()) {
                // If it's a directory, recursively call this function
                filenames = filenames.concat(findFilesByPattern(filename, filter));
				console.log('filenames:', filenames);
            } else if (filter.test(filename)) {
                filenames.push(filename);
            }
        });
        resolve(filenames);
    });
}

// Modify generateCallHierarchy to use async/await for findFilesByPattern
async function generateCallHierarchy(filePath) {
    const outputFilePath = path.join(__dirname, 'call_hierarchy.dot');
    fs.writeFileSync(outputFilePath, ''); // Ensure the output file is empty 

    try {
        // Get the root directory of the user's workspace
        const workspaceRoot = workspace.workspaceFolders[0].uri.fsPath;

        const files = await findFilesByPattern(workspaceRoot, /\.py$/); // Use root directory
        for (const file of files) { 
            console.log('-- found:', file);
            const command = `pyan3 "${file}" --dot`;
            console.log('Executing command: ' + command);
            exec(command, { shell: true, env: process.env }, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Error executing pyan3 for ${file}: ${error}`);
                    return;
                }
                fs.appendFileSync(outputFilePath, stdout);
                console.log('file ' + file + ' = ' + stdout);
            });
        };
    } catch (error) {
        console.error('Error finding files:', error);
    }
}
/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Congratulations, your extension "smartcallhierarchy" is now active!');

    // Register the webview command
    let disposableWebview = vscode.commands.registerCommand('smartcallhierarchy.showWebview', async function () {
        const panel = vscode.window.createWebviewPanel(
            'interactiveWebview',
            'Interactive Webview',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
            }
        );

        try {
            // const content = await fetchExternalContent(); // Now valid because the function is async
            const content = getWebviewContent();
            panel.webview.html = content;
        } catch (error) {
            console.error('Failed to fetch external content:', error);
            panel.webview.html = `Error fetching content: ${error}`;
        }
    });

    context.subscriptions.push(disposableWebview);

    const chatProvider = new ChatProvider();
    vscode.window.registerTreeDataProvider('chatPanel', chatProvider);

    context.subscriptions.push(vscode.commands.registerCommand('extension.addChatMessage', async () => {
        const message = await vscode.window.showInputBox({ placeHolder: 'Type a message...' });
        if (message) {
            chatProvider.addMessage(message);
        }
    }));


    context.subscriptions.push(vscode.commands.registerCommand('smartcallhierarchy.openChatPanel', () => {
        vscode.commands.executeCommand('workbench.view.extension.chatSidebar');
    }));

    // Register the 'smartcallhierarchy.execute' command
    context.subscriptions.push(vscode.commands.registerCommand('smartcallhierarchy.execute', async () => {
        vscode.window.showInformationMessage("smartcallhierarchy command executed.");
    }));

    // Register the CodeLens provider for Python files
    context.subscriptions.push(vscode.languages.registerCodeLensProvider({language: 'python'}, new FunctionCodeLensProvider()));

    // Register the 'extension.runFunction' command
    context.subscriptions.push(vscode.commands.registerCommand('extension.runFunction', function (funcName) {
        vscode.window.showInformationMessage(`Showing call traces for function: ${funcName}`);
    }));

    // Register the 'extension.generateCallHierarchy' command
    context.subscriptions.push(vscode.commands.registerCommand('extension.generateCallHierarchy', function () {
        let editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage("No active editor found.");
            return;
        }

        let filePath = editor.document.fileName;
        generateCallHierarchy(filePath);
    }));

}

function getWebviewContent() {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <!-- Include the CSP meta tag below -->
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'; frame-src http://localhost:5173; style-src 'self' 'unsafe-inline';">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Webview Title</title>
    <style>
        html, body {
            height: 100%;
            width: 100%;
            padding: 0;
            margin: 0;
        }
        body {
            background-color: red;
        }
        iframe {
            min-height: 1000px;
            height: 100%;
            width: 100%;
        }
    </style>
    </head>
    <body>
        <iframe src="http://localhost:5173/" width="100%" height="100%"></iframe>
    </body>
    </html>`;
}
{/* <iframe src="http://35.88.110.113:5173/" width="100%" height="500px"></iframe> */}

function deactivate() {}

function fetchExternalContent() {
    return new Promise((resolve, reject) => {
        exec('curl http://35.88.110.113:5173/', (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                return reject(error);
            }
            resolve(stdout);
        });
    });
}

module.exports = {
    activate,
    deactivate: function() {}
}


// function fetchExternalContent() {
//     return new Promise((resolve, reject) => {
//         const command = `curl 35.88.110.113:8080/generate -X POST -d '{"inputs":"what is pizza?","parameters":{"max_new_tokens":50}}' -H "Content-Type: application/json"`;
//         exec(command, (error, stdout, stderr) => {
//             if (error) {
//                 console.error(`exec error: ${error}`);
//                 return reject(error);
//             }
//             resolve(stdout);
//         });
//     });
// }