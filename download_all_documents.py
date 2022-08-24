import argparse
import re
from pathlib import Path

import yaml

from yuque_py import Yuque


def get_repo_indices_from_yuque(yuque: Yuque, user: str):
    return yuque.repos.list(user=user)["data"]


def get_repo_data_from_yuque(yuque: Yuque, namespace: str):
    return yuque.repos.get(namespace=namespace)["data"]


def get_doc_data_from_yuque(yuque: Yuque, namespace: str, slug: str):
    return yuque.docs.get(namespace=namespace, slug=slug)["data"]


def get_doc_indices_from_repo_data(repo_data: dict):
    repo_toc_yml = yaml.load(stream=repo_data["toc_yml"], Loader=yaml.SafeLoader)

    doc_indices = []
    for doc_index in repo_toc_yml:
        if "title" not in doc_index:
            continue
        if doc_index["type"] == "DOC":
            doc_indices.append(doc_index)
    return doc_indices


def get_doc_content_from_doc_data(doc_data):
    doc_title = doc_data["title"]
    doc_slug = doc_data["slug"]
    doc_created_at = doc_data["created_at"]
    doc_updated_at = doc_data["updated_at"]
    doc_description = doc_data["description"]
    doc_author = doc_data["creator"]["name"]

    book_slug = doc_data["book"]["slug"]
    book_description = doc_data["book"]["description"]
    book_author = doc_data["book"]["user"]["login"]

    book_yuque_link = f"https://www.yuque.com/{book_author}/{book_slug}"
    doc_yuque_link = f"https://www.yuque.com/{book_author}/{book_slug}/{doc_slug}"

    doc_body: str = substitute_invalid_text(doc_data["body"])

    doc_content = [
        "---",
        f"title: {doc_title}",
        f"created: {doc_created_at}",
        f"updated: {doc_updated_at}",
        f"description: {doc_description}",
        f"author: {doc_author}",
        f"original_link: {doc_yuque_link}",
        f"book:",
        f"    - title: {book_slug}",
        f"    - author: {book_author}",
        f"    - description: {book_description}",
        f"    - original_link: {book_yuque_link}",
        "---",
        f"\n# {doc_title}",
        doc_body,
    ]
    return doc_content


def substitute_invalid_text(text: str):
    patterns = {
        r"<a.*?>": "",
        f"</a>": "",
        r"<br ?/>": "\n\n",
        "\n   -": "\n    -",
    }
    for p, r in patterns.items():
        text = re.sub(pattern=p, repl=r, string=text, flags=re.IGNORECASE)
    return text


def convert_string_to_valid_window_path(string):
    patterns = {
        r"[/\\\\:\*\?\|\.]": "_",
        r"\n": " ",
    }
    for p, r in patterns.items():
        string = re.sub(pattern=p, repl=r, string=string)
    return string


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=str, required=True, help="用户名")
    parser.add_argument("--token", type=str, required=True, help="用户token")
    parser.add_argument("--output", type=str, default="download", help="下载文档的存放目录")
    parser.add_argument("--verbose", action="store_true", help="是否打印中间信息")
    return parser.parse_args()


def main():
    args = get_args()
    output_dir = Path(args.output)

    yuque = Yuque(api_host="https://www.yuque.com/api/v2", user_token=args.token)

    repo_indices = get_repo_indices_from_yuque(yuque=yuque, user=args.user)
    for repo_index in repo_indices:
        if repo_index["type"] != "Book":
            continue
        repo_data = get_repo_data_from_yuque(
            yuque=yuque, namespace=repo_index["namespace"]
        )
        repo_name = convert_string_to_valid_window_path(repo_data["name"])

        doc_indices = get_doc_indices_from_repo_data(repo_data=repo_data)
        num_docs = len(doc_indices)
        for i, doc_index in enumerate(doc_indices, start=1):
            doc_title = str(doc_index["title"])
            if args.verbose:
                print(f"[{i}/{num_docs}] {repo_name}/{doc_title}")

            doc_data = get_doc_data_from_yuque(
                yuque=yuque, namespace=repo_data["namespace"], slug=doc_index["url"]
            )
            doc_content = get_doc_content_from_doc_data(doc_data=doc_data)

            doc_title = convert_string_to_valid_window_path(doc_title)
            doc_file = output_dir.joinpath(repo_name, doc_title + ".md")
            doc_file.parent.mkdir(exist_ok=True)
            doc_file.write_text("\n".join(doc_content), encoding="utf-8")
            if args.verbose:
                print(f"[{i}/{num_docs}] 文档保存为 {doc_file}")


if __name__ == "__main__":
    main()
