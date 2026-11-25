import glob
import json
import re
import sys
import roman
import lxml.etree as ET

namespaces = {"tei": "http://www.tei-c.org/ns/1.0"}
ET.register_namespace("tei", "http://www.tei-c.org/ns/1.0")



def main(path):
	xml_tree = ET.parse(path)
	all_pb = xml_tree.xpath("descendant::tei:pb", namespaces=namespaces)
	all_n = xml_tree.xpath("descendant::tei:pb/@n", namespaces=namespaces)
	indices = all_n.index("37v") + 1
	filtered_pb = all_pb[indices:]
	filtered_n = all_n[indices:]
	print(filtered_n)
	current_n = "37v"
	for number, pb in zip(filtered_n, filtered_pb):
		print("---")
		print(f"Current n: {number}")
		search = re.search(r"(\d+)([rv])", current_n)
		digits, side = search.group(1), search.group(2)
		correct_n = int(digits) + 1 if side == "v" else int(digits)
		corrected_side = "r" if side == "v" else "v"
		current_n = f"{correct_n}{corrected_side}"
		pb.set("n", f"{current_n}")
		print(f"Corrected n: {current_n}")
	serialize(path=path, xml_tree=xml_tree)



def serialize(path, xml_tree):
	basename = path.split("/")[-1]
	out_path = f"/home/mgl/Bureau/Travail/projets/Biblissima-Text/data/Biblissima-Textes/structured/struct.{basename}"
	print(f"Writing to {out_path}")
	with open(out_path, "w") as output_xml:
		output_xml.write(ET.tostring(xml_tree, pretty_print=True, encoding="utf8").decode("utf8"))




if __name__ == '__main__':
	path = sys.argv[1]
	main(path)