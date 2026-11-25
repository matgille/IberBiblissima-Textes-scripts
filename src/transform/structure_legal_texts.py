import glob
import json
import re
import sys
import roman
import lxml.etree as ET

namespaces = {"tei": "http://www.tei-c.org/ns/1.0"}
ET.register_namespace("tei", "http://www.tei-c.org/ns/1.0")

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


def structure_book(xml_tree):
	preexisting_structure = xml_tree.xpath("descendant::tei:div[@type='livre']", namespaces=namespaces)
	if len(preexisting_structure) != 0:
		first_rubric = preexisting_structure[0].xpath("following::tei:figure[tei:ab/tei:hi[@rend='rubrique']]", namespaces=namespaces)[0]


	# Vérifier que le premier texte de la pied_mouch n'est pas ignoré.
	following_siblings = first_rubric.xpath("following-sibling::*",
												namespaces=namespaces)
	localisation_dict = {first_rubric: []}

	# for node in following_siblings:
	current_node = first_rubric
	for index, node in enumerate(following_siblings):
		if node.xpath("self::tei:figure[descendant::tei:hi[@rend='rubrique']]", namespaces=namespaces):
			localisation_dict[node] = []
			current_node = node
		else:
			localisation_dict[current_node].append(node)
	parent_element = first_rubric.xpath("parent::tei:div", namespaces=namespaces)[0]
	print(parent_element)
	for heading, following_nodes in localisation_dict.items():
		div = ET.Element("div")
		div.set("type", "livre")
		parent_element.append(div)
		heading.tag = ET.QName(heading).localname
		head = ET.Element("head")
		head.append(heading)
		par = ET.Element("p")
		par.extend(following_nodes)
		div.append(head)
		div.append(par)
		div.tag = ET.QName(div).localname
	return xml_tree


def structure_chapters(path, do_books:bool):
	xml_tree = ET.parse(path)
	if do_books is True:
		xml_tree = structure_book(xml_tree)
	# Problème de namespace
	sections = xml_tree.xpath("descendant::div[@type='section'] | descendant::tei:div[@type='section']", namespaces=namespaces)
	parts = xml_tree.xpath("descendant::div[@type='partie'] | descendant::tei:div[@type='partie']", namespaces=namespaces)
	books = xml_tree.xpath("descendant::div[@type='section'] | descendant::tei:div[@type='section']", namespaces=namespaces)


	for idx, book in enumerate(books):
		print(f"Treating book {idx + 1}")
		all_rubrics = book.xpath("descendant::tei:div[@type='chapitre']/tei:head/tei:hi", namespaces=namespaces)

		# On récupère les headings qui contiennent "Titul"
		matching = [item for item in all_rubrics if "Titu" in ''.join(item.itertext())]
		print(matching)
		for item in matching:
			ancestor_div = item.xpath("ancestor::tei:div[@type='chapitre']", namespaces=namespaces)[0]
			milestone = ET.Element("milestone")
			ancestor_div.addprevious(milestone)
		previous_title = book.xpath("descendant::tei:div[@type='sous-section']", namespaces=namespaces)
		# if len(previous_title) == 0:
		# 	subsection = ET.Element("div")
		# 	subsection.set("type", "sous-section")
		# 	book.append(subsection)
		# 	previous_title = subsection
		title_n = 1
		for chapter in book.xpath("tei:div[@type='chapitre']", namespaces=namespaces):
			heading = chapter.xpath("descendant::tei:head", namespaces=namespaces)[0]
			if chapter.xpath("boolean(preceding-sibling::*[1][self::milestone])", namespaces=namespaces):
				div_n = 1
				addendum_n = 1
				previous_title = ET.Element("div")
				previous_title.set("type", "sous-section")
				previous_title.set("subtype", "titulo")
				previous_title.set("n", str(title_n))
				title_n += 1
				milestone = chapter.xpath("preceding-sibling::*[1][self::milestone]", namespaces=namespaces)[0]
				milestone.addnext(previous_title)
				milestone.getparent().remove(milestone)
				previous_title.append(heading)
				# chapter.set("type", "prologue")
			else:
				if True: # re.search("[lL]e[ixy]", ''.join(heading.itertext())):
					chapter.set("type", "sous-sous-section")
					chapter.set("subtype", "ley")
					chapter.set("n", str(div_n))
					div_n += 1
				elif "Adi" in ''.join(heading.itertext()):
					chapter.set("type", "addendum")
					chapter.set("subtype", "adicion")
					chapter.set("n", str(addendum_n))
					addendum_n += 1
				elif "Concordança" in ''.join(heading.itertext()):
					chapter.set("type", "addendum")
					chapter.set("subtype", "concordancia")
					chapter.set("n", str(addendum_n))
					addendum_n += 1
			previous_title.append(chapter)
	serialize(path=path, xml_tree=xml_tree)



def serialize(path, xml_tree):
	basename = path.split("/")[-1]
	out_path = f"/home/mgl/Bureau/Travail/projets/Biblissima-Text/data/Biblissima-Textes/structured/struct.{basename}"
	print(f"Writing to {out_path}")
	with open(out_path, "w") as output_xml:
		output_xml.write(ET.tostring(xml_tree, pretty_print=True, encoding="utf8").decode("utf8"))




if __name__ == '__main__':
	path = sys.argv[1]
	is_book = True if sys.argv[2] == "True" else False
	structure_chapters(path, do_books=is_book)