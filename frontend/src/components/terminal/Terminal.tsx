import { useEffect, useRef } from 'react';
import { Terminal as XTerm } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

interface TerminalProps {
  onCommand?: (command: string) => void;
  readOnly?: boolean;
}

export default function Terminal({ onCommand, readOnly = false }: TerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const currentLineRef = useRef<string>('');

  useEffect(() => {
    if (!terminalRef.current) return;

    // Create terminal instance
    const term = new XTerm({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'JetBrains Mono, Fira Code, monospace',
      theme: {
        background: '#000000',
        foreground: '#00ff00',
        cursor: '#00ffff',
        cursorAccent: '#000000',
        selectionBackground: '#00ffff33',
        black: '#000000',
        red: '#ff0055',
        green: '#00ff00',
        yellow: '#ffff00',
        blue: '#00ffff',
        magenta: '#a855f7',
        cyan: '#00ffff',
        white: '#e0e0e0',
        brightBlack: '#606060',
        brightRed: '#ff0055',
        brightGreen: '#00ff00',
        brightYellow: '#ffff00',
        brightBlue: '#00ffff',
        brightMagenta: '#a855f7',
        brightCyan: '#00ffff',
        brightWhite: '#ffffff',
      },
    });

    // Create fit addon
    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);

    // Open terminal
    term.open(terminalRef.current);
    fitAddon.fit();

    // Store refs
    xtermRef.current = term;
    fitAddonRef.current = fitAddon;

    // Welcome message
    term.writeln('\x1b[1;36m╔════════════════════════════════════════╗\x1b[0m');
    term.writeln('\x1b[1;36m║       GIT QUEST TERMINAL v1.0.0       ║\x1b[0m');
    term.writeln('\x1b[1;36m╚════════════════════════════════════════╝\x1b[0m');
    term.writeln('');
    term.writeln('\x1b[32mWelcome to the Git Quest interactive terminal!\x1b[0m');
    term.writeln('\x1b[90mType \x1b[36mgit --help\x1b[90m to see available commands.\x1b[0m');
    term.writeln('');
    writePrompt(term);

    if (!readOnly) {
      // Handle user input
      term.onData((data) => {
        const code = data.charCodeAt(0);

        // Handle Enter
        if (code === 13) {
          term.write('\r\n');
          const command = currentLineRef.current.trim();

          if (command) {
            handleCommand(term, command);
            if (onCommand) {
              onCommand(command);
            }
          }

          currentLineRef.current = '';
          writePrompt(term);
        }
        // Handle Backspace
        else if (code === 127) {
          if (currentLineRef.current.length > 0) {
            currentLineRef.current = currentLineRef.current.slice(0, -1);
            term.write('\b \b');
          }
        }
        // Handle Ctrl+C
        else if (code === 3) {
          term.write('^C\r\n');
          currentLineRef.current = '';
          writePrompt(term);
        }
        // Handle printable characters
        else if (code >= 32 && code < 127) {
          currentLineRef.current += data;
          term.write(data);
        }
      });
    }

    // Handle window resize
    const handleResize = () => {
      fitAddon.fit();
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      term.dispose();
    };
  }, [readOnly, onCommand]);

  const writePrompt = (term: XTerm) => {
    term.write('\x1b[36mgitquest\x1b[0m:\x1b[35m~\x1b[0m$ ');
  };

  const handleCommand = (term: XTerm, command: string) => {
    const [cmd, ...args] = command.split(' ');

    // Mock Git command responses
    switch (cmd) {
      case 'git':
        handleGitCommand(term, args);
        break;
      case 'clear':
        term.clear();
        break;
      case 'help':
        term.writeln('\x1b[32mAvailable commands:\x1b[0m');
        term.writeln('  \x1b[36mgit\x1b[0m         - Git version control');
        term.writeln('  \x1b[36mclear\x1b[0m       - Clear terminal');
        term.writeln('  \x1b[36mhelp\x1b[0m        - Show this help');
        term.writeln('');
        break;
      default:
        term.writeln(`\x1b[31mCommand not found: ${cmd}\x1b[0m`);
        term.writeln(`Type \x1b[36mhelp\x1b[0m for available commands.`);
        term.writeln('');
    }
  };

  const handleGitCommand = (term: XTerm, args: string[]) => {
    if (args.length === 0) {
      term.writeln('\x1b[33musage: git <command> [<args>]\x1b[0m');
      term.writeln('');
      term.writeln('Common Git commands:');
      term.writeln('  \x1b[32minit\x1b[0m        Initialize a repository');
      term.writeln('  \x1b[32mstatus\x1b[0m      Show working tree status');
      term.writeln('  \x1b[32madd\x1b[0m         Add file contents to index');
      term.writeln('  \x1b[32mcommit\x1b[0m      Record changes to repository');
      term.writeln('  \x1b[32mlog\x1b[0m         Show commit logs');
      term.writeln('  \x1b[32mbranch\x1b[0m      List, create, or delete branches');
      term.writeln('  \x1b[32mcheckout\x1b[0m    Switch branches or restore files');
      term.writeln('');
      return;
    }

    const subcommand = args[0];

    switch (subcommand) {
      case '--help':
      case '-h':
        handleGitCommand(term, []);
        break;
      case 'init':
        term.writeln('\x1b[32mInitialized empty Git repository in /gitquest/.git/\x1b[0m');
        term.writeln('');
        break;
      case 'status':
        term.writeln('On branch \x1b[36mmain\x1b[0m');
        term.writeln('');
        term.writeln('No commits yet');
        term.writeln('');
        term.writeln('nothing to commit (create/copy files and use "git add" to track)');
        term.writeln('');
        break;
      case 'add':
        if (args.length < 2) {
          term.writeln('\x1b[31mNothing specified, nothing added.\x1b[0m');
        } else {
          term.writeln(`\x1b[32mAdded ${args.slice(1).join(' ')}\x1b[0m`);
        }
        term.writeln('');
        break;
      case 'commit':
        if (args.includes('-m')) {
          term.writeln('\x1b[36m[main 1a2b3c4]\x1b[0m Commit message');
          term.writeln('\x1b[32m 1 file changed, 1 insertion(+)\x1b[0m');
        } else {
          term.writeln('\x1b[31mAbort commit due to empty commit message.\x1b[0m');
        }
        term.writeln('');
        break;
      case 'log':
        term.writeln('\x1b[33mcommit 1a2b3c4d5e6f7g8h9i0j\x1b[0m (\x1b[36mHEAD -> main\x1b[0m)');
        term.writeln('Author: Git Quest Player <player@gitquest.com>');
        term.writeln('Date:   ' + new Date().toDateString());
        term.writeln('');
        term.writeln('    Initial commit');
        term.writeln('');
        break;
      case 'branch':
        term.writeln('* \x1b[32mmain\x1b[0m');
        term.writeln('');
        break;
      default:
        term.writeln(`\x1b[31mgit: '${subcommand}' is not a git command. See 'git --help'.\x1b[0m`);
        term.writeln('');
    }
  };

  return (
    <div className="w-full h-full bg-cyber-black border border-neon-green/30 rounded-lg overflow-hidden">
      <div
        ref={terminalRef}
        className="w-full h-full p-4"
        style={{ minHeight: '400px' }}
      />
    </div>
  );
}
