# 座席空き状況取得機能（get_seat_availability）

## 1. 前提条件
- 本機能は Azure Functions v2 Python プログラミングモデルで実装する。
- Azure Blob Storage の movies コンテナ配下にある seats_{showtime_id}.json を参照する。
- バインディングは Azure Functions の Input Binding（blob）を利用する。
- Azure Functions のバインディング名は英数字のみ（アンダースコア不可）とする。
- MCPツールとして generic_trigger を利用し、引数は context 経由で受け取る。
- MCPツールのプロパティ定義は既存の形式に準拠する。
- showtime_id を arguments として context から取得する。
- 取得結果は JSON 形式で返却する。

## 2. 共通仕様
- 例外発生時はエラーメッセージを JSON で返却する。
- バインディング経由で取得したファイルは UTF-8 でデコードする。
- MCPツールのデコレーターやバインディングの記述方法は get_snippet/save_snippet に準拠する。

## 3. get_seat_availability 機能詳細
### 3.1 入力
- showtime_id: string（必須）

### 3.2 出力
- 指定した上映回の座席空き状況（JSON配列）
- 例外時は {"error": "..."} 形式

### 3.3 ロジック
1. context から arguments を取得
2. showtime_id を抽出
3. showtime_id 未指定時はエラー返却
4. seats_{showtime_id}.json を blob input binding で取得
5. ファイル内容を返却

### 3.4 バインディング
- arg_name: seatsblob
- type: blob
- connection: AzureWebJobsStorage
- path: movies/seats_{showtime_id}.json

### 3.5 MCPツールデコレーター
- toolName: get_seat_availability
- description: 指定した上映回の座席空き状況を取得する。
- toolProperties: showtime_id

---

# 実装例（function_app.py への追加コード）

```python
# MCPツール用プロパティ定義（座席空き状況取得）
tool_properties_get_seat_availability = json.dumps([
    {"propertyName": "showtime_id", "propertyType": "string", "description": "上映スケジュールID（必須）"}
])

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_seat_availability",
    description="指定した上映回の座席空き状況を取得する。",
    toolProperties=tool_properties_get_seat_availability,
)
@app.generic_input_binding(arg_name="seatsblob", type="blob", connection="AzureWebJobsStorage", path="movies/seats_{mcptoolargs.showtime_id}.json")
def get_seat_availability(seatsblob: func.InputStream, context) -> str:
    args = _parse_context_args(context)
    showtime_id = args.get("showtime_id")
    if not showtime_id:
        return json.dumps({"error": "showtime_idは必須です。"})
    try:
        seats = json.loads(seatsblob.read().decode("utf-8"))
    except Exception as e:
        return json.dumps({"error": f"seats_{showtime_id}.jsonの読み込みに失敗: {str(e)}"})
    return json.dumps({"seats": seats}, ensure_ascii=False)
```
