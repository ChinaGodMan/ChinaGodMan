import re
import os
from lxml import etree
import base64
import requests

USER_ID = os.getenv("USER_ID")


def download_files_from_file(input_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.replace("USER_ID", USER_ID).strip()
            if "|" in line:
                url, filename = line.split("|", 1)
                url, filename = url.strip(), filename.strip()
                if url and filename:
                    try:
                        response = requests.get(url, stream=True)
                        response.raise_for_status()

                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                    except requests.RequestException as e:
                        print(f"Failed to download {url}: {e}")
                else:
                    print(f"Invalid line format: {line}")
            else:
                print(f"Invalid line format: {line}")


def extract_and_save_images(svg_file_path, output_dir="my_songs"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(svg_file_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    namespace = {'svg': 'http://www.w3.org/2000/svg',
                 'xlink': 'http://www.w3.org/1999/xlink'}
    tree = etree.fromstring(svg_content)
    image_tags = tree.xpath('//svg:image', namespaces=namespace)
    for image_tag in image_tags:
        image_id = image_tag.attrib.get('id', '无ID')

        if image_id.startswith("image") and image_id[5:].isdigit():
            xlink_href = image_tag.attrib.get(
                '{http://www.w3.org/1999/xlink}href', '无xlink:href')

            if xlink_href.startswith("data:image/"):
                img_format = xlink_href.split(";")[0].split("/")[-1]
                base64_data = xlink_href.split(",")[1]
                try:
                    image_data = base64.b64decode(base64_data)
                    output_file_path = os.path.join(
                        output_dir, f"{image_id}.{img_format}")

                    with open(output_file_path, 'wb') as img_file:
                        img_file.write(image_data)
                except Exception as e:
                    print(f"解码或保存图片时出错，跳过该图片: {e}")
            else:
                print(f"跳过无效的 xlink:href: {xlink_href}")


def parse_svg_and_generate_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    tree = etree.fromstring(svg_content)
    a_tags = tree.xpath('//svg:a', namespaces=namespace)
    md_output = []
    mb = 0
    for a_tag in a_tags:
        link = a_tag.attrib.get('href', '').strip()
        link_text_elements = a_tag.xpath(
            './/svg:tspan//svg:a/text()', namespaces=namespace)
        for link_text in link_text_elements:
            link_text = link_text.strip()
            mb = mb + 1
            text_elements = a_tag.xpath(
                './/svg:text//svg:tspan', namespaces=namespace)
            other_texts = [t.text.strip() for t in text_elements if t.text]
            other_text_combined = ' '.join(other_texts)
            image_url = f"/my_songs/image{mb - 1}.jpg"
            md_line = f"""<li><img src="{image_url}" alt="Image {mb - 1} width="24" height="24""><a href="{link}">{link_text} - {other_text_combined}</a></li>"""
            md_output.append(md_line)

    return md_output


download_files_from_file("src/images.txt", "dist")
extract_and_save_images("dist/163_dark.svg")
md_results = parse_svg_and_generate_md("dist/163_dark.svg")

text = "\n".join(str(md) for md in md_results)
with open("README.md", "r", encoding="utf-8") as file:
    content = file.read()

new_content = re.sub(
    r"<!--MUSIC-->.*?<!--MUSIC-END-->",
    f"<!--MUSIC-->\n{text}\n<!--MUSIC-END-->",
    content,
    flags=re.DOTALL
)
with open("README.md", "w", encoding="utf-8") as file:
    file.write(new_content)
