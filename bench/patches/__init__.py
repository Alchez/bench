from difflib import unified_diff
from importlib import import_module
from pathlib import Path
from shutil import copyfile


def run(bench_path):
	print('\nRunning bench patches...')
	# get patch file paths
	source_file, target_file = get_patch_files(bench_path)

	# get the new bench patches that need to be run
	source_data = source_file.read_text().splitlines()
	target_data = target_file.read_text().splitlines()

	executed_patches = list(filter(None, target_data))
	new_patches = list(unified_diff(source_data, target_data, n=0))

	if not new_patches:
		print('...already executed')
		return

	# go through and run each new patch
	try:
		for line in new_patches:
			# ignore diff descriptions, skipped patches and empty lines
			for prefix in ('---', '+++', '@@', '-#'):
				if line.startswith(prefix) or not line[1:].strip():
					break
			else:
				patch = line[1:].strip().split()[0]
				module = import_module(patch)
				execute = getattr(module, 'execute')
				result = execute(bench_path)

				if result is not False:
					executed_patches.append(patch)
	finally:
		target_file.write_text('\n'.join(executed_patches))
	print('...done')


def set_all_patches_executed(bench_path):
	source_file, target_file = get_patch_files(bench_path)
	copyfile(source_file, target_file)


def get_patch_files(bench_path):
	CURRENT_DIR = Path(__file__).resolve().parent
	PATCH_DIR = Path(bench_path)

	source_file = CURRENT_DIR.joinpath("patches.txt")
	target_file = PATCH_DIR.joinpath("patches.txt")

	if not source_file.exists():
		source_file.touch()

	if not target_file.exists():
		target_file.touch()

	return source_file, target_file
