import os
import sys
import json
import signal
import time
from rich.table import Table
from deepdiff import DeepHash

class TimeoutException(Exception):
	pass

class CancelationToken():

	def __init__(self):
		self.__cancel_requested = False
		self.__last_ctrl_c_time = 0
		
	def is_cancelation_requested(self):
		return self.__cancel_requested
	
	def watch(self, iterable):
		if self.is_cancelation_requested():
			return
		for i in iterable:
			if self.is_cancelation_requested():
				break
			yield i
			if self.is_cancelation_requested():
				break
	
	def get_token():
		def __signal_handler_builder(self_obj):
			def __signal_handler(sig, frame):
				current_time = time.time()
				time_since_last = current_time - self_obj.__last_ctrl_c_time
	
				if time_since_last < 0.5:
					sys.exit(1)
				else:
					print("\nCancellation requested. Press ctrl+c twice to kill.")
					self_obj.__cancel_requested = True
					self_obj.__last_ctrl_c_time = current_time
			return __signal_handler

		token = CancelationToken()
		signal.signal(signal.SIGINT, __signal_handler_builder(token))
		return token

def dict_with_tuples_to_json(d):
	temp_dict = {str(k): v for k, v in d.items()}
	return json.dumps(temp_dict)

def json_to_dict(json_string):
	return json.loads(json_string)

def json_to_dict_with_tuples(json_string):
	loaded_dict = json.loads(json_string)
	ret = {eval(k): v for k, v in loaded_dict.items()}
	return ret

def load_secret(input_string):
	heading = "file:"
	if input_string.startswith(heading):
		file_path = input_string[len(heading):]
		if os.path.isfile(file_path):
			try:
				with open(file_path, 'r') as file:
					file_contents = file.read()
				return file_contents
			except IOError as e:
				print(f"Error reading file: {e}", file=sys.stderr)
				sys.exit(1)
		else:
			print(f"File does not exist: {file_path}", file=sys.stderr)
			sys.exit(1)
	else:
		return input_string

def build_table(data: list[dict]):
	all_keys = set()
	for item in data:
		all_keys.update(item.keys())

	all_keys = sorted(all_keys)
	table = Table(*all_keys)
	
	for item in data:
		row = [str(item.get(key, "")) for key in all_keys]
		table.add_row(*row)
		
	return table

def __timeout_handler(signum, frame):
	raise TimeoutException("Operation timed out")

def timer(sub, timeout=None, timeout_handler=None):
	if timeout_handler is None:
		timeout_handler = __timeout_handler
		
	# Set up the timeout only if it's specified and the system is not Windows
	if timeout is not None and os.name != "nt":
		signal.signal(signal.SIGALRM, timeout_handler)
		signal.alarm(timeout)
		
	try:
		start_time = time.time()
		ret = sub()
		end_time = time.time()
		seconds = end_time - start_time
		return ret, seconds
	finally:
		if timeout is not None and os.name != "nt":
			signal.alarm(0)

def round_dict_values(dictionary, precision):
	return {k: round(v, precision) for k, v in dictionary.items()}

def compute_object_hash(obj):
	return DeepHash(obj)[obj]