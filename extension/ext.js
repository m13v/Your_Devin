// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
let customTerminal = vscode.window.createTerminal('readMeSimplified Terminal'); // Declare a variable to store the terminal
const textPath = path.join(__dirname, './doc2cli.txt');

// Function to fetch HTML
async function fetchHtml(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return await response.text(); // Extract HTML as text
    } catch (error) {
        console.error('Error fetching HTML:', error);
        throw error; // Propagate the error
    }
}

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

function findFilesByPattern(startPath, filter, callback) {
    if (!fs.existsSync(startPath)) {
        console.log("Directory not found:", startPath);
        return;
    }

    const files = fs.readdirSync(startPath);
    for (let i = 0; i < files.length; i++) {
        const filename = path.join(startPath, files[i]);
        const stat = fs.lstatSync(filename);
        if (stat.isDirectory()) {
            findFilesByPattern(filename, filter, callback); // Recursive call
        } else if (filter.test(filename)) callback(filename);
    }
}

function generateCallHierarchy(filePath) {
    // Specify the output file path
    const outputFilePath = path.join(__dirname, 'call_hierarchy.dot');
    // Ensure the output file is empty
    fs.writeFileSync(outputFilePath, '');
    // Construct the pyan3 command without output redirection
    // Find all Python files in the project directory
    findFilesByPattern('./', /\.py$/, (filename) => {
        console.log('-- found:', filename);
        files.forEach(file => {
            const filePath = path.join(projectPath, file);
            // Construct the pyan3 command
            const command = `pyan3 "${filePath}" --dot`;
            console.log('Executing command: ' + command);
            // Execute the command
            exec(command, { shell: true, env: process.env }, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Error executing pyan3 for ${filePath}: ${error}`);
                    return;
                }
                // Append the output to the file
                fs.appendFileSync(outputFilePath, stdout);
                console.log('file ' + file + ' = ' + stdout);
            });
        });
    });
}
/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Congratulations, your extension "dosc2cli" is now active!');
    // Register the 'readmesimplified.execute' command
    context.subscriptions.push(vscode.commands.registerCommand('readmesimplified.execute', async () => {
        // Your command implementation here.
        vscode.window.showInformationMessage("DOCS2CLI command executed.");
    }));

    // Register the CodeLens provider for all files
    context.subscriptions.push(vscode.languages.registerCodeLensProvider({language: 'python'}, new FunctionCodeLensProvider()));

    // Register the 'extension.runFunction' command
    context.subscriptions.push(vscode.commands.registerCommand('extension.runFunction', function (funcName) {
        vscode.window.showInformationMessage(`Showing call traces for function: ${funcName}`);
    }));  

    let disposable = vscode.commands.registerCommand('extension.generateCallHierarchy', function () {
        // Get the path of the currently active text editor
        let editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage("No active editor found.");
            return;
        }

        let filePath = editor.document.fileName;
        generateCallHierarchy(filePath);
    });

    context.subscriptions.push(disposable);
    // let disposable = vscode.commands.registerCommand('readmesimplified.execute', async () => {
        // Collecting user input
        // const userInput = await vscode.window.showInputBox({
        //     prompt: 'Tell us what you want to install:',
        //     placeHolder: 'Text will be stored here',
        // });
        // if (!userInput) {
        //     return; // Exit if no input is provided
        // }

        // // Fetching HTML content
        // vscode.window.showInformationMessage("Fetching HTML content...");
        // const prompt = 'http://127.0.0.1:7001/prod/' + encodeURIComponent(userInput);
        // let dataOutput;
        // try {
        //     dataOutput = await fetchHtml(prompt);
        // } catch (error) {
        //     console.log('Failed to fetch HTML:', error);
        //     vscode.window.showErrorMessage('Failed to fetch HTML: ' + error.message);
        //     return;
        // }

        // // Writing to text file
        // vscode.window.showInformationMessage("Saving commands to text file...");
        // const textPath = path.join(__dirname, './doc2cli.txt');
        // try {
        //     await fs.promises.writeFile(textPath, dataOutput);
        //     console.log('File was saved!');
        // } catch (err) {
        //     console.error('An error occurred:', err);
        //     vscode.window.showErrorMessage('An error occurred: ' + err.message);
        //     return;
        // }

        // // Opening the text file
        // const filePath = vscode.Uri.file(textPath);
        // await vscode.workspace.openTextDocument(filePath).then(doc => {
        //     vscode.window.showTextDocument(doc);
        // });

        // // Extracting commands
        // vscode.window.showInformationMessage("Ready to execute terminal commands?", "OK").then(async selection => {
        //     if (selection === "OK") {
        //         let splitCommands = dataOutput.split("$: ");
        //         if (splitCommands.length > 1) {
        //             splitCommands.shift(); // Remove the portion before the first occurrence
        //         }
        //         let splitSentences = splitCommands.map(splitCommand => splitCommand.split("\n")[0]);

        //         if (splitCommands.length) {
        //             for (let i = 0; i < splitCommands.length; i++) {
        //                 const confirmation = await vscode.window.showInformationMessage(
        //                     `Execute the command: "${splitSentences[i]}"?`,
        //                     'Yes',
        //                     'No'
        //                 );

        //                 if (confirmation === 'Yes') {
        //                     let customTerminal = vscode.window.createTerminal('readMeSimplified Terminal');
        //                     customTerminal.sendText(splitSentences[i]);
        //                     customTerminal.show();
        //                 }
        //             }
        //         }
        //     }
        // });
    // });

    // context.subscriptions.push(disposable);
}

module.exports = {
    activate,
    deactivate: function() {}
}


