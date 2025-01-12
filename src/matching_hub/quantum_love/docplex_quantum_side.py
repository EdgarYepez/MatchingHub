# Codebase from https://github.com/sdbs-uni-p/quantum_love

from docplex.mp.model import Model


def search_pairs(man, woman, pairs):
	"""
		Finds the specific pair (man, woman) in the pairs list.

		:param man: The man that should appear in the pair.
		:param woman: The woman that should appear in the pair.
		:param pairs: The pairs list with all the possible pairs.
		:return: The pair (man, woman) of the pairs list.
		"""
	for p in pairs:
		if p.m == man and p.w == woman:
			return p
	return None


def does_prefer(person, prefer_more, prefer_less):
	"""
	Checks whether a person prefers person1(prefer_more) over person2(prefer_less).

	:param person: The person whose preference list gets checked.
	:param prefer_more: The person that should get preferred.
	:param prefer_less: The person that should not get preferred.
	:return: True if person1(prefer_more) gets preferred, False otherwise.
	"""
	person1 = prefer_more[0]
	person2 = prefer_less[0]

	if person1 == person2:
		return False
	else:
		preferences = person[1]
		for preference in preferences:
			if type(preference).__name__ == 'list':
				if person1 in preference:
					if person2 not in preference:
						return True
					else:
						return False
				elif person2 in preference:
					return False
			else:  # if type(preference).__name__ == 'str'
				if preference == person1:
					return True
				elif preference == person2:
					return False
		return False


def do_appear_in_each_others_preference_lists(person1, person2):
	"""
	Checks if person1 appears in person2's preference list and the other way round.

	:param person1: The first person that should appear in person2's preference list.
	:param person2: The second person that should appear in person1's preference list.
	:return: True if they appear in each other's preference list, False otherwise.
	"""
	person1_name = person1[0]
	person2_name = person2[0]
	preferences_of_person1 = person1[1]
	preferences_of_person2 = person2[1]
	person1_appeared = False
	person2_appeared = False

	for preference in preferences_of_person1:
		if type(preference).__name__ == 'list':
			if person2_name in preference:
				person2_appeared = True
				break
		else:
			if preference == person2_name:
				person2_appeared = True
				break
	if not person2_appeared:
		return False

	for preference in preferences_of_person2:
		if type(preference).__name__ == 'list':
			if person1_name in preference:
				person1_appeared = True
				break
		else:
			if preference == person1_name:
				person1_appeared = True
				break
	if not person1_appeared:
		return False

	return True


def compute_twice_constraint(p3, pairs):
	"""
	Computes the twice constraint that "noone gets matched more than once in the final solution".
	As soon as a candidate appears in two pairs in the final solution, he is matched twice.

	:param p3: The penalty for the twice constraint.
	:param pairs: The possible pairs.
	:return: The computed twice constraint.
	"""
	twice_constraint = 0
	existing_pairs_in_twice_constraint = list()
	for i in range(len(pairs)):
		for j in range(len(pairs)):
			pair1 = pairs[i]
			pair2 = pairs[j]

			if i != j:  # pairs not equal
				if pair1.m == pair2.m or pair1.w == pair2.w:  # man matched twice or woman matched twice
					if not (((pair1.m, pair1.w, pair2.m, pair2.w) in existing_pairs_in_twice_constraint)
							or ((pair2.m, pair2.w, pair1.m, pair1.w) in existing_pairs_in_twice_constraint)):
						twice_constraint += p3 * pairs[i] * pairs[j]
						existing_pairs_in_twice_constraint.append((pair1.m, pair1.w, pair2.m, pair2.w))
	return twice_constraint


def compute_stable_constraint(p2, pairs, possible_men, possible_women):
	"""
	Computes the stable constraint of the Stable Marriage Problem.
	A pair is blocking as soon as both partners would prefer another partner over their current one.

	:param p2: The penalty for the stable constraint.
	:param pairs: The possible pairs.
	:param possible_men: All possible men.
	:param possible_women: All possible women.
	:return: The computed stable constraint.
	"""
	stable_constraint = 0

	for k in range(len(pairs)):
		stableConstraint_blockingPair = 0
		stableConstraint_stablePair = 0
		fixed_man = pairs[k].m
		fixed_woman = pairs[k].w

		# Punishes pairs that are blocking
		for i in range(len(possible_men)):
			variable_man = possible_men[i]
			for j in range(len(possible_women)):
				variable_woman = possible_women[j]
				if do_appear_in_each_others_preference_lists(fixed_man, variable_woman) \
						and do_appear_in_each_others_preference_lists(variable_man, fixed_woman):
					if not does_prefer(fixed_man, fixed_woman, variable_woman) \
							or not does_prefer(fixed_woman, fixed_man, variable_man):
						boolean_value = 1
					else:
						boolean_value = 0
					pair1 = search_pairs(fixed_man, variable_woman, pairs)
					pair2 = search_pairs(variable_man, fixed_woman, pairs)
					if pair1 is not None and pair2 is not None:
						stableConstraint_blockingPair += pair1 * pair2 * boolean_value
					else:
						pass

		# Promotes pairs that are most likely not blocking
		for n in range(len(possible_men)):
			variable_man = possible_men[n]
			if do_appear_in_each_others_preference_lists(fixed_woman, variable_man):
				if not does_prefer(fixed_woman, fixed_man, variable_man):
					boolean_value = 1
				else:
					boolean_value = 0
				pair3 = search_pairs(variable_man, fixed_woman, pairs)
				if pair3 is not None:
					stableConstraint_stablePair += pair3 * boolean_value
				else:
					pass

		# Promotes pairs that are most likely not blocking
		for m in range(len(possible_women)):
			variable_woman = possible_women[m]
			if do_appear_in_each_others_preference_lists(fixed_man, variable_woman):
				if not does_prefer(fixed_man, fixed_woman, variable_woman):
					boolean_value = 1
				else:
					boolean_value = 0
				pair4 = search_pairs(fixed_man, variable_woman, pairs)
				if pair4 is not None:
					stableConstraint_stablePair += pair4 * boolean_value
				else:
					pass

		stable_constraint += p2 * (stableConstraint_blockingPair - stableConstraint_stablePair)

	return stable_constraint


def compute_objective_function(p1, pairs):
	"""
	Computes the objective function "find the maximum pairs" of the Stable Marriage Problem.

	:param p1: The penalty for the objective function.
	:param pairs: The possible pairs.
	:return: The computed objective function.
	"""
	objective_function = 0
	for i in range(len(pairs)):
		objective_function += pairs[i]
	objective_function = -p1 * objective_function
	return objective_function


def setup_docplex_model(possible_pairs, penalties):
	"""
	Creates a corresponding Stable Marriage QUBO model shown as a minimizing docplex model.

	:param possible_pairs: The pairs that will act as variables in the QUBO formula.
	:param penalties: The set penalties. If no penalties are chosen, the default ones get used.
	:return: The docplex Stable Marriage QUBO model.
	"""
	model = Model("Stable Marriage Problem")
	pairs = model.binary_var_list([(x[0][0], x[1][0]) for x in possible_pairs], 0, 1, "")
	#pairs = model.binary_var_list([chr(97 + i) for i in range(len(possible_pairs))], 0, 1, "")

	possible_men = []
	possible_women = []

	for k in range(len(pairs)):
		man = possible_pairs[k][0]
		woman = possible_pairs[k][1]
		pairs[k].m = man
		pairs[k].w = woman

		if man not in possible_men:
			possible_men.append(man)
		if woman not in possible_women:
			possible_women.append(woman)

	# Setup penalties
	if penalties is None:
		p1 = 1
		p2 = min(len(possible_men), len(possible_women))
		p3 = p2 * p2 + p1
	else:
		p1 = penalties[0]
		p2 = penalties[1]
		p3 = penalties[2]

	# Compute objective function and constraints
	twice_constraint = compute_twice_constraint(p3, pairs)
	stable_constraint = compute_stable_constraint(p2, pairs, possible_men, possible_women)
	objective_function = compute_objective_function(p1, pairs)

	model.minimize(objective_function + twice_constraint + stable_constraint)

	return model
