"""Quick test script for interactive mode."""
import subprocess
import sys

# Test commands to execute
commands = [
    'add "Buy groceries"',
    'add "Call dentist" -d "Schedule checkup"',
    'add "Read Python book"',
    'list',
    'help',
    'exit',
]

# Join commands with newlines
input_data = '\n'.join(commands)

# Run the interactive CLI with piped input
process = subprocess.Popen(
    [sys.executable, '-m', 'src.cli.main'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

stdout, stderr = process.communicate(input=input_data)

print("=== STDOUT ===")
print(stdout)

if stderr:
    print("\n=== STDERR ===")
    print(stderr)

print(f"\n=== EXIT CODE: {process.returncode} ===")
