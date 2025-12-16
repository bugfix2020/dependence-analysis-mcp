import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

import {
  Client,
} from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

type AnalysisRequest = {
  directory: string;
  roots?: string[] | null;
  includeExtensions?: string[] | null;
};

type ReferencedFile = { path: string; importCount: number };

type UnusedImport = {
  file: string;
  importSource: string;
  importedNames: string[];
};

type AnalysisResult = {
  referencedFiles: ReferencedFile[];
  unreferencedFiles: string[];
  unusedImports: UnusedImport[];
  __experimentalUnusefulFiles?: string[];
  __experimentalNotice?: string;
  warnings?: string[];
};

type SpawnResult = { code: number | null; signal: NodeJS.Signals | null; stdout: string; stderr: string; error?: string };

function ensureDir(p: string) {
  fs.mkdirSync(p, { recursive: true });
}

function tryGetBundledServerCommand(context: vscode.ExtensionContext): { command: string; args: string[] } | null {
  // Windows onefolder layout:
  //   vscode-extension/bin/dependence-analysis-mcp-win32-x64/dependence-analysis-mcp/dependence-analysis-mcp.exe
  // When packaged, bin is inside extension installation path.
  const folder = path.join(context.extensionPath, 'bin', 'dependence-analysis-mcp-win32-x64', 'dependence-analysis-mcp');
  const exe = path.join(folder, 'dependence-analysis-mcp.exe');
  if (fs.existsSync(exe)) {
    return { command: exe, args: [] };
  }
  return null;
}

function pad2(n: number) {
  return String(n).padStart(2, '0');
}

function formatReportMarkdown(inputDir: string, result: AnalysisResult): string {
  const lines: string[] = [];
  lines.push(`# Dependence Analysis Report`);
  lines.push('');
  lines.push(`- 扫描目录: \`${inputDir}\``);
  lines.push(`- 生成时间: ${new Date().toISOString()}`);
  lines.push('');

  if (result.warnings && result.warnings.length) {
    lines.push('## Warnings');
    for (const w of result.warnings) lines.push(`- ${w}`);
    lines.push('');
  }

  lines.push('## 已引用文件（排除“导入但未使用”）');
  lines.push('');
  lines.push('| 文件 | import 次数 |');
  lines.push('| --- | ---: |');
  for (const rf of result.referencedFiles || []) {
    lines.push(`| \`${rf.path}\` | ${rf.importCount} |`);
  }
  lines.push('');

  lines.push('## 未引用文件');
  lines.push('');
  for (const p of result.unreferencedFiles || []) {
    lines.push(`- \`${p}\``);
  }
  lines.push('');

  lines.push('## 已导入但未使用');
  lines.push('');
  lines.push('| 文件 | importSource | importedNames |');
  lines.push('| --- | --- | --- |');
  for (const u of result.unusedImports || []) {
    lines.push(`| \`${u.file}\` | \`${u.importSource}\` | ${u.importedNames.map(n => `\`${n}\``).join(', ')} |`);
  }
  lines.push('');

  lines.push('## __experimentalUnusefulFiles（实验性）');
  lines.push('');
  lines.push('> 这是一个实验性属性，非常不稳定，仅供参考。');
  if (result.__experimentalNotice) {
    lines.push(`> ${result.__experimentalNotice}`);
  }
  lines.push('');
  for (const p of result.__experimentalUnusefulFiles || []) {
    lines.push(`- \`${p}\``);
  }
  lines.push('');

  lines.push('---');
  lines.push('');
  lines.push('```json');
  lines.push(JSON.stringify(result, null, 2));
  lines.push('```');

  return lines.join('\n');
}

function spawnCapture(command: string, args: string[], env: Record<string, string>): Promise<SpawnResult> {
  return new Promise((resolve) => {
    const child = spawn(command, args, {
      shell: false,
      env,
      windowsHide: true,
    });

    let stdout = '';
    let stderr = '';

    child.stdout?.on('data', (d) => (stdout += String(d)));
    child.stderr?.on('data', (d) => (stderr += String(d)));

    child.on('error', (e: any) => {
      resolve({ code: null, signal: null, stdout, stderr, error: e?.message ?? String(e) });
    });
    child.on('close', (code, signal) => {
      resolve({ code, signal, stdout, stderr });
    });
  });
}

function getCleanEnv(): Record<string, string> {
  return Object.fromEntries(
    Object.entries(process.env).filter(([, v]) => typeof v === 'string') as Array<[string, string]>
  );
}

async function findPythonCommand(env: Record<string, string>): Promise<{ command: string; args: string[] } | null> {
  // Windows: prefer py launcher, then python.
  const candidates: Array<{ command: string; args: string[] }> = process.platform === 'win32'
    ? [
        { command: 'py', args: ['-3'] },
        { command: 'python', args: [] },
      ]
    : [
        { command: 'python3', args: [] },
        { command: 'python', args: [] },
      ];

  for (const c of candidates) {
    const r = await spawnCapture(c.command, [...c.args, '--version'], env);
    if (r.code === 0) return c;
  }
  return null;
}

async function checkMcpCliAvailable(env: Record<string, string>): Promise<boolean> {
  const r = await spawnCapture('dependence-analysis-mcp', ['--help'], env);
  return r.code === 0;
}

async function checkPythonPackageAvailable(python: { command: string; args: string[] }, env: Record<string, string>): Promise<boolean> {
  // Verify the installed Python can import and run our server module.
  // Using -m avoids relying on console_scripts on PATH.
  const r = await spawnCapture(python.command, [...python.args, '-m', 'dependence_analysis_mcp.server', '--help'], env);
  return r.code === 0;
}

async function runTool(directory: string): Promise<AnalysisResult> {
  // NOTE: command is set by caller via global override.
  const transport = new StdioClientTransport({
    command: MCP_SERVER_COMMAND.command,
    args: MCP_SERVER_COMMAND.args,
    env: getCleanEnv(),
  });

  const client = new Client(
    { name: 'dependence-analysis-mcp-vscode', version: '0.0.1' },
    { capabilities: {} }
  );

  await client.connect(transport);
  try {
    const request: AnalysisRequest = {
      directory,
      roots: null,
      includeExtensions: null,
    };

    const resp = await client.callTool({
      name: 'run_dependence_analysis',
      arguments: request,
    });

    // MCP tool returns { content: [...] } in some clients; SDK normalizes as { content }.
    // We expect our Python server returns a JSON dict; SDK exposes it as resp.content[0].text sometimes.
    // Handle both shapes conservatively.
    const anyResp: any = resp as any;
    if (anyResp && typeof anyResp === 'object') {
      if (anyResp.content && Array.isArray(anyResp.content) && anyResp.content.length) {
        const c0 = anyResp.content[0];
        if (c0 && typeof c0 === 'object') {
          if (typeof (c0 as any).text === 'string') {
            return JSON.parse((c0 as any).text) as AnalysisResult;
          }
          if ((c0 as any).type === 'json' && (c0 as any).json) {
            return (c0 as any).json as AnalysisResult;
          }
        }
      }

      if ((anyResp as any).result && typeof (anyResp as any).result === 'object') {
        return (anyResp as any).result as AnalysisResult;
      }
    }

    return anyResp as AnalysisResult;
  } finally {
    await client.close();
  }
}

// Resolved at activation time (bundled exe preferred).
let MCP_SERVER_COMMAND: { command: string; args: string[] } = { command: 'dependence-analysis-mcp', args: [] };

export function activate(context: vscode.ExtensionContext) {
  const output = vscode.window.createOutputChannel('Dependence Analysis');

  const bundled = tryGetBundledServerCommand(context);
  if (bundled) {
    MCP_SERVER_COMMAND = bundled;
    output.appendLine(`Using bundled MCP server: ${bundled.command}`);
  } else {
    MCP_SERVER_COMMAND = { command: 'dependence-analysis-mcp', args: [] };
    output.appendLine('Using MCP server from PATH: dependence-analysis-mcp');
  }

  // Chat participant command for Copilot Chat: /runDependenceAnalysis
  // This will show up in the slash command list under our participant.
  const participant = vscode.chat.createChatParticipant(
    'dependence-analysis-mcp.participant',
    async (request, _chatContext, stream, token) => {
      if (request.command !== 'runDependenceAnalysis') {
        stream.markdown('仅支持命令：`/runDependenceAnalysis`');
        return;
      }

      const pickedFolder = await vscode.window.showOpenDialog({
        canSelectFiles: false,
        canSelectFolders: true,
        canSelectMany: false,
        openLabel: '选择要扫描的目录',
      });
      if (!pickedFolder || !pickedFolder.length) {
        stream.markdown('已取消。');
        return;
      }

      const directory = pickedFolder[0].fsPath;
      stream.markdown(`开始扫描：\`${directory}\``);

      const ws = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!ws) {
        stream.markdown('未打开工作区，无法写入 `.hc/reports`。');
        return;
      }

      const env = getCleanEnv();
      output.show(true);
      output.appendLine('[chat] Checking runtime...');

      // If we have the bundled server, we do not need Python or PATH.
      const hasBundled = !!tryGetBundledServerCommand(context);
      const cliOk = hasBundled ? true : await checkMcpCliAvailable(env);
      if (!cliOk) {
        const py = await findPythonCommand(env);
        if (!py) {
          output.appendLine('[chat] Python not found via `py -3` or `python`.');
          stream.markdown('未检测到 Python（`py -3`/`python` 都无法执行）。请安装 Python 并重启 VS Code 后再试。');
          return;
        }

        const pkgOk = await checkPythonPackageAvailable(py, env);
        if (!pkgOk) {
          const choice = await vscode.window.showWarningMessage(
            '`dependence-analysis-mcp` 未安装（或当前 Python 环境不可用）。是否现在用 pip 安装？',
            '安装',
            '取消'
          );
          if (choice !== '安装') {
            stream.markdown('未安装，已取消。');
            return;
          }

          const term = vscode.window.createTerminal('Dependence Analysis (pip)');
          term.show(true);
          term.sendText(`${py.command} ${[...py.args, '-m', 'pip', 'install', '-U', 'dependence-analysis-mcp'].join(' ')}`);
          stream.markdown('已在终端执行安装命令，安装完成后请重试。');
          return;
        }

        // Package exists but CLI not on PATH.
        output.appendLine('[chat] Python package found, but `dependence-analysis-mcp` not on PATH.');
        stream.markdown('检测到已安装 Python 包，但 `dependence-analysis-mcp` 命令不在 PATH：请重启 VS Code 或修复 PATH。\n\n如果你希望“安装扩展即用（不依赖 Python/PATH）”，请使用带内置 exe 的扩展版本。');
        return;
      }

      let result: AnalysisResult;
      try {
        result = await runTool(directory);
      } catch (e: any) {
        const msg = e?.message ?? String(e);
        stream.markdown(`执行失败：${msg}`);
        return;
      }

      const now = new Date();
      const yyyy = String(now.getFullYear());
      const mm = pad2(now.getMonth() + 1);
      const dd = pad2(now.getDate());
      const time = `${pad2(now.getHours())}${pad2(now.getMinutes())}${pad2(now.getSeconds())}`;
      const reportDir = path.join(ws, '.hc', 'reports', yyyy, mm, dd);
      ensureDir(reportDir);
      const reportPath = path.join(reportDir, `${time}.md`);

      const md = formatReportMarkdown(directory, result);
      fs.writeFileSync(reportPath, md, { encoding: 'utf-8' });

      stream.markdown(`已写入报告：\`${reportPath}\``);
      const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(reportPath));
      await vscode.window.showTextDocument(doc, { preview: true });
    }
  );
  context.subscriptions.push(participant);

  const disposable = vscode.commands.registerCommand(
    'dependenceAnalysis.runDependenceAnalysis',
    async () => {
      const pickedFolder = await vscode.window.showOpenDialog({
        canSelectFiles: false,
        canSelectFolders: true,
        canSelectMany: false,
        openLabel: '选择要扫描的目录',
      });
      if (!pickedFolder || !pickedFolder.length) return;

      const directory = pickedFolder[0].fsPath;

      const env = getCleanEnv();
      output.show(true);
      output.appendLine('Checking runtime...');

      const hasBundled = !!tryGetBundledServerCommand(context);
      const cliOk = hasBundled ? true : await checkMcpCliAvailable(env);
      if (!cliOk) {
        const py = await findPythonCommand(env);
        if (!py) {
          output.appendLine('Python not found via `py -3` or `python`.');
          vscode.window.showErrorMessage('未检测到 Python（`py -3`/`python` 都无法执行）。请安装 Python 并重启 VS Code 后再试。');
          return;
        }

        const pkgOk = await checkPythonPackageAvailable(py, env);
        output.appendLine(`Python: ${py.command} ${py.args.join(' ')} (package ok: ${pkgOk})`);

        if (!pkgOk) {
          const choice = await vscode.window.showWarningMessage(
            '`dependence-analysis-mcp` 未安装（或当前 Python 环境不可用）。是否现在用 pip 安装？',
            '安装',
            '取消'
          );
          if (choice !== '安装') return;

          const term = vscode.window.createTerminal('Dependence Analysis (pip)');
          term.show(true);
          term.sendText(`${py.command} ${[...py.args, '-m', 'pip', 'install', '-U', 'dependence-analysis-mcp'].join(' ')}`);
          vscode.window.showInformationMessage('已在终端执行安装命令，安装完成后请重试。');
          return;
        }

        vscode.window.showErrorMessage('已检测到 Python 包，但 `dependence-analysis-mcp` 命令不在 PATH。请重启 VS Code 或修复 PATH。');
        return;
      }

      output.show(true);
      output.appendLine(`扫描目录: ${directory}`);
      output.appendLine('调用 MCP tool: run_dependence_analysis ...');

      let result: AnalysisResult;
      try {
        result = await runTool(directory);
      } catch (e: any) {
        const msg = e?.message ?? String(e);
        output.appendLine(`失败: ${msg}`);
        vscode.window.showErrorMessage(`Dependence analysis failed: ${msg}`);
        return;
      }

      // write .hc/reports/yyyy/mm/dd/time.md
      const ws = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!ws) {
        vscode.window.showErrorMessage('未打开工作区，无法写入 .hc/reports 目录。');
        return;
      }

      const now = new Date();
      const yyyy = String(now.getFullYear());
      const mm = pad2(now.getMonth() + 1);
      const dd = pad2(now.getDate());
      const time = `${pad2(now.getHours())}${pad2(now.getMinutes())}${pad2(now.getSeconds())}`;

      const reportDir = path.join(ws, '.hc', 'reports', yyyy, mm, dd);
      ensureDir(reportDir);
      const reportPath = path.join(reportDir, `${time}.md`);

      const md = formatReportMarkdown(directory, result);
      fs.writeFileSync(reportPath, md, { encoding: 'utf-8' });

      output.appendLine(`已写入报告: ${reportPath}`);
      const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(reportPath));
      await vscode.window.showTextDocument(doc, { preview: true });
    }
  );

  context.subscriptions.push(disposable, output);
}

export function deactivate() {}
