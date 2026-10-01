import glob
import json
import sys

import lxml.etree as ET

def unwrap(node):
	"""Remplace `node` par son contenu dans le parent."""
	parent = node.getparent()
	# le texte avant le 1er enfant de node est collé à ce qui précède
	prev = node.getprevious()
	if prev is not None:
		prev.tail = (prev.tail or "") + (node.text or "")
	else:
		parent.text = (parent.text or "") + (node.text or "")

	# déplacer les enfants de node juste avant node (= à sa place)
	for child in list(node):
		node.addprevious(child)

	# le tail de node est collé à ce qui précède maintenant
	prev = node.getprevious()
	if prev is not None:
		prev.tail = (prev.tail or "") + (node.tail or "")
	else:
		parent.text = (parent.text or "") + (node.tail or "")

	parent.remove(node)



def replace_element(parent, old_element, new_element):
	"""
	Remplace un élément enfant par un nouvel élément dans un parent donné.

	Args:
		parent: L'élément parent contenant l'élément à remplacer
		old_element: L'élément à remplacer
		new_element: Le nouvel élément à insérer
	"""
	# Trouver l'index de l'ancien élément
	index = parent.index(old_element)

	# Supprimer l'ancien élément
	parent.remove(old_element)

	# Insérer le nouvel élément à la même position
	parent.insert(index, new_element)



namespaces = {"tei": "http://www.tei-c.org/ns/1.0"}
ET.register_namespace("tei", "http://www.tei-c.org/ns/1.0")


def structure_stroph(lineGroup):
	first_node_in_stroph = lineGroup.xpath("descendant::speaker", namespaces=namespaces)[0]


	# Vérifier que le premier texte de la pied_mouch n'est pas ignoré.
	following_siblings = first_node_in_stroph.xpath("following-sibling::*",
												namespaces=namespaces)
	localisation_dict = {first_node_in_stroph: []}

	# for node in following_siblings:
	current_node = first_node_in_stroph
	for index, node in enumerate(following_siblings):
		if node.tag == "{http://www.tei-c.org/ns/1.0}lb":
			localisation_dict[node] = []
			current_node = node
		else:
			localisation_dict[current_node].append(node)
	print(len(localisation_dict))
	lg = ET.Element("lg")
	for leading_node, following_nodes in localisation_dict.items():
		leading_node.tag = ET.QName(leading_node).localname
		verse = ET.Element("l")
		verse.append(leading_node)
		[verse.append(item) for item in following_nodes]
		lg.append(verse)
		lineGroup.append(lg)
		if leading_node.tag == "speaker":
			first_verse = leading_node.xpath("following-sibling::*")
			interm_node = ET.Element("l")
			interm_node.text = leading_node.tail
			leading_node.tail = None
			[interm_node.append(item) for item in first_verse]
			verse.addnext(interm_node)
	return lineGroup

def structure(path):
	xml_tree = ET.parse(path)

	parent_element = \
	xml_tree.xpath("descendant::tei:body/descendant::tei:p[@type='debut_piece']", namespaces=namespaces)[0]

	## La structure générale




	first_didascalie = parent_element.xpath("child::tei:lb[following-sibling::*[1][self::tei:hi[tei:choice]]]", namespaces=namespaces)[0]

	# Le tail de la pied_mouch n'est pas pris en compte
	# Vérifier que le premier texte de la pied_mouch n'est pas ignoré.
	following_siblings = first_didascalie.xpath("following-sibling::*", namespaces=namespaces)
	localisation_dict = {first_didascalie: []}

	# for node in following_siblings:
	current_node = first_didascalie
	for index, node in enumerate(following_siblings):
		if (
				node.xpath("self::tei:lb[following-sibling::*[1][self::tei:hi[tei:choice]]]", namespaces=namespaces)
		):
			localisation_dict[node] = []
			current_node = node
		else:
			localisation_dict[current_node].append(node)
	print(len(localisation_dict))

	for idx, (linebreak, following_nodes) in enumerate(localisation_dict.items()):
		linebreak.tag = ET.QName(linebreak).localname
		intervention = ET.Element("sp")
		speaker = ET.Element("speaker")
		# On l'insère après le lb.
		intervention.append(linebreak)
		[intervention.append(item) for  item in following_nodes]
		didascalie = intervention.xpath("tei:hi[@rend='rubrique'][tei:choice]", namespaces=namespaces)[0]

		speaker.append(didascalie)
		intervention.insert(1, speaker)
		# ON déplace les tails de didascalie vers speaker
		tail_speaker = didascalie.tail
		didascalie.tail = ""
		speaker.tail = tail_speaker

		# Avec la ligne précédente, on a
		parent_element.append(intervention)

	all_sp = parent_element.xpath("//sp", namespaces=namespaces)
	for sp in all_sp:
		replace_element(sp.getparent(), sp, structure_stroph(sp))
		speaker = sp.xpath("descendant::speaker")[0]
		sp.insert(1, speaker)
		empty_verse = sp.xpath("descendant::l[not(node() or text())]")
		for verse in empty_verse:
			verse.getparent().remove(verse)


	basename = path.split("/")[-1]
	out_path = f"/home/mgl/Bureau/Travail/projets/Biblissima-Text/data/Biblissima-Textes/structured/{basename}"
	print(f"Writing to {out_path}")
	with open(out_path, "w") as output_xml:
		output_xml.write(ET.tostring(xml_tree, pretty_print=True, encoding="utf8").decode("utf8"))




if __name__ == '__main__':
	path = sys.argv[1]
	structure(path)