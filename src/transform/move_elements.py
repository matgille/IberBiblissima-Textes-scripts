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
	target_node = f"descendant::tei:div[@type='chapitre']"
	#target_node = f"descendant::tei:div[@type='acte']"
	for idx_chapitre, target_div in enumerate(root.xpath(target_node, namespaces=namespaces)):
		print(f"Found div {idx_chapitre}")
		target_elements = "descendant::tei:p/descendant::tei:seg[@ana='#addendum'][tei:add[@hand='#self']][not(following-sibling::*)]"
		for elem in target_div.xpath(target_elements, namespaces=namespaces):
			print(ET.tostring(elem, pretty_print=True))
			print("Moving file")
			target_location = target_div.xpath("following-sibling::tei:div[@type='chapitre']/tei:head", namespaces=namespaces)[0]
			target_location.append(elem)

	basename = file.split("/")[-1]
	out_path = f"/home/mgl/Bureau/Travail/projets/Biblissima-Text/data/Biblissima-Textes/structured/struct.{basename}"


	as_tree.write(out_path, pretty_print=True, encoding="utf-8")

if __name__ == '__main__':
	file = sys.argv[1]
	add_n(file)