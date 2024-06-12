import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as BS
import trafilatura


def trafilatura_standard_xml(html_str):
    xml = trafilatura.extract(
        html_str,
        output_format="xml",
        with_metadata=False,
        include_comments=False,
        include_images=False,
        include_formatting=False,
    )

    if not xml:
        return None

    # delete metadata from doc
    root = ET.fromstring(xml)
    root.attrib.clear()
    xml = ET.tostring(root, encoding="unicode")

    return xml


def trafilatura_h1extra_xml(html_str):
    xml = trafilatura.extract(
        html_str,
        output_format="xml",
        with_metadata=False,
        include_comments=False,
        include_images=False,
        include_formatting=False,
    )

    # delete metadata from doc
    root = ET.fromstring(xml)
    root.attrib.clear()

    # Add header1 to xml
    # Create header element
    soup = BS(html_str, "lxml")
    header1 = soup.find("h1").get_text(separator=" ")
    header1_element = ET.Element("head")
    header1_element.text = header1
    header1_element.tail = "\n"
    header1_element.attrib["rend"] = "h1"
    # Insert at the beginning
    main_element = root.find("main")
    main_element.insert(0, header1_element)

    xml = ET.tostring(root, encoding="unicode")

    return xml


def text_from_xml(xml):
    tree = BS(xml, "lxml-xml")
    main = tree.find("main")
    texts = [
        elem.get_text(separator=' ', strip=True)
        for elem in main.find_all(recursive=False)
    ]
    rawtext = "\n\n".join([t.strip() for t in texts if t is not None])
    rawtext = re.sub(r"\n[ \t]*\n([ \t]*\n)+", "\n\n", rawtext)
    return rawtext


def get_xml_and_text(html_str, trafilatura_function=trafilatura_standard_xml):
    xml = trafilatura_function(html_str)
    rawtext = text_from_xml(xml)

    return xml, rawtext


if __name__ == "__main__":
    with open("test_files/spektrum_test1.html", "r", encoding="utf-8") as f:
        html_str = f.read()
    print(trafilatura_standard_xml(html_str))
