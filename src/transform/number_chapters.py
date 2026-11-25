import sys

import lxml.etree as ET


def add_n(file):
	"""
	Adds the n attribute to the <div> elements
	:return:
	"""
	namespaces = {"tei": "http://www.tei-c.org/ns/1.0"}
	as_tree = ET.parse(file)
	root = as_tree.getroot()
	parent_type = "//tei:div[@type='livre']"
	parent_type = "//tei:body"
	target_node = f"descendant::tei:div[@type='chapitre']"
	#target_node = f"descendant::tei:div[@type='acte']"
	for idx_livre, livre_div in enumerate(root.xpath(parent_type, namespaces=namespaces)):
		current_n = 1
		for idx_chapitre, target_div in enumerate(livre_div.xpath(target_node, namespaces=namespaces)):
			if len(target_div.xpath("@real_n")):
				current_n = int(target_div.xpath("@real_n")[0])
			target_div.set("n", str(current_n))
			current_n += 1


	# parent_type = "//tei:body"
	# target_node = f"descendant::tei:div[@type='section']"
	# for idx_livre, livre_div in enumerate(root.xpath(parent_type, namespaces=namespaces)):
	# 	livre_div.set("n", str(idx_livre + 1))
	# 	for idx_chapitre, target_div in enumerate(livre_div.xpath(target_node, namespaces=namespaces)):
	# 		target_div.set("n", str(idx_chapitre + 1))

	as_tree.write(file, pretty_print=True, encoding="utf-8")

if __name__ == '__main__':
	file = sys.argv[1]
	add_n(file)