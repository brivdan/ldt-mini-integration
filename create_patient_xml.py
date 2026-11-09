import xml.etree.ElementTree as ET

root = ET.Element("LabReport")
patient = ET.SubElement(root, "Patient")

ET.SubElement(patient, "FamilyName").text = "Maximillian"
ET.SubElement(patient, "GivenName").text = "Michael"

ET.indent(root, space="  ")
ET.dump(root)