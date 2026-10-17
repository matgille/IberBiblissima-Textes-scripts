import glob
import json
import re
import sys
import roman
import lxml.etree as ET

namespaces = {"tei": "http://www.tei-c.org/ns/1.0"}
ET.register_namespace("tei", "http://www.tei-c.org/ns/1.0")



def add_paragraphs(path):
	xml_tree = ET.parse(path)
	# Problème de namespace
	filter_node = "livre"
	filter_node = "chapitre"
	target_nodes = "tei:hi[@rend='initiale']"
	target_nodes = "tei:g[@ref='#calderon1']"
	element_name = "p"

	# Dans quel élément envelopper l'élément créé (peut être None)
	wrap_text = None
	wrap_text = "p"
	# Faut-il ajouter un type à la division mère (peut être None)
	element_type = "section"
	element_type = None
	divs = xml_tree.xpath(f"descendant::tei:div[@type='{filter_node}']", namespaces=namespaces)

	for idx, div in enumerate(divs):
		print(f"Treating chapter {idx + 1}")
		try:
			first_initial = div.xpath(f"descendant::{target_nodes}", namespaces=namespaces)[0]
		except IndexError:
			print("No node found")
			continue


		# Le tail de la rubrique n'est pas pris en compte
		# Vérifier que le premier texte de la rubrique n'est pas ignoré.
		following_siblings = first_initial.xpath("following-sibling::*", namespaces=namespaces)
		localisation_dict = {first_initial: []}

		# for node in following_siblings:
		current_node = first_initial
		for index, node in enumerate(following_siblings):
				# localisation_dict[node] = []
				# current_node = node
			# elif node.tag == "{http://www.tei-c.org/ns/1.0}g" and node.attrib['ref'] == "#calderon1":
			# 	localisation_dict[node] = []
			# 	current_node = node
			if node.xpath(f"boolean(self::{target_nodes})", namespaces=namespaces):
				localisation_dict[node] = []
				current_node = node
			else:
				localisation_dict[current_node].append(node)

		parent_element = div
		for idx, (target_node, following_nodes) in enumerate(localisation_dict.items()):
			subdiv = ET.Element(element_name)
			if element_type:
				subdiv.set("type", element_type)
				subdiv.set("n", str(idx + 1))
			parent_element.append(subdiv)
			if wrap_text:
				wrapping_element = ET.SubElement(subdiv, wrap_text)
				wrapping_element.append(target_node)
				wrapping_element.extend(following_nodes)
			else:
				subdiv.append(target_node)
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
	add_paragraphs(path)