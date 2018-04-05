import json
import argparse
from urlparse import urlparse
import phonenumbers
import gzip
import os
import itertools

def parse_line_into_quad(line):
	answer = dict()
	l = line.split("<")
	new_data = ""
	cur_idx = 0
	for cur_idx in range(len(l)):
		if l[cur_idx] == "":
			continue
		if l[cur_idx] == " .":
			new_data = new_data + " ."
		if len(l[cur_idx]) < 2:
			continue
		if l[cur_idx][-2] != ">" and l[cur_idx][-1] != ">":
			sub_comps = l[cur_idx].split(">")
			if len(sub_comps) > 1:
				if sub_comps[1] == " .":
					new_data = new_data + "<" + sub_comps[0] + "> ."
				else:
					new_data = new_data + "<" + sub_comps[0] + "> <" + sub_comps[1] + "> "
			else:
				new_data = new_data + "<" + sub_comps[0] + "> "
		else:
			new_data = new_data + "<" + l[cur_idx]

	new_l = new_data.split("<")
	if len(new_l) < 4:
		return None
	answer['subject'] = new_l[1].split(">")[0].replace(" ", "")
	answer['predicate'] = new_l[2].split(">")[0]
	answer['object'] = new_l[3].split(">")[0]
	graph_url = new_l[4].split(">")[0]
	answer['graph'] = urlparse(graph_url).netloc
	if 'subject' not in answer:
		return None
	else:
		return answer

def parse_data(line, identifier):
	is_applicable = False
	answer = parse_line_into_quad(line)
	# identifier
	if identifier in answer['predicate'].lower():
		answer['object'] = identifier_normalizer(answer['object'])
	else:
		answer['object'] = answer['object'].strip()
	return answer

def build_graph(schema_types, identifier, properties, property_types, f, result_path, blank_node_list, num_query = 1000):
	# schema_types = [u'http://schema.org/ElementarySchool', 
					  # u'http://schema.org/Preschool', 
					  # u'http://schema.org/HighSchool', 
					  # 'http://schema.org/EducationalOrganization', 
					  # u'http://schema.org/CollegeOrUniversity', 
					  # u'http://schema.org/School', 
					  # u'http://schema.org/MiddleSchool']
	# identifier = 'telephone'
	# properties = ['name', 'address', 'email']
	# property_types = [u'http://schema.org/PostalAddress']
	q_idx = 0
	data_dict = {}
	property_dict = {}
	duplicate_dict = {}
	prop1 = properties[0]
	prop2 = properties[1]
	prop3 = properties[2]
	prop1s = []
	prop2s = []
	prop3s = []
	idens = []
	for st in schema_types:
		prop1s.append(st+"/"+prop1)
		prop2s.append(st+"/"+prop2)
		prop3s.append(st+"/"+prop3)
		idens.append(st+"/"+identifier)
	for line in f:
		q = line.strip()
		q_idx += 1
		is_applicable = False
		for schema_type in schema_types:
			if schema_type in line:
				is_applicable = True
				break
		for p in properties:
			if p in line:
				is_applicable = True
				break
		for pt in property_types:
			if pt in line:
				is_applicable = True
				break
		if not is_applicable:
			continue
		answer = parse_data(line, identifier)
		if answer['object'] in schema_types:
			if any(answer['subject'] in sublist for sublist in blank_node_list):
				if answer['subject'] not in duplicate_dict.keys():
					duplicate_dict[answer['subject']] = {}
					duplicate_dict[answer['subject']]['type'] = answer['object'].split("http://schema.org/")[1]
					duplicate_dict[answer['subject']]['pld'] = answer['graph']
					for dup_index in range(len(blank_node_list)):
						if answer['subject'] in blank_node_list[dup_index]:
							duplicate_dict[answer['subject']]['batch'] = dup_index
				continue
			data_dict[answer['subject']] = {}
			data_dict[answer['subject']]['type'] = answer['object'].split("http://schema.org/")[1]
			data_dict[answer['subject']]['prop1'] = ""
			data_dict[answer['subject']]['prop2'] = ""
			data_dict[answer['subject']]['prop3'] = ""
			data_dict[answer['subject']]['id'] = []
			data_dict[answer['subject']]['pld'] = answer['graph']
		elif answer['predicate'] in idens:
		# elif identifier in answer['predicate']:
			#TODO: assuming that blank node is defined with its type first
			if any(answer['subject'] in sublist for sublist in blank_node_list):
				if answer['subject'] not in duplicate_dict.keys():
					duplicate_dict[answer['subject']] = {}
				duplicate_dict[answer['subject']]['id'] = answer['object']
				continue
			if answer['subject'] in data_dict.keys():
				data_dict[answer['subject']]['id'].extend(answer['object'])
			else:
				print "identifier"
				print data_dict
				print answer
		# elif prop1 in answer['predicate']:
		elif answer['predicate'] in prop1s:
			#TODO: assuming that blank node is defined with its type first
			if any(answer['subject'] in sublist for sublist in blank_node_list):
				if answer['subject'] not in duplicate_dict.keys():
					duplicate_dict[answer['subject']] = {}
				duplicate_dict[answer['subject']]['prop1'] = answer['object'].strip()
				continue
			if answer['subject'] in data_dict.keys():
				if "http://schema.org/" + data_dict[answer['subject']]['type']+"/"+prop1 != answer['predicate']:
					print "prop1 diff"
					print answer['predicate']
					print "http://schema.org/" + data_dict[answer['subject']]['type']+"/"+prop1
				data_dict[answer['subject']]['prop1'] = answer['object']
			else:
				print "prop1"
				print answer
		elif answer['predicate'] in prop2s:
		# elif prop2 in answer['predicate']:
			#TODO: assuming that blank node is defined with its type first
			if any(answer['subject'] in sublist for sublist in blank_node_list):
				if answer['subject'] not in duplicate_dict.keys():
					duplicate_dict[answer['subject']] = {}
				duplicate_dict[answer['subject']]['prop2'] = answer['object'].strip()
				continue
			if answer['subject'] in data_dict.keys():
				if "http://schema.org/" + data_dict[answer['subject']]['type']+"/"+prop2 != answer['predicate']:
					print "prop2 diff"
					print answer['predicate']
					print "http://schema.org/" + data_dict[answer['subject']]['type']+"/"+prop2
				data_dict[answer['subject']]['prop2'] = answer['object']
			else:
				print "prop2"
				print answer
		elif answer['predicate'] in prop3s:
		# elif prop3 in answer['predicate']:
			#TODO: assuming that blank node is defined with its type first
			if any(answer['subject'] in sublist for sublist in blank_node_list):
				if answer['subject'] not in duplicate_dict.keys():
					duplicate_dict[answer['subject']] = {}
				duplicate_dict[answer['subject']]['prop3'] = answer['object'].strip()
				continue
			if answer['subject'] in data_dict.keys():
				if "http://schema.org/" + data_dict[answer['subject']]['type']+"/"+prop3 != answer['predicate']:
					print "prop3 diff"
					print answer['predicate']
					print "http://schema.org/" + data_dict[answer['subject']]['type']+"/"+prop3
				data_dict[answer['subject']]['prop3'] = answer['object']
			else:
				print "prop3"
				print answer
			
		elif answer['object'] in property_types:
			property_dict[answer['subject']] = {}
			property_dict[answer['subject']]['type'] = answer['object'].split("http://schema.org/")[1]
		for pt in property_types:
			if pt in answer['predicate']:
				if pt+"/" not in answer["predicate"]:
					print answer["predicate"]
				else:
					prop_name = answer['predicate'].split(pt+"/")[1]
					if answer['subject'] not in property_dict.keys():
						property_dict[answer['subject']] = {}
					property_dict[answer['subject']][prop_name] = answer['object']
		if q_idx > num_query:
			for k in data_dict.keys():
				data_dict[k]['id'] = list(set(data_dict[k]['id']))
			with open(result_path+"-data.json", "w") as output:
				json.dump(data_dict, output)
			with open(result_path+"-property.json", "w") as output:
				json.dump(property_dict, output)
			with open(result_path+"-occurred.json", "w") as output:
				json.dump(duplicate_dict, output)
			return data_dict.keys()
	with open(result_path+"-data.json", "w") as output:
		json.dump(data_dict, output)
	with open(result_path+"-property.json", "w") as output:
		json.dump(property_dict, output)
	with open(result_path+"-occurred.json", "w") as output:
			json.dump(duplicate_dict, output)
	return None

def process_data(input_args, num_query = 1000, num_batch = 100):
	with open("ontology/Hierarchy.json") as json_data:
		hierarchy_data = json.load(json_data)
	
	with open("ontology/Properties.json") as json_data:
		property_data = json.load(json_data)

	f = gzip.open(input_args['input'], 'r')

	schema_types = get_subtypes(input_args['type'], hierarchy_data)
	identifier = input_args['identifier']
	properties = [input_args['prop1'], input_args['prop2'], input_args['prop3']]
	property_types = get_data_types(properties, property_data)
	result_path = os.path.join(input_args['output'], input_args['year'], input_args['input'].split("/")[-1].split(".gz")[0])
	if not os.path.exists(result_path):
		os.makedirs(result_path)

	blank_node_list = [[]]
	for b_idx in itertools.count():
		b_path = result_path + "/" + str(b_idx)
		new_blank_node_list = build_graph(schema_types, identifier, properties, property_types, f, b_path, blank_node_list, num_query)
		if new_blank_node_list == None:
			print "batch " + str(b_idx)
			node_list = {}
			if len(blank_node_list) > 1:
				node_list['node_list'] = blank_node_list[1:]
			else:
				node_list['node_list'] = []
			with open(b_path + "-nodelist.json", "w") as output:
				json.dump(node_list, output)
			break
		else:
			blank_node_list.append(new_blank_node_list)
		if b_idx % num_batch == num_batch - 1:
			print "batch " + str(b_idx)
			node_list = {}
			node_list['node_list'] = blank_node_list[1:]
			with open(b_path + "-nodelist.json", "w") as output:
				json.dump(node_list, output)
			blank_node_list = []
			blank_node_list.append(new_blank_node_list)
	return b_idx

def identifier_normalizer(raw_identifier):
	matched_numbers = phonenumbers.PhoneNumberMatcher(raw_identifier, "US")
	identifiers = []
	for match in matched_numbers:
		identifiers.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164))
	return identifiers

def get_subtypes(schema_type, hierarchy_data):
	subtypes = set()
	ss = hierarchy_data[schema_type]["subclasses"]
	for s in ss:
		subtypes.update(get_subtypes(s, hierarchy_data))
	subtypes.add(schema_type)
	return list(subtypes)

def get_parent_properties(schema_type, hierarchy_data):
	properties = set()
	pp = hierarchy_data[schema_type]["parent"]
	for p in pp:
		properties.update(get_parent_properties(p, hierarchy_data))
	properties.update(set(hierarchy_data[schema_type]["properties"]))
	return list(properties)

def get_properties(schema_type, hierarchy_data, include_subtype):
	properties = set()
	properties.update(get_parent_properties(schema_type, hierarchy_data))
	if include_subtype:
		subtypes = get_subtypes(schema_type, hierarchy_data)
		for st in subtypes:
			properties.update(set(hierarchy_data[st]['properties']))
	return list(properties)

def get_data_types(properties, property_data):
	types = set()
	for p in properties:
		types.update(property_data["http://schema.org/"+p])
	return list(types)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', default="/Interlinking-Schema.org/data/2017/schema_Library.gz")
	parser.add_argument('--output', default="/Interlinking-Schema.org/results/")
	parser.add_argument('--type', default="http://schema.org/Library")
	parser.add_argument('--prop1', default="name")
	parser.add_argument('--prop2', default="address")
	parser.add_argument('--prop3', default="email")
	parser.add_argument('--identifier', default="telephone")
	parser.add_argument('--year', default="2017")
	parser.add_argument('--num_query', default=5000, type=int)
	parser.add_argument('--num_batch', default=100, type=int)
	args = vars(parser.parse_args())
	batch_num = process_data(args, args['num_query'], args['num_batch'])
	print batch_num
