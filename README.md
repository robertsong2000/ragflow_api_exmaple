# RAGFlow API Example

这是一个用于与 RAGFlow 知识库系统进行交互的 Python 示例项目。

## 功能特性

- 📚 列出所有知识库
- 📋 查看指定知识库中的所有文档
- 🔍 支持通过知识库 ID 或名称查询
- 📊 多种输出格式（表格、JSON、CSV）
- 💾 支持导出到文件

## 安装

### 环境要求

- Python 3.7+

### 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `ragflow_config.json` 配置文件：

```json
{
  "api_url": "http://your-ragflow-server:1800/api/v1",
  "api_key": "your-api-key-here"
}
```

或者通过环境变量设置：

```bash
export RAGFLOW_API_URL="http://your-ragflow-server:1800/api/v1"
export RAGFLOW_API_KEY="your-api-key-here"
```

## 使用方法

### 列出所有知识库

```bash
python list_kb_documents.py --list-kbs
```

### 查看指定知识库的文档（通过 ID）

```bash
python list_kb_documents.py --kb-id <知识库ID>
```

### 查看指定知识库的文档（通过名称）

```bash
python list_kb_documents.py --kb-name "<知识库名称>"
```

### 以不同格式输出

```bash
# JSON 格式
python list_kb_documents.py --kb-id <知识库ID> --format json

# CSV 格式
python list_kb_documents.py --kb-id <知识库ID> --format csv
```

### 导出到文件

```bash
# 导出为 JSON
python list_kb_documents.py --kb-id <知识库ID> --output documents.json --format json

# 导出为 CSV
python list_kb_documents.py --kb-id <知识库ID> --output documents.csv --format csv

# 导出为文本
python list_kb_documents.py --kb-id <知识库ID> --output documents.txt
```

### 使用自定义配置文件

```bash
python list_kb_documents.py --config /path/to/config.json --kb-id <知识库ID>
```

### 覆盖配置文件中的 API 地址和密钥

```bash
python list_kb_documents.py --api-url "http://localhost:9380" --api-key "your-key" --kb-id <知识库ID>
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--kb-id` | 知识库 ID |
| `--kb-name` | 知识库名称（支持模糊匹配） |
| `--list-kbs` | 列出所有知识库 |
| `--format` | 输出格式（table/json/csv，默认：table） |
| `--output` | 输出文件路径 |
| `--config` | 配置文件路径（默认：ragflow_config.json） |
| `--api-url` | RAGFlow API 地址（覆盖配置文件） |
| `--api-key` | RAGFlow API 密钥（覆盖配置文件） |

## 示例输出

### 表格格式
```
====================================================================================================
序号   文档ID                        文档名称                                 Chunks     状态          大小
====================================================================================================
1      doc_123..                    示例文档.pdf                             150        ✅ SUCCESS    2.45 MB
2      doc_456..                    技术文档.docx                            89         ✅ SUCCESS    1.12 MB
====================================================================================================
```

### JSON 格式
```json
[
  {
    "document_id": "doc_123",
    "name": "示例文档.pdf",
    "chunk_count": 150,
    "status": "SUCCESS",
    "size": 2568192
  }
]
```

## 注意事项

- ⚠️ 请勿将 `ragflow_config.json` 提交到版本控制系统
- 🔒 API 密钥请妥善保管
- 📝 知识库名称查询支持模糊匹配
- 🔄 分页查询会自动处理，无需手动指定页码

## 许可证

MIT License
