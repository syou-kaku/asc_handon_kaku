# 映画館窓口業務エージェント 要件定義書

## 1. 概要
本システムは、映画館の発券窓口業務を自動化するエージェント（MCPツール群）をAzure Functions上で実現することを目的とします。ユーザーとの対話を通じて、映画の選択、座席予約、予約確定までの一連の業務をサポートします。

## 2. 機能一覧と要件

### 2.1 映画一覧提示機能
- ユーザーに現在上映中の映画の一覧を提示する。
- 日時指定があれば、その日時に上映される映画のみを提示する。
- 映画の内容や評価をユーザーに推薦・説明できる。
- ユーザーの曖昧な入力（例：映画名の揺れ）にも対応し、候補を補正・提示する。

### 2.2 上映時間枠選択機能
- ユーザーが希望する上映日時を指定できる。
- 指定日時に該当する映画・時間枠を提示する。

### 2.3 座席空き状況提示機能
- 映画と時間枠が確定した後、その枠で空いている座席を一覧で提示する。
- 複数席の同時選択に対応する。

### 2.4 座席予約確定機能
- ユーザーが選択した座席の予約を確定する。
- 予約確定後、ユーザーに予約内容を通知する。

### 2.5 対話管理・補助機能
- ユーザーとの対話履歴を管理し、業務フローをガイドする。
- 必要に応じて映画の推薦や説明を行う。

## 3. 管理データ構造

### 3.1 映画情報（Movie）
- movie_id: string
- title: string
- description: string
- rating: float
- showtimes: List[Showtime]

### 3.2 上映時間枠（Showtime）
- showtime_id: string
- movie_id: string
- start_time: datetime
- available_seats: List[Seat]

### 3.3 座席情報（Seat）
- seat_id: string
- row: string
- number: int
- is_reserved: bool

### 3.4 予約情報（Reservation）
- reservation_id: string
- user_id: string
- showtime_id: string
- seats: List[Seat]
- reserved_at: datetime

### 3.5 ユーザー情報（User）
- user_id: string
- name: string
- contact_info: string

### 3.6 対話履歴（Conversation）
- conversation_id: string
- user_id: string
- history: List[Message]

### 3.7 メッセージ（Message）
- message_id: string
- sender: string (user/agent)
- content: string
- timestamp: datetime

## 4. 非機能要件
- 決済処理は本システムの対象外とする。
- Azure Functions v2 Pythonモデルを利用し、拡張性・保守性を考慮する。
- MCPクライアントツールからの呼び出しに対応するAPI設計とする。

---
本要件定義書に基づき、今後の設計・実装を進めます。
