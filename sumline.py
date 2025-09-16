import os


def count_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0


large_files = []
extensions = ['.py', '.js', '.ts', '.tsx', '.sh']

for root, dirs, files in os.walk('.'):
    # Skip node_modules and other build directories
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', 'venv', '.venv']]

    for file in files:
        if any(file.endswith(ext) for ext in extensions):
            file_path = os.path.join(root, file)
            lines = count_lines(file_path)
            large_files.append((lines, file_path))

# Sort by line count and show all files
large_files.sort(reverse=True)
print('All files sorted by line count:')
for lines, file_path in large_files[:20]:  # Show top 20
    print(f'{lines:4d} lines: {file_path}')

print('\nFiles with more than 600 lines:')
for lines, file_path in large_files:
    if lines > 600:
        print(f'{lines:4d} lines: {file_path}')
