import glob
import json
import re
import sys
import roman
import lxml.etree as ET

namespaces = {"tei": "http://www.tei-c.org/ns/1.0"}
ET.register_namespace("tei", "http://www.tei-c.org/ns/1.0")



def structure_items(path):
	xml_tree = ET.parse(path)
	# Problème de namespace
	xpath = "descendant::tei:div[@type='sommaire']"
	target = "tei:hi[@rend='rubrique']"
	parent_wrapper = "list"
	wrapper =  "item"
	parent_div = xml_tree.xpath(xpath, namespaces=namespaces)


	for idx, div in enumerate(parent_div):
		print(f"Treating book {idx + 1}")
		try:
			first_rubric = div.xpath(f"descendant::{target}", namespaces=namespaces)[0]
		except IndexError:
			print("Error")
			exit(0)

		# Le tail de la rubrique n'est pas pris en compte
		# Vérifier que le premier texte de la rubrique n'est pas ignoré.
		following_siblings = first_rubric.xpath("following-sibling::*", namespaces=namespaces)
		localisation_dict = {first_rubric: []}

		# for node in following_siblings:
		current_node = first_rubric
		for index, node in enumerate(following_siblings):
			if node.xpath(f"boolean(self::{target})", namespaces=namespaces):
				localisation_dict[node] = []
				current_node = node
			else:
				localisation_dict[current_node].append(node)

		parent_element = div
		parent_wrapper = ET.SubElement(parent_element, parent_wrapper)
		div.append(parent_wrapper)
		for idx, (element_to_wrap, following_nodes) in enumerate(localisation_dict.items()):
			subdiv = ET.Element(wrapper)
			parent_wrapper.append(subdiv)
			subdiv.append(element_to_wrap)
			subdiv.extend(following_nodes)




	serialize(path=path, xml_tree=xml_tree)



def serialize(path, xml_tree):
	basename = path.split("/")[-1]
	out_path = f"/home/mgl/Bureau/Travail/projets/Biblissima-Text/data/Biblissima-Textes/structured/struct.{basename}"
	print(f"Writing to {out_path}")
	with open(out_path, "w") as output_xml:
		output_xml.write(ET.tostring(xml_tree, pretty_print=True, encoding="utf8").decode("utf8"))




if __name__ == '__main__':
	path = sys.argv[1]
	structure_items(path)