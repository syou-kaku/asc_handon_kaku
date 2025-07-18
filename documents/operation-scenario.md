# 映画館の発券窓口
## 業務内容
このシナリオでは以下のような業務を行います。
1. ユーザーが見たい映画と上映時間枠を対話的に確定する
- ユーザーに現在上映中の映画の一覧を提示する。
- 先に日時を指定した場合、その日の映画の一覧を提示する。
- 必要に応じて映画の内容や評価について、ユーザーに推薦することもある。
- ユーザーは映画名を完全に正確に指定しないこともあり、多少の揺れはあるため補正する。
2. ユーザーに空いている座席を提示し、指定してもらう
- 映画と時間枠が確定したらその枠で空いている座席を提示する。
- ユーザーに席を選んでもらう。ここで、ユーザーは複数の席を選ぶこともありうる。
3. 座席予約を確定する
- ユーザーが指定した座席の予約を確定する。
- 予約が確定したらユーザーに予約が確定した旨を伝える。
## 備考
- ここでの業務想定では決済は行わないものとする。
