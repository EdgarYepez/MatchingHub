# Codebase from https://github.com/sdbs-uni-p/quantum_love
# Changes to the original code are appropriately marked

def get_preference_value(preference):
	return preference[1]


def get_correct_preferences_as_tuples(possible_persons):
	"""
	Create the correct preference lists for the inputted persons.

	:param possible_persons: The possible men or women.
	:return: The inputted persons with their preferences.
	"""
	possible_persons_with_preferences = []
	for possible_person in possible_persons:
		tuple_name = possible_person[0]
		possible_person_tuple = ()
		tuple_preferences = ()

		# The person has multiple different matches with different values in the other table
		if len(possible_person[1]) > 1:
			for preference in possible_person[1]:
				preferences = preference[0]
				if len(preferences) > 1:  # The match has two or more equally likely matches in the other table
					if tuple_preferences == ():
						tuple_preferences = (preferences,)
					else:
						tuple_preferences = tuple_preferences + (preferences,)
				else:  # The match has only one equally likely match in the other table
					tuple_preferences = tuple_preferences + tuple(preferences)
			possible_person_tuple = (tuple_name, tuple_preferences)
		elif len(possible_person[1]) == 1:  # The man has only one possible match
			preferences = possible_person[1][0][0]
			if len(preferences) > 1:  # The match has two or more equally likely matches in the other table
				possible_person_tuple = (tuple_name, (preferences,))
			else:  # The match has only one equally likely match in the other table
				possible_person_tuple = (tuple_name, (preferences[0],))

		if possible_person_tuple != ():
			possible_persons_with_preferences.append(possible_person_tuple)

	return possible_persons_with_preferences


def get_possible_pairs_as_tuples(possible_men_with_preferences, possible_women_with_preferences):
	"""
	Reformulate the possible pairs with preferences as tuples by comparing the possible men with preferences
	with the possible women with preferences and finding correspondences i.e. that the man and the woman appear in each
	other's preference list.

	:param possible_men_with_preferences: The possible mens with their preferences.
	:param possible_women_with_preferences: The possible women with their preferences.
	:return: The possible pairs with preferences as tuples.
	"""
	possible_pairs_with_preferences = []
	for possible_man_with_preferences in possible_men_with_preferences:
		for possible_woman_with_preferences in possible_women_with_preferences:
			woman_appears_in_man = False
			man_appears_in_woman = False

			man_prefs = possible_man_with_preferences[1]
			for man_pref in man_prefs:
				woman_to_be_matched = possible_woman_with_preferences[0]
				if isinstance(man_pref, list):
					if woman_to_be_matched in man_pref:
						woman_appears_in_man = True
						break
				else:
					if woman_to_be_matched == man_pref:
						woman_appears_in_man = True
						break

			if woman_appears_in_man:
				woman_prefs = possible_woman_with_preferences[1]
				for woman_pref in woman_prefs:
					man_to_be_matched = possible_man_with_preferences[0]
					if isinstance(woman_pref, list):
						if man_to_be_matched in woman_pref:
							man_appears_in_woman = True
							break
					else:
						if man_to_be_matched == woman_pref:
							man_appears_in_woman = True
							break

			if woman_appears_in_man and man_appears_in_woman:
				pair = (possible_man_with_preferences, possible_woman_with_preferences)
				possible_pairs_with_preferences.append(pair)

	return possible_pairs_with_preferences


def add_preferences(matches, schema1, schema2, possible_men, possible_women):
	"""
	Creates the preference lists of the men and women.

	:param matches: The valentine schema matches.
	:param schema1: The first schema to get matched.
	:param schema2: The second schema to get matched.
	:param possible_men: The candidates of the first schema.
	:param possible_women: The candidates of the second schema.
	"""
	def _a(schm1, schm2, temp_possible_men, temp_possible_women):
		for column in schm1.columns.values:
			temp_possible_men.append((column, list()))
		for column in schm2.columns.values:
			temp_possible_women.append((column, list()))

		items = list(matches.items())
		for item in items:
			name_of_table_1 = item[0][0][1]
			name_of_table_2 = item[0][1][1]
			value = item[1]
			man = None
			woman = None

			# Find corresponding man and woman
			for possible_man in temp_possible_men:
				if possible_man[0] == name_of_table_1:
					man = possible_man
					break
			for possible_woman in temp_possible_women:
				if possible_woman[0] == name_of_table_2:
					woman = possible_woman
					break

			# Add preferences
			preference_list_man = list()
			preference_list_man.append(name_of_table_2)
			preference_list_woman = list()
			preference_list_woman.append(name_of_table_1)
			if not man is None:
				man[1].append((preference_list_man, value))
			if not woman is None:
				woman[1].append((preference_list_woman, value))

	# CHANGED FROM THE ORIGINAL CODEBASE
	# The _a method determines preference lists for a set of matches that are symmetric,
	# where target preferences are derived from source preferences. This approach does not support
	# cases with asymmetric preferences, where target preferences are independent of source preferences.
	# To support both cases, the input `matches` must be a union of preferences from both source and target.
	_a(schema1, schema2, possible_men, []) # The [] discards inferred target preferences from the source
	_a(schema2, schema1, possible_women, [])
	#_a(schema1, schema2, possible_men, possible_women) # To enable original behaviour, `matches` must only be source preferences;
	# comment the above lines and uncomment this one


def cleanup_preferences(person):
	"""
	Removes duplicates and sums equal likeliness in the preference list of the person.

	:param person: The person whose preference list should get polished.
	"""
	preferences = person[1]
	prev_reference = None
	length = len(preferences)
	i = 0
	while i < length:
		preference = preferences.__getitem__(i)

		if preferences.count(preference) > 1:  # Remove duplicates
			preferences.remove(preference)
			length = length - 1
			i = i + 1
			continue

		elif prev_reference is not None and preference[1] == prev_reference[1]:  # Sum equal likeliness
			prev_reference[0].extend(preference[0])
			preferences.remove(preference)
			length = length - 1
			continue
		prev_reference = preference
		i = i + 1

	preferences.sort(reverse=True, key=get_preference_value)


def get_pairs_and_men_and_women_with_preferences(matches, schema1, schema2):
	"""
	Converts the database schemas to suitable input for the quantum side.

	:param matches: The possible matches that the valentine schema matcher has found.
	:param schema1: The first inputted schema.
	:param schema2: the second inputted schema.
	:return: The converted pairs, men and women.
	"""
	possible_men = list()
	possible_women = list()

	add_preferences(matches, schema1, schema2, possible_men, possible_women)

	# Sort preferences in men and women, remove duplicates, sum equal likeliness
	for man in possible_men:
		cleanup_preferences(man)
	for woman in possible_women:
		cleanup_preferences(woman)

	# Replace lists with final preference tuples
	possible_men_with_preferences = get_correct_preferences_as_tuples(possible_men)
	possible_women_with_preferences = get_correct_preferences_as_tuples(possible_women)
	possible_pairs_with_preferences = get_possible_pairs_as_tuples(possible_men_with_preferences,
																   possible_women_with_preferences)

	return possible_pairs_with_preferences, possible_men_with_preferences, possible_women_with_preferences
