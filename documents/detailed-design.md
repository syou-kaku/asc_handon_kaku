# 映画館窓口業務エージェント 詳細設計書

## 1. 前提
- データはAzure Blob Storageの`movies`コンテナ配下のjsonファイルとして管理する。
- 各種データ（映画、上映スケジュール、座席、予約）はBlob上のjsonファイルを読み書きすることで実現する。
- Blobへのアクセスは既存の`get_snippet`/`save_snippet` MCPツールの実装方式を踏襲する。
- 予約データは`src/data/reservations.jsonl`にJSON Lines形式で追記保存する。
- 各MCPツールはリクエストパラメータの最低限のバリデーションを行う。

## 2. 機能詳細

### 2.1 映画一覧提示ツール（list_movies）
#### 処理フロー
1. リクエストパラメータ（date, title_query）をバリデーション。
2. Azure Blob Storageの`movies/movies.json`を取得。
3. date指定があれば、同じく`movies/showtimes.json`を取得し、該当日付に上映される映画IDのみ抽出。
4. title_queryがあれば、曖昧検索（部分一致・類似度判定）で候補映画を抽出。
5. 条件に合致する映画リストをレスポンスとして返却。

### 2.2 上映時間枠選択ツール（list_showtimes）
#### 処理フロー
1. リクエストパラメータ（movie_id, date）をバリデーション。
2. Azure Blob Storageの`movies/showtimes.json`を取得。
3. movie_id・dateで該当する上映枠を抽出。
4. 各上映枠の空席数は、`movies/seats_{showtime_id}.json`を取得し、is_reserved=falseの件数で算出。
5. 上映枠リストをレスポンスとして返却。

### 2.3 座席空き状況提示ツール（list_available_seats）
#### 処理フロー
1. リクエストパラメータ（showtime_id）をバリデーション。
2. Azure Blob Storageの`movies/seats_{showtime_id}.json`を取得。
3. is_reserved=falseの座席のみ抽出し、レスポンスとして返却。

### 2.4 座席予約確定ツール（reserve_seats）
#### 処理フロー
1. リクエストパラメータ（user_id, showtime_id, seat_ids）をバリデーション。
2. `movies/seats_{showtime_id}.json`を取得。
3. seat_idsのうちis_reserved=falseの席のみ予約可能と判定。
4. 予約可能な席のis_reservedをtrueに更新し、Blobへ保存。
5. 予約情報（reservation_id, user_id, showtime_id, seats, reserved_at）を生成し、`src/data/reservations.jsonl`に追記保存。
6. 予約内容をレスポンスとして返却。

### 2.5 対話履歴管理ツール（record_conversation, get_conversation_history）
#### (a) record_conversation
1. リクエストパラメータ（conversation_id, user_id, message）をバリデーション。
2. `movies/conversation_{conversation_id}.json`を取得（なければ新規作成）。
3. messageをhistoryリストに追加し、Blobへ保存。
4. 成功レスポンスを返却。

#### (b) get_conversation_history
1. リクエストパラメータ（conversation_id）をバリデーション。
2. `movies/conversation_{conversation_id}.json`を取得。
3. historyリストをレスポンスとして返却。

## 3. Blobアクセス設計
- Azure FunctionsのバインディングまたはAzure SDKを利用し、`movies`コンテナ配下の各jsonファイルを読み書きする。
- get_snippet/save_snippetの実装例に倣い、ファイル名・パスはパラメータから動的に組み立てる。
- 読み込み時は存在チェック・エラー処理を行う。
- 書き込み時は排他制御（楽観ロック等）を考慮する。

## 4. バリデーション方針
- 必須パラメータの有無、型チェック、値の妥当性（日付フォーマット、ID存在確認等）を最低限実施。
- 不正な場合はエラーレスポンスを返却。

## 5. 予約データの保存
- 予約確定時、`src/data/reservations.jsonl`に1予約1行のJSONとして追記保存。
- 予約情報にはreservation_id, user_id, showtime_id, seats, reserved_atを含める。

---

本設計書に基づき、各MCPツールの実装を進める。
