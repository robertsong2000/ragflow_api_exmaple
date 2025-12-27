#!/usr/bin/env python3
"""
列出指定知识库中的所有文档

使用方法:
    python list_kb_documents.py --kb-id <知识库ID>
    python list_kb_documents.py --kb-name <知识库名称>
    python list_kb_documents.py --list-kbs  # 列出所有知识库

示例:
    python list_kb_documents.py --list-kbs
    python list_kb_documents.py --kb-id <知识库ID>
    python list_kb_documents.py --kb-name "<知识库名称>"
    python list_kb_documents.py --kb-id <知识库ID> --format csv
    python list_kb_documents.py --kb-id <知识库ID> --output documents.txt
    python list_kb_documents.py --kb-id <知识库ID> --brief  # 仅输出文档名称

配置说明:
    1. 默认读取 ragflow_config.json 配置文件
    2. 可通过 --config 参数指定配置文件路径
    3. 可通过 --api-url 和 --api-key 参数覆盖配置文件
    4. 配置文件格式：
       {
         "api_url": "http://your-ragflow-server:1800/api/v1",
         "api_key": "your-api-key-here"
       }
"""

import argparse
import sys
import os
import json
from typing import List, Dict, Any
import requests


class DocumentLister:
    """文档列表工具"""

    def __init__(self, api_url: str = None, api_key: str = None, config_file: str = None):
        """初始化

        Args:
            api_url: RAGFlow API地址，默认从配置文件或环境变量读取
            api_key: RAGFlow API密钥，默认从配置文件或环境变量读取
            config_file: 配置文件路径，默认为 ragflow_config.json
        """
        # 1. 尝试从配置文件读取
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if not api_url:
                        api_url = config.get('api_url')
                    if not api_key:
                        api_key = config.get('api_key')
                print(f"✅ 已从配置文件读取: {config_file}")
            except Exception as e:
                print(f"⚠️  读取配置文件失败: {e}")

        # 2. 从环境变量读取
        if not api_url:
            api_url = os.getenv('RAGFLOW_API_URL')
        if not api_key:
            api_key = os.getenv('RAGFLOW_API_KEY')

        # 3. 使用默认值
        if not api_url:
            api_url = 'http://localhost:9380'
            print(f"⚠️  未指定API地址，使用默认值: {api_url}")

        if not api_key:
            raise ValueError('API密钥未设置！请通过以下方式之一设置:\n'
                           '  1. 配置文件 ragflow_config.json 中的 api_key 字段\n'
                           '  2. --api-key 参数\n'
                           '  3. RAGFLOW_API_KEY 环境变量')

        self.api_url = api_url.rstrip('/')
        self.api_key = api_key

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        print(f"✅ 已连接到 RAGFlow API: {self.api_url}")

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """通用请求方法"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API请求错误: {e}")
            raise

    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """获取所有知识库"""
        try:
            result = self._request('GET', '/datasets')
            if result.get('code') == 0:
                return result.get('data', [])
            print(f"⚠️  API返回错误: {result.get('message', '未知错误')}")
            return []
        except Exception as e:
            print(f"❌ 获取知识库失败: {e}")
            return []

    def get_kb_by_name(self, name: str) -> Dict[str, Any]:
        """根据名称查找知识库

        Args:
            name: 知识库名称（支持模糊匹配）

        Returns:
            找到的知识库信息，未找到返回None
        """
        kbs = self.list_knowledge_bases()
        for kb in kbs:
            if name.lower() in kb.get('name', '').lower():
                return kb
        return None

    def list_documents(self, kb_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
        """获取知识库中的所有文档

        Args:
            kb_id: 知识库ID
            page_size: 每页数量，默认100

        Returns:
            文档列表
        """
        all_docs = []
        page = 1

        print(f"📋 正在获取知识库 '{kb_id}' 的文档...")

        while True:
            try:
                params = {
                    'page': page,
                    'page_size': page_size
                }
                result = self._request('GET', f'/datasets/{kb_id}/documents', params=params)

                if result.get('code') == 0:
                    data = result.get('data', {})
                    docs = data.get('docs', [])

                    if not docs:
                        break

                    all_docs.extend(docs)
                    print(f"   已获取 {len(all_docs)} 个文档...")

                    # 检查是否还有更多文档
                    if len(docs) < page_size:
                        break

                    page += 1
                else:
                    print(f"❌ API返回错误: {result.get('message', '未知错误')}")
                    break

            except Exception as e:
                print(f"❌ 获取文档失败: {e}")
                break

        print(f"✅ 共获取 {len(all_docs)} 个文档\n")
        return all_docs

    def display_documents(self, docs: List[Dict[str, Any]], format_type: str = 'table', brief: bool = False):
        """显示文档列表

        Args:
            docs: 文档列表
            format_type: 显示格式 (table, json, csv)
            brief: 是否仅输出文档名称
        """
        if not docs:
            print("⚠️  该知识库中没有文档")
            return

        if brief:
            # 简洁模式：仅输出文档名称
            for doc in docs:
                print(doc.get('name', 'N/A'))
            return

        if format_type == 'json':
            import json
            print(json.dumps(docs, indent=2, ensure_ascii=False))

        elif format_type == 'csv':
            # 输出CSV格式
            print("文档ID,文档名称,Chunk数量,状态,大小")
            for doc in docs:
                doc_id = doc.get('document_id', 'N/A')
                name = doc.get('name', 'N/A')
                chunk_count = doc.get('chunk_count', 0)
                status = doc.get('status', 'N/A')
                size = doc.get('size', 0)
                size_mb = f"{size / 1024 / 1024:.2f} MB" if size else 'N/A'
                print(f'"{doc_id}","{name}",{chunk_count},{status},"{size_mb}"')

        else:
            # 默认表格格式
            print("\n" + "=" * 120)
            print(f"{'序号':<6} {'文档ID':<30} {'文档名称':<40} {'Chunks':<10} {'状态':<15} {'大小':<12}")
            print("=" * 120)

            for idx, doc in enumerate(docs, 1):
                doc_id = doc.get('document_id', 'N/A')[:28] + '..' if len(doc.get('document_id', '')) > 30 else doc.get('document_id', 'N/A')
                name = doc.get('name', 'N/A')[:38] + '..' if len(doc.get('name', '')) > 40 else doc.get('name', 'N/A')
                chunk_count = doc.get('chunk_count', 0)
                status = doc.get('status', 'N/A')
                size = doc.get('size', 0)
                size_str = f"{size / 1024 / 1024:.2f} MB" if size else '-'

                # 状态图标
                status_icon = {
                    'SUCCESS': '✅',
                    'RUNNING': '🔄',
                    'UNSTART': '⏸️',
                    'FAIL': '❌'
                }.get(status, '⚪')

                print(f"{idx:<6} {doc_id:<30} {name:<40} {chunk_count:<10} {status_icon} {status:<12} {size_str:<12}")

            print("=" * 120)
            print(f"\n总计: {len(docs)} 个文档\n")

    def save_to_file(self, docs: List[Dict[str, Any]], output_file: str, format_type: str = 'json'):
        """保存文档列表到文件

        Args:
            docs: 文档列表
            output_file: 输出文件路径
            format_type: 文件格式 (json, csv, txt)
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if format_type == 'json':
                    import json
                    json.dump(docs, f, indent=2, ensure_ascii=False)

                elif format_type == 'csv':
                    f.write("文档ID,文档名称,Chunk数量,状态,大小\n")
                    for doc in docs:
                        doc_id = doc.get('document_id', 'N/A')
                        name = doc.get('name', 'N/A')
                        chunk_count = doc.get('chunk_count', 0)
                        status = doc.get('status', 'N/A')
                        size = doc.get('size', 0)
                        size_mb = f"{size / 1024 / 1024:.2f} MB" if size else 'N/A'
                        f.write(f'"{doc_id}","{name}",{chunk_count},{status},"{size_mb}"\n')

                else:  # txt
                    f.write(f"知识库文档列表\n")
                    f.write(f"=" * 80 + "\n\n")
                    for idx, doc in enumerate(docs, 1):
                        f.write(f"{idx}. {doc.get('name', 'N/A')}\n")
                        f.write(f"   ID: {doc.get('document_id', 'N/A')}\n")
                        f.write(f"   Chunks: {doc.get('chunk_count', 0)}\n")
                        f.write(f"   状态: {doc.get('status', 'N/A')}\n")
                        f.write(f"   大小: {doc.get('size', 0) / 1024 / 1024:.2f} MB\n" if doc.get('size') else "   大小: N/A\n")
                        f.write("\n")

            print(f"✅ 文档列表已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='列出指定知识库中的所有文档',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--kb-id', type=str, help='知识库ID')
    parser.add_argument('--kb-name', type=str, help='知识库名称(支持模糊匹配)')
    parser.add_argument('--list-kbs', action='store_true', help='列出所有知识库')
    parser.add_argument('--format', type=str, choices=['table', 'json', 'csv'], default='table',
                       help='输出格式 (默认: table)')
    parser.add_argument('--brief', action='store_true',
                       help='简洁模式: 仅输出文档名称,每行一个')
    parser.add_argument('--output', type=str, help='输出文件路径 (可选)')
    parser.add_argument('--config', type=str, default='ragflow_config.json',
                       help='RAGFlow配置文件路径 (默认: ragflow_config.json)')
    parser.add_argument('--api-url', type=str, help='RAGFlow API地址 (覆盖配置文件)')
    parser.add_argument('--api-key', type=str, help='RAGFlow API密钥 (覆盖配置文件)')

    args = parser.parse_args()

    try:
        # 初始化客户端（优先级：命令行参数 > 配置文件 > 环境变量）
        lister = DocumentLister(
            api_url=args.api_url,
            api_key=args.api_key,
            config_file=args.config
        )

        # 列出所有知识库
        if args.list_kbs:
            print("\n📚 所有知识库列表:\n")
            kbs = lister.list_knowledge_bases()

            if not kbs:
                print("⚠️  未找到任何知识库")
                return

            print(f"{'序号':<6} {'知识库ID':<40} {'知识库名称':<40} {'文档数':<10} {'Chunks':<10}")
            print("-" * 120)
            for idx, kb in enumerate(kbs, 1):
                kb_id = kb.get('id', 'N/A')
                name = kb.get('name', 'N/A')
                chunk_count = kb.get('chunk_count', 0)  # 修复：使用正确的字段名
                doc_count = kb.get('document_count', 0)
                print(f"{idx:<6} {kb_id:<40} {name:<40} {doc_count:<10} {chunk_count:<10}")

            print(f"\n总计: {len(kbs)} 个知识库\n")
            return

        # 获取文档列表
        kb_id = args.kb_id

        # 如果使用知识库名称
        if args.kb_name:
            print(f"\n🔍 正在查找知识库: {args.kb_name}")
            kb = lister.get_kb_by_name(args.kb_name)
            if kb:
                kb_id = kb.get('id')
                print(f"✅ 找到知识库: {kb.get('name')} (ID: {kb_id})\n")
            else:
                print(f"❌ 未找到知识库: {args.kb_name}")
                print("💡 提示: 使用 --list-kbs 查看所有可用知识库")
                return

        if not kb_id:
            parser.print_help()
            print("\n❌ 错误: 请指定 --kb-id 或 --kb-name 参数")
            return

        # 获取并显示文档
        docs = lister.list_documents(kb_id)

        if docs:
            lister.display_documents(docs, format_type=args.format, brief=args.brief)

            # 保存到文件
            if args.output:
                lister.save_to_file(docs, args.output, format_type=args.format)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
