# 映画館窓口業務エージェント インタフェース仕様書

本ドキュメントは、要件定義書および業務シナリオに基づき、MCPツールとして実装する各機能のインタフェース仕様をJSON-RPC形式で定義します。

## 1. MCPツール一覧

1. 映画一覧提示ツール（list_movies）
2. 上映時間枠選択ツール（list_showtimes）
3. 座席空き状況提示ツール（list_available_seats）
4. 座席予約確定ツール（reserve_seats）
5. 対話履歴管理ツール（record_conversation, get_conversation_history）

---

## 2. 各ツールのインタフェース定義

### 2.1 映画一覧提示ツール（list_movies）
- 概要: 指定日時に上映中の映画一覧を取得し、曖昧な映画名にも対応。
- メソッド名: `list_movies`
- リクエスト:
```json
{
  "jsonrpc": "2.0",
  "method": "list_movies",
  "params": {
    "date": "2025-07-13", // 任意。指定がなければ全上映中映画
    "title_query": "string" // 任意。曖昧な映画名も可
  },
  "id": 1
}
```
- レスポンス:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "movies": [
      {
        "movie_id": "string",
        "title": "string",
        "description": "string",
        "rating": 4.5
      }
    ]
  }
}
```

### 2.2 上映時間枠選択ツール（list_showtimes）
- 概要: 指定映画・日付の上映時間枠一覧を取得。
- メソッド名: `list_showtimes`
- リクエスト:
```json
{
  "jsonrpc": "2.0",
  "method": "list_showtimes",
  "params": {
    "movie_id": "string",
    "date": "2025-07-13" // 任意
  },
  "id": 2
}
```
- レスポンス:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "showtimes": [
      {
        "showtime_id": "string",
        "movie_id": "string",
        "start_time": "2025-07-13T14:00:00",
        "available_seats_count": 30
      }
    ]
  }
}
```

### 2.3 座席空き状況提示ツール（list_available_seats）
- 概要: 指定上映時間枠の空席一覧を取得。
- メソッド名: `list_available_seats`
- リクエスト:
```json
{
  "jsonrpc": "2.0",
  "method": "list_available_seats",
  "params": {
    "showtime_id": "string"
  },
  "id": 3
}
```
- レスポンス:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "seats": [
      {
        "seat_id": "string",
        "row": "A",
        "number": 5,
        "is_reserved": false
      }
    ]
  }
}
```

### 2.4 座席予約確定ツール（reserve_seats）
- 概要: 指定座席の予約を確定。
- メソッド名: `reserve_seats`
- リクエスト:
```json
{
  "jsonrpc": "2.0",
  "method": "reserve_seats",
  "params": {
    "user_id": "string",
    "showtime_id": "string",
    "seat_ids": ["string", "string"]
  },
  "id": 4
}
```
- レスポンス:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "reservation_id": "string",
    "reserved_at": "2025-07-13T14:05:00",
    "seats": [
      {
        "seat_id": "string",
        "row": "A",
        "number": 5
      }
    ]
  }
}
```

### 2.5 対話履歴管理ツール
#### (a) 対話履歴記録（record_conversation）
- メソッド名: `record_conversation`
- リクエスト:
```json
{
  "jsonrpc": "2.0",
  "method": "record_conversation",
  "params": {
    "conversation_id": "string",
    "user_id": "string",
    "message": {
      "sender": "user",
      "content": "string",
      "timestamp": "2025-07-13T14:00:00"
    }
  },
  "id": 5
}
```
- レスポンス:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "success": true
  }
}
```
#### (b) 対話履歴取得（get_conversation_history）
- メソッド名: `get_conversation_history`
- リクエスト:
```json
{
  "jsonrpc": "2.0",
  "method": "get_conversation_history",
  "params": {
    "conversation_id": "string"
  },
  "id": 6
}
```
- レスポンス:
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "history": [
      {
        "message_id": "string",
        "sender": "user",
        "content": "string",
        "timestamp": "2025-07-13T14:00:00"
      }
    ]
  }
}
```

---

## 3. データ構造

各ツールのリクエスト・レスポンスで利用するデータ構造は要件定義書の管理データ構造（Movie, Showtime, Seat, Reservation, User, Conversation, Message）に準拠します。

## 4. 備考
- すべてのインタフェースはJSON-RPC 2.0形式で設計されています。
- 必要に応じてパラメータやレスポンス項目は拡張可能です。
- 決済処理は対象外です。
