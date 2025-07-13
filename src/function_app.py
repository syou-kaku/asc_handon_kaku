import re
import json
import logging
import azure.functions as func
from typing import List, Dict

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# 映画一覧取得ツール用プロパティ定義
tool_properties_get_movie_list = json.dumps([
    {"propertyName": "date", "propertyType": "string", "description": "上映日（YYYY-MM-DD, 任意）"},
    {"propertyName": "title_query", "propertyType": "string", "description": "映画タイトルの曖昧検索クエリ（任意）"}
])

# Blobパス定義
MOVIES_BLOB_PATH = "movies/movies.json"
SHOWTIMES_BLOB_PATH = "movies/showtimes.json"

def _parse_context_args(context) -> Dict:
    try:
        content = json.loads(context)
        return content.get("arguments", {})
    except Exception:
        return {}

def _validate_date(date_str: str) -> bool:
    if not date_str:
        return True
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_str))

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_movie_list",
    description="映画一覧を取得する。date指定でその日に上映される映画のみ返す。title_query指定で曖昧検索も可能。",
    toolProperties=tool_properties_get_movie_list,
)
@app.generic_input_binding(arg_name="moviesblob", type="blob", connection="AzureWebJobsStorage", path=MOVIES_BLOB_PATH)
@app.generic_input_binding(arg_name="showtimesblob", type="blob", connection="AzureWebJobsStorage", path=SHOWTIMES_BLOB_PATH)
def get_movie_list(moviesblob: func.InputStream, showtimesblob: func.InputStream, context) -> str:
    """
    映画一覧を取得するMCPツール。date指定でその日に上映される映画のみ返す。title_query指定で曖昧検索も可能。
    """
    args = _parse_context_args(context)
    date = args.get("date")
    title_query = args.get("title_query")

    # バリデーション
    if date and not _validate_date(date):
        return json.dumps({"error": "dateはYYYY-MM-DD形式で指定してください。"})


    try:
        movies = json.loads(moviesblob.read().decode("utf-8"))
    except Exception as e:
        return json.dumps({"error": f"movies.jsonの読み込みに失敗: {str(e)}"})

    # date指定時はshowtimes.jsonから該当movie_idを抽出
    if date:
        try:
            showtimes = json.loads(showtimesblob.read().decode("utf-8"))
            movie_ids = set(st["movie_id"] for st in showtimes if st["start_time"].startswith(date))
            movies = [m for m in movies if m["movie_id"] in movie_ids]
        except Exception as e:
            return json.dumps({"error": f"showtimes.jsonの読み込みに失敗: {str(e)}"})

    # title_query指定時は部分一致・大文字小文字無視
    if title_query:
        q = title_query.lower()
        movies = [m for m in movies if q in m["title"].lower()]

    return json.dumps({"movies": movies}, ensure_ascii=False)

# MCPツール用プロパティ定義（上映スケジュール取得）
tool_properties_get_show_schedule = json.dumps([
    {"propertyName": "date", "propertyType": "string", "description": "上映日（YYYY-MM-DD, 任意）"},
    {"propertyName": "movie_id", "propertyType": "string", "description": "映画ID（任意）"}
])

# 上映スケジュール取得機能
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


# Constants for the Azure Blob Storage container, file, and blob path
_SNIPPET_NAME_PROPERTY_NAME = "snippetname"
_SNIPPET_PROPERTY_NAME = "snippet"
_BLOB_PATH = "snippets/{mcptoolargs." + _SNIPPET_NAME_PROPERTY_NAME + "}.json"


class ToolProperty:
    def __init__(self, property_name: str, property_type: str, description: str):
        self.propertyName = property_name
        self.propertyType = property_type
        self.description = description

    def to_dict(self):
        return {
            "propertyName": self.propertyName,
            "propertyType": self.propertyType,
            "description": self.description,
        }


# Define the tool properties using the ToolProperty class
tool_properties_save_snippets_object = [
    ToolProperty(_SNIPPET_NAME_PROPERTY_NAME, "string", "The name of the snippet."),
    ToolProperty(_SNIPPET_PROPERTY_NAME, "string", "The content of the snippet."),
]

tool_properties_get_snippets_object = [ToolProperty(_SNIPPET_NAME_PROPERTY_NAME, "string", "The name of the snippet.")]

# Convert the tool properties to JSON
tool_properties_save_snippets_json = json.dumps([prop.to_dict() for prop in tool_properties_save_snippets_object])
tool_properties_get_snippets_json = json.dumps([prop.to_dict() for prop in tool_properties_get_snippets_object])


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="hello_mcp",
    description="Hello world.",
    toolProperties="[]",
)
def hello_mcp(context) -> None:
    """
    A simple function that returns a greeting message.

    Args:
        context: The trigger context (not used in this function).

    Returns:
        str: A greeting message.
    """
    return "Hello I am MCPTool!"


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_snippet",
    description="Retrieve a snippet by name.",
    toolProperties=tool_properties_get_snippets_json,
)
@app.generic_input_binding(arg_name="file", type="blob", connection="AzureWebJobsStorage", path=_BLOB_PATH)
def get_snippet(file: func.InputStream, context) -> str:
    """
    Retrieves a snippet by name from Azure Blob Storage.

    Args:
        file (func.InputStream): The input binding to read the snippet from Azure Blob Storage.
        context: The trigger context containing the input arguments.

    Returns:
        str: The content of the snippet or an error message.
    """
    snippet_content = file.read().decode("utf-8")
    logging.info(f"Retrieved snippet: {snippet_content}")
    return snippet_content


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="save_snippet",
    description="Save a snippet with a name.",
    toolProperties=tool_properties_save_snippets_json,
)
@app.generic_output_binding(arg_name="file", type="blob", connection="AzureWebJobsStorage", path=_BLOB_PATH)
def save_snippet(file: func.Out[str], context) -> str:
    content = json.loads(context)
    snippet_name_from_args = content["arguments"][_SNIPPET_NAME_PROPERTY_NAME]
    snippet_content_from_args = content["arguments"][_SNIPPET_PROPERTY_NAME]

    if not snippet_name_from_args:
        return "No snippet name provided"

    if not snippet_content_from_args:
        return "No snippet content provided"

    file.set(snippet_content_from_args)
    logging.info(f"Saved snippet: {snippet_content_from_args}")
    return f"Snippet '{snippet_content_from_args}' saved successfully"


# MCPツール用プロパティ定義（座席予約）
tool_properties_save_seat_reservation = json.dumps([
    {"propertyName": "showtime_id", "propertyType": "string", "description": "上映スケジュールID（必須）"},
    {"propertyName": "seat_id", "propertyType": "string", "description": "座席ID（必須）"}
])

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="save_seat_reservation",
    description="指定した上映回・座席IDで座席予約を行う。",
    toolProperties=tool_properties_save_seat_reservation,
)
@app.generic_input_binding(arg_name="seatsblob", type="blob", connection="AzureWebJobsStorage", path="movies/seats_{mcptoolargs.showtime_id}.json")
@app.generic_output_binding(arg_name="seatsout", type="blob", connection="AzureWebJobsStorage", path="movies/seats_{mcptoolargs.showtime_id}.json")
def save_seat_reservation(seatsblob: func.InputStream, seatsout: func.Out[str], context) -> str:
    args = _parse_context_args(context)
    showtime_id = args.get("showtime_id")
    seat_id = args.get("seat_id")
    if not showtime_id or not seat_id:
        return json.dumps({"error": "showtime_idとseat_idは必須です。"})
    try:
        seats = json.loads(seatsblob.read().decode("utf-8"))
    except Exception as e:
        return json.dumps({"error": f"seats_{showtime_id}.jsonの読み込みに失敗: {str(e)}"})
    if seat_id not in seats:
        return json.dumps({"error": f"座席ID {seat_id} は既に予約済みか存在しません。"})
    seats.remove(seat_id)
    try:
        seatsout.set(json.dumps(seats, ensure_ascii=False))
    except Exception as e:
        return json.dumps({"error": f"座席予約の保存に失敗: {str(e)}"})
    return json.dumps({"message": f"座席 {seat_id} の予約が完了しました。"})


# MCPツール用プロパティ定義（予約詳細確認）
tool_properties_get_reservation_detail = json.dumps([
    {"propertyName": "showtime_id", "propertyType": "string", "description": "上映スケジュールID（必須）"},
    {"propertyName": "seat_id", "propertyType": "string", "description": "座席ID（必須）"}
])

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_reservation_detail",
    description="指定した上映回・座席IDの予約状況を確認する。",
    toolProperties=tool_properties_get_reservation_detail,
)
@app.generic_input_binding(arg_name="seatsblob", type="blob", connection="AzureWebJobsStorage", path="movies/seats_{mcptoolargs.showtime_id}.json")
def get_reservation_detail(seatsblob: func.InputStream, context) -> str:
    args = _parse_context_args(context)
    showtime_id = args.get("showtime_id")
    seat_id = args.get("seat_id")
    if not showtime_id or not seat_id:
        return json.dumps({"error": "showtime_idとseat_idは必須です。"})
    try:
        seats = json.loads(seatsblob.read().decode("utf-8"))
    except Exception as e:
        return json.dumps({"error": f"seats_{showtime_id}.jsonの読み込みに失敗: {str(e)}"})
    if seat_id in seats:
        return json.dumps({"reserved": False, "message": f"座席 {seat_id} は予約可能です。"})
    else:
        return json.dumps({"reserved": True, "message": f"座席 {seat_id} は既に予約済みです。"})
