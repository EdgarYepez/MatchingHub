from deepdiff import DeepDiff

def extract_elements(pref):
	source_elements = set()
	target_elements = set()
	
	for (source, target) in pref.keys():
		source_elements.add(source[1])
		target_elements.add(target[1])
	
	return source_elements, target_elements

def translate_probabilities_to_levels(prob_dict):
	level_dict = {}
	grouped_probabilities = {}
	for key, prob in prob_dict.items():
		row = key[0][1]
		if row not in grouped_probabilities:
			grouped_probabilities[row] = []
		grouped_probabilities[row].append((key, prob))

	for row, key_prob_list in grouped_probabilities.items():
		sorted_key_prob_list = sorted(key_prob_list, key=lambda x: x[1], reverse=False)

		current_level = 1
		prev_prob = None
		for (key, prob) in sorted_key_prob_list:
			if prev_prob is not None and prob != prev_prob:
				current_level += 1
			level_dict[key] = current_level
			prev_prob = prob

	return level_dict

def build_preference_lists(matches):
	preferences_of_source = { }
	preferences_of_target = { }
	for m in matches:
		source_field_name = m[0][1]
		target_field_name = m[1][1]
		score = matches[m]
		if not source_field_name in preferences_of_source:
			preferences_of_source[source_field_name] = [ ]
		preferences_of_source[source_field_name].append((target_field_name, score))
		if not target_field_name in preferences_of_target:
			preferences_of_target[target_field_name] = [ ]
		preferences_of_target[target_field_name].append((source_field_name, score))
	return preferences_of_source, preferences_of_target

def check_is_symmetric(pref_of_source, infer_pref_of_source, pref_of_target, infer_pref_of_target):
	"""
	Checks whether the preference lists for both source and target are identical 
	to their corresponding inferred preference lists.
	"""
	eq_1 = DeepDiff(pref_of_source, infer_pref_of_source)
	eq_2 = DeepDiff(pref_of_target, infer_pref_of_target)
	return len(eq_1) == 0 and len(eq_2) == 0

def check_is_complete(pref_of_source, pref_of_target):
	"""
	Determines whether the preference lists are complete.
	A complete preference list requires that each element
	of the source ranks all elements of the target, and also
	each element of the target ranks all elements of the source.
	"""
	def __complete_lists(ref, lists):
		ref_set = set(ref)
		for l in lists:
			l_set = set(map(lambda m: m[0], l))
			if l_set != ref_set or len(ref) != len(l):
				return False
		return True
	return __complete_lists(list(pref_of_source.keys()), list(pref_of_target.values())) and \
		__complete_lists(list(pref_of_target.keys()), list(pref_of_source.values()))

def check_has_ties(pref):
	"""
	Checks whether the preference list contains ties.
	"""
	def __has_ties(lists):
		for l in lists:
			scores = { }
			for m in l:
				if not m[1] in scores:
					scores[m[1]] = set()
				scores[m[1]].add(m[0])
				if len(scores[m[1]]) > 1:
					return True
		return False
	return __has_ties(list(pref.values()))

def check_is_balanced(pref_of_source, pref_of_target):
	"""
	Checks whether the preference lists are balanced.
	A balanced preference list requires that source and target have the same 
	number of elements, and that neither source nor target ranks any unknown 
	or foreign elements.
	"""
	def __balanced_lists(ref, lists):
		ref_set = set(ref)
		for l in lists:
			l_set = set(map(lambda m: m[0], l))
			if not l_set.issubset(ref_set):
				return False
		return True
	return len(pref_of_source) == len(pref_of_target) and \
		__balanced_lists(list(pref_of_source.keys()), list(pref_of_target.values())) and \
		__balanced_lists(list(pref_of_target.keys()), list(pref_of_source.values()))
