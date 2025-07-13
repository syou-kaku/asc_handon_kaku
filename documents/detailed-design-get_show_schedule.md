# 上映スケジュール取得機能（get_show_schedule）

## 1. 前提条件
- 本機能は Azure Functions v2 Python プログラミングモデルで実装する。
- Azure Blob Storage の movies コンテナ配下にある showtimes.json を参照する。
- バインディングは Azure Functions の Input Binding（blob）を利用する。
- Azure Functions のバインディング名は英数字のみ（アンダースコア不可）とする。
- MCPツールとして generic_trigger を利用し、引数は context 経由で受け取る。
- MCPツールのプロパティ定義は既存の形式に準拠する。
- 日付や映画IDなどの検索条件は arguments として context から取得する。
- 取得結果は JSON 形式で返却する。

## 2. 共通仕様
- 例外発生時はエラーメッセージを JSON で返却する。
- 日付は "YYYY-MM-DD" 形式でバリデーションを行う。
- バインディング経由で取得したファイルは UTF-8 でデコードする。
- MCPツールのデコレーターやバインディングの記述方法は get_snippet/save_snippet に準拠する。

## 3. get_show_schedule 機能詳細
### 3.1 入力
- date: string（任意、YYYY-MM-DD形式）
- movie_id: string（任意）

### 3.2 出力
- 指定条件に合致する上映スケジュール一覧（JSON配列）
- 例外時は {"error": "..."} 形式

### 3.3 ロジック
1. context から arguments を取得
2. date, movie_id を抽出
3. date 指定時はバリデーション（YYYY-MM-DD形式）
4. showtimes.json を blob input binding で取得
5. 条件に合致するスケジュールのみ抽出
6. 結果を JSON で返却

### 3.4 バインディング
- arg_name: showtimesblob
- type: blob
- connection: AzureWebJobsStorage
- path: movies/showtimes.json

### 3.5 MCPツールデコレーター
- toolName: get_show_schedule
- description: 上映スケジュール一覧を取得する。dateやmovie_idで絞り込み可能。
- toolProperties: date, movie_id

---

# 実装例（function_app.py への追加コード）

```python
# MCPツール用プロパティ定義
tool_properties_get_show_schedule = json.dumps([
    {"propertyName": "date", "propertyType": "string", "description": "上映日（YYYY-MM-DD, 任意）"},
    {"propertyName": "movie_id", "propertyType": "string", "description": "映画ID（任意）"}
])

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_show_schedule",
    description="上映スケジュール一覧を取得する。dateやmovie_idで絞り込み可能。",
    toolProperties=tool_properties_get_show_schedule,
)
@app.generic_input_binding(arg_name="showtimesblob", type="blob", connection="AzureWebJobsStorage", path=SHOWTIMES_BLOB_PATH)
def get_show_schedule(showtimesblob: func.InputStream, context) -> str:
    args = _parse_context_args(context)
    date = args.get("date")
    movie_id = args.get("movie_id")

    # バリデーション
    if date and not _validate_date(date):
        return json.dumps({"error": "dateはYYYY-MM-DD形式で指定してください。"})

    try:
        showtimes = json.loads(showtimesblob.read().decode("utf-8"))
    except Exception as e:
        return json.dumps({"error": f"showtimes.jsonの読み込みに失敗: {str(e)}"})

    # フィルタリング
    if date:
        showtimes = [s for s in showtimes if s["start_time"].startswith(date)]
    if movie_id:
        showtimes = [s for s in showtimes if s["movie_id"] == movie_id]

    return json.dumps({"showtimes": showtimes}, ensure_ascii=False)
```
