# MCP Directory Local

A small, dependency-free local registry for organizing, searching, validating, and exporting Model Context Protocol (MCP) server configurations. It stores metadata only: **it never launches stored commands or connects to stored URLs**.

## English

### Why this exists
MCP clients often use separate configuration files. Once you test several local and remote servers, remembering names, transports, commands, and purposes becomes awkward. MCP Directory Local provides one portable registry and a predictable CLI without turning configuration discovery into execution.

### Features
- Register `stdio`, `http`, and `https` MCP endpoints.
- Search by name, description, tag, or transport.
- Show and remove entries; explicitly replace duplicates.
- Export all or selected entries as the common `{ "mcpServers": ... }` client shape.
- Strict schema validation and duplicate-name detection.
- Atomic registry writes through a temporary sibling file.
- Deterministic ordering for clean diffs.
- JSON output for inspection/automation.
- Python API and `python -m mcp_directory` support.
- Standard-library runtime: no third-party dependencies.

### Preview
```text
$ mcp-directory --registry registry.json find local
filesystem-local  stdio  filesystem, local  Example local filesystem MCP server entry...

$ mcp-directory --registry registry.json validate
OK: 1 server(s)
```
No screenshot is required because this is a terminal application; the commands above represent the primary interface.

### Requirements & installation
Requires Python 3.10+.

```bash
git clone https://github.com/rad03i2/mcp-directory-local.git
cd mcp-directory-local
python -m pip install -e .
```

### Usage
Use an explicit project registry or omit `--registry` to use `~/.mcp-directory.json`.

```bash
mcp-directory --registry registry.json add examples/filesystem.json
mcp-directory --registry registry.json find filesystem
mcp-directory --registry registry.json find --tag local --transport stdio
mcp-directory --registry registry.json show filesystem-local
mcp-directory --registry registry.json export filesystem-local
mcp-directory --registry registry.json export --output mcp-client.json
mcp-directory --registry registry.json validate
mcp-directory --registry registry.json remove filesystem-local
```

A server entry looks like:
```json
{
  "name": "filesystem-local",
  "description": "Local filesystem tools",
  "transport": "stdio",
  "command": "your-installed-command",
  "args": [],
  "tags": ["filesystem", "local"]
}
```
For HTTP transports use `url` instead of `command`/`args`. The URL scheme must match `http` or `https`.

### Python API
```python
from mcp_directory import Directory, validate_server

registry = Directory.load("registry.json")
registry.add(validate_server({
    "name": "clock",
    "description": "Local clock tools",
    "transport": "stdio",
    "command": "clock-mcp",
    "args": [],
    "tags": ["time"]
}))
registry.save("registry.json")
print(registry.export_client_config(["clock"]))
```

### Configuration and data format
Registry files are UTF-8 JSON with `version: 1` and a `servers` array. Names are restricted to 1–64 letters, digits, `.`, `_`, or `-` (starting with a letter/digit). Descriptions are limited to 500 characters. Tags are normalized to lowercase and deduplicated. This project intentionally has no `.env` file because it does not need credentials.

### Project structure
```text
src/mcp_directory/core.py   validation, persistence, search, export
src/mcp_directory/cli.py    command-line interface
examples/                   safe synthetic configuration
 tests/                     core and CLI tests
.github/workflows/ci.yml    cross-platform CI
```

### Testing
```bash
python -m compileall -q src tests
python -m unittest discover -s tests -v
```
CI runs these checks on Python 3.10, 3.12, and 3.13 across Linux, Windows, and macOS.

### Security & privacy
The tool is local-only and has no network code, telemetry, command execution, or secret handling. **Do not put tokens, passwords, API keys, or authorization headers in registry entries.** Exported files contain the stored command arguments and URLs. Review them before sharing. See [SECURITY.md](SECURITY.md).

### Limitations
This is a registry/configuration utility, not an MCP protocol inspector or server manager. It does not start servers, perform MCP handshakes, discover tools/resources/prompts, test endpoint reachability, interpolate environment variables, or manage credentials. Client-specific configuration formats may require adaptation after export.

### Optional roadmap
Potential future additions include import adapters for popular clients, schema migrations, and redacted inventory reports. They are not required for the current core workflow.

### Contributing & license
See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

## العربية

### نظرة عامة
**MCP Directory Local** أداة محلية خفيفة وبدون اعتماديات خارجية لتنظيم إعدادات خوادم Model Context Protocol والبحث فيها والتحقق منها وتصديرها. تحفظ الأداة بيانات الإعداد فقط، ولا تشغّل الأوامر المخزنة ولا تتصل بالروابط المخزنة.

### لماذا المشروع؟
عند استخدام عدة خوادم MCP يصبح تتبع الاسم والنقل والأمر والغرض من كل خادم موزعًا بين إعدادات العملاء. يوفر المشروع سجلاً محليًا واحدًا وواجهة أوامر واضحة مع فصل متعمد بين **إدارة الإعداد** و**تنفيذ الخادم**.

### المزايا
- تسجيل خوادم `stdio` و`http` و`https`.
- البحث بالاسم والوصف والوسم ونوع النقل.
- عرض الإدخالات وحذفها واستبدال المكرر بصورة صريحة.
- تصدير الكل أو أسماء محددة بصيغة `mcpServers` الشائعة.
- تحقق صارم من البنية ومنع الأسماء المكررة.
- كتابة ذرية للسجل وترتيب ثابت يسهل مراجعة الفروقات.
- إخراج JSON وواجهة Python وتشغيل عبر `python -m mcp_directory`.
- لا توجد اعتماديات تشغيل خارج مكتبة Python القياسية.

### المعاينة والتثبيت
المشروع أداة طرفية، لذلك لا يحتاج إلى لقطة شاشة. يتطلب Python 3.10 أو أحدث:
```bash
git clone https://github.com/rad03i2/mcp-directory-local.git
cd mcp-directory-local
python -m pip install -e .
```

### الاستخدام
```bash
mcp-directory --registry registry.json add examples/filesystem.json
mcp-directory --registry registry.json find --tag local
mcp-directory --registry registry.json show filesystem-local
mcp-directory --registry registry.json export --output mcp-client.json
mcp-directory --registry registry.json validate
```
إذا حذفت `--registry` يستخدم البرنامج الملف `~/.mcp-directory.json`. لخوادم `stdio` استخدم `command` و`args`، ولـHTTP/HTTPS استخدم `url` مع مخطط مطابق لنوع النقل.

### الإعداد وواجهة Python
ملف السجل JSON بترميز UTF-8 ويحتوي `version: 1` ومصفوفة `servers`. الأسماء محدودة بمحارف آمنة، والأوصاف حتى 500 محرف، والوسوم تتحول إلى أحرف صغيرة وتزال تكراراتها. لا يوجد `.env.example` لأن المشروع لا يحتاج أسرارًا أو متغيرات بيئة.

يمكن استخدام `Directory` و`validate_server` مباشرة من الحزمة كما في المثال الإنجليزي أعلاه.

### بنية المشروع والاختبارات
المحرك في `src/mcp_directory/core.py`، وCLI في `cli.py`، والأمثلة في `examples/`، والاختبارات في `tests/`. للتأكد محليًا:
```bash
python -m compileall -q src tests
python -m unittest discover -s tests -v
```
ويشغّل CI الاختبارات على Linux وWindows وmacOS مع عدة إصدارات Python.

### الأمان والخصوصية
الأداة محلية ولا تحتوي على اتصالات شبكة أو telemetry أو تنفيذ أوامر أو إدارة أسرار. **لا تضع كلمات مرور أو Tokens أو API keys أو Authorization headers داخل السجل.** ملفات التصدير تتضمن الأوامر والوسائط والروابط التي خزنتها، لذلك راجعها قبل مشاركتها. راجع [SECURITY.md](SECURITY.md).

### القيود
هذه أداة سجل وإعداد وليست MCP inspector أو مدير عمليات. لا تشغّل الخوادم، ولا تنفذ handshake، ولا تكتشف tools/resources/prompts، ولا تختبر الوصول إلى endpoint، ولا تدير credentials أو توسع متغيرات البيئة. بعض عملاء MCP قد يحتاجون تعديلاً بسيطًا على صيغة التصدير.

### التطوير الاختياري
يمكن مستقبلًا إضافة مستوردات لإعدادات عملاء مشهورين، وترحيل إصدارات schema، وتقارير inventory منقحة. هذه إضافات اختيارية وليست ميزات مدعاة حاليًا.

### المساهمة والترخيص
راجع [CONTRIBUTING.md](CONTRIBUTING.md). المشروع مرخص برخصة [MIT](LICENSE).

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
