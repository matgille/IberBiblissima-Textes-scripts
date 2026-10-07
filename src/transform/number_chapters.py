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
	parent_type = "//tei:div[@type='partie']"
	# parent_type = "//tei:body"
	target_type = "chapitre"
	for idx_livre, livre_div in enumerate(root.xpath(parent_type, namespaces=namespaces)):
		livre_div.set("n", str(idx_livre + 1))
		for idx_chapitre, chapter_div in enumerate(livre_div.xpath(f"descendant::tei:div[@type='{target_type}']", namespaces=namespaces)):
			chapter_div.set("n", str(idx_chapitre + 1))

	as_tree.write(file, pretty_print=True, encoding="utf-8")

if __name__ == '__main__':
	file = sys.argv[1]
	add_n(file)