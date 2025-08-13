const vscode = require("vscode");
const { exec } = require("child_process");

function activate(context) {
  const redHighlight = vscode.window.createTextEditorDecorationType({
    backgroundColor: "rgba(255, 0, 0, 0.3)"
  });

  let disposable = vscode.commands.registerCommand("extension.runSemgrep", () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage("No file open!");
      return;
    }

    vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "Anzen Lite scanning...",
        cancellable: false
      },
      (progress) => {
        return new Promise((resolve) => {
          const filePath = editor.document.uri.fsPath;

          exec(`semgrep --json --quiet --disable-version-check -f auto ${filePath}`, (err, stdout, stderr) => {
            editor.setDecorations(redHighlight, []); // clear old highlights

            if (err && !stdout) {
              vscode.window.showErrorMessage("Error running Semgrep. Make sure it's installed.");
              resolve();
              return;
            }

            try {
              const results = JSON.parse(stdout);

              const decorations = results.results.map(result => {
                const startLine = result.start.line - 1;
                const startCol = result.start.col - 1;
                const endLine = result.end.line - 1;
                const endCol = result.end.col - 1;

                return {
                  range: new vscode.Range(startLine, startCol, endLine, endCol),
                                                      hoverMessage: result.extra.message || "Potential vulnerability"
                };
              });

              editor.setDecorations(redHighlight, decorations);
              vscode.window.showInformationMessage(`Anzen Lite found ${decorations.length} issues.`);
            } catch {
              vscode.window.showErrorMessage("Failed to parse Semgrep output.");
            }

            resolve();
          });
        });
      }
    );
  });

  context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};
