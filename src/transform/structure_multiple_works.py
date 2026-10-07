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
		first_note = preexisting_structure[0].xpath("following::tei:note[starts-with(text(), 'HSMS-')]", namespaces=namespaces)[0]


	# Vérifier que le premier texte de la pied_mouch n'est pas ignoré.
	following_siblings = first_note.xpath("following-sibling::*",
												namespaces=namespaces)
	localisation_dict = {first_note: []}

	# for node in following_siblings:
	current_node = first_note
	for index, node in enumerate(following_siblings):
		if node.xpath("following::tei:note[starts-with(text(), 'HSMS-')]", namespaces=namespaces):
			localisation_dict[node] = []
			current_node = node
		else:
			localisation_dict[current_node].append(node)
	parent_element = first_note.xpath("parent::tei:div", namespaces=namespaces)[0]
	print(parent_element)
	for heading, following_nodes in localisation_dict.items():
		div = ET.Element("div")
		div.set("type", "livre")
		parent_element.append(div)
		div.append(heading)
		par = ET.Element("p")
		par.extend(following_nodes)
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
	books = xml_tree.xpath("descendant::div[@type='livre'] | descendant::tei:div[@type='livre']", namespaces=namespaces)

	print(books)
	for idx, book in enumerate(books):
		print(f"Treating book {idx + 1}")
		try:
			first_rubric = book.xpath("descendant::tei:note[starts-with(text(), 'HSMS-')]", namespaces=namespaces)[0]
			# first_rubric = book.xpath("descendant::tei:g[@ref='#calderon1']", namespaces=namespaces)[0]
			# first_rubric = book.xpath("descendant::tei:hi[@rend='rubrique'][not(ancestor::figure)]", namespaces=namespaces)[0]
		except IndexError:
			print("Error")
			# Create a default div if no rubric is found
			parent_element = book.xpath("tei:div", namespaces=namespaces)[0]
			subdiv = ET.Element("div")
			parent_element.append(subdiv)
			subdiv.set("type", "section")
			p = ET.Element("p")
			subdiv.append(p)

			# Add all content to the default paragraph
			for node in book.iterchildren():
				if node.tag == "{http://www.tei-c.org/ns/1.0}div":
					continue  # Skip existing divs
				try:
					node.tag = ET.QName(node).localname
				except (ValueError, AttributeError):
					pass
				p.append(node)

			basename = path.split("/")[-1]
			out_path = f"/home/mgl/Bureau/Travail/projets/Biblissima-Text/data/Biblissima-Textes/structured/{basename}"
			with open(out_path, "w") as output_xml:
				output_xml.write(ET.tostring(xml_tree, pretty_print=True, encoding="utf8").decode("utf8"))
			return

		# Le tail de la rubrique n'est pas pris en compte
		# Vérifier que le premier texte de la rubrique n'est pas ignoré.
		following_siblings = first_rubric.xpath("following-sibling::*", namespaces=namespaces)
		localisation_dict = {first_rubric: []}

		# for node in following_siblings:
		current_node = first_rubric
		for index, node in enumerate(following_siblings):
			if node.tag == "{http://www.tei-c.org/ns/1.0}note" and "HSMS-" in node.text:
				localisation_dict[node] = []
				current_node = node
			else:
				localisation_dict[current_node].append(node)

		parent_element = book
		for idx, (note, following_nodes) in enumerate(localisation_dict.items()):
			note.tag = ET.QName(note).localname
			subdiv = ET.Element("div")
			ident = re.search(r"HSMS-\d{4}-\d{4}", note.text).group(0)
			subdiv.set("{http://www.w3.org/XML/1998/namespace}id", ident)
			parent_element.append(subdiv)
			subdiv.set("type", "chapitre")
			subdiv.set("n", str(idx + 1))
			subdiv.append(note)
			p = ET.Element("p")
			subdiv.append(p)
			p.extend(following_nodes)

			# Gestion des noeuds non textuels
			for idx, node in enumerate(following_nodes):
				try:
					node.tag = ET.QName(node).localname
				except (ValueError, AttributeError):
					pass
				try:
					p.append(node)
				except TypeError as e:
					print(e)
					print(f"Erreur sur |{node}|, vérifiez que le noeud textuel a été correctement placé")
					print(idx)
					print(following_nodes)
					if node is None:
						continue
					else:
						if isinstance(node, str):
							p.text = node
							continue
					try:
						following_nodes[idx - 1].tail = following_nodes[idx - 1].tail + node
					except (TypeError, AttributeError) as e:
						print(e)
						print(f"Tail |{following_nodes[idx - 1]}| non injecté")
						print(following_nodes[idx - 1].tail)
						print(ET.tostring(following_nodes[idx - 1]))
						continue


	serialize(path=path, xml_tree=xml_tree)



def set_page_breaks(path, base_path="/home/mgl/Bureau/Travail/projets/Biblissima-Text/data/Biblissima-Textes/facsimiles/HSMS-0075/"):
	"""
	Sets the facsimile paths for page breaks in the XML tree.

	Args:
		xml_tree: The XML tree to process
		base_path: The base path for facsimile images (default is HSMS-0075)
	"""
	# Find all page breaks, handling both namespaced and non-namespaced elements
	xml_tree = ET.parse(path)
	page_breaks = xml_tree.xpath(
		"descendant::pb | descendant::tei:pb",
		namespaces=namespaces
	)

	for idx, page_break in enumerate(page_breaks):
		# Start numbering from 2 (as in the original code)
		page_num = idx + 1

		# Format the page number with leading zeros
		if page_num < 10:
			correct_pb = f"000{page_num}"
		elif page_num < 100:
			correct_pb = f"00{page_num}"
		elif page_num < 1000:
			correct_pb = f"0{page_num}"
		else:
			correct_pb = str(page_num)

		# Set the facs attribute with the formatted page number
		page_break.set("facs", f"{base_path}pg_{correct_pb}.pdf")
	return xml_tree

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