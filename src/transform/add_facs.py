import sys

import lxml.etree as ET


def serialize(path, xml_tree):
	print(f"Writing to {path}")
	with open(path, "w") as output_xml:
		output_xml.write(ET.tostring(xml_tree, pretty_print=True, encoding="utf8").decode("utf8"))



def main(file, facs_dir, page_shift):
	namespaces = {"tei": "http://www.tei-c.org/ns/1.0"}
	xml_tree = ET.parse(file)
	for idx, page_break in enumerate(xml_tree.xpath("descendant::tei:pb", namespaces=namespaces)):
		idx += page_shift
		# correct_pb = idx
		if idx < 10:
			correct_pb = f"000{idx}"
		elif idx < 100:
			correct_pb = f"00{idx}"
		elif idx < 1000:
			correct_pb = f"0{idx}"
		else:
			correct_pb = idx
		wd = f"/home/mgl/Bureau/Travail/projets/Biblissima-Text/data/Biblissima-Textes/facsimiles/{facs_dir}/"
		page_break.set("facs", f"{wd}pg_{correct_pb}.pdf")
		# page_break.set("facs", f"{wd}{correct_pb}.jpg")
		# page_break.set("facs", f"{wd}{correct_pb}.pdf")
	serialize(path=f"/home/mgl/Bureau/Travail/projets/Biblissima-Text/data/Biblissima-Textes/with_facs/{file.split('/')[-1]}", xml_tree=xml_tree)


if __name__ == '__main__':
	input_file = sys.argv[1]
	facs_dir = sys.argv[2]
	page_shift = int(sys.argv[3])
	main(input_file, facs_dir, page_shift)