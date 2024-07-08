# API ドキュメント

## Config

バックアップ対象（vCenter Server や NSX-T Manager）の接続情報に関するリソース

### `GET /api/v1/configs`

すべてのバックアップ対象（vCenter Server や NSX-T Manager）の接続情報を取得する

#### HTTP リクエスト

```
GET http://localhost:8088/api/v1/configs
```

#### パラメータ

なし

#### リクエストボディ

なし

#### レスポンス

- 成功時のステータスコード: `200 OK`

```
$ curl -s -L -X GET http://localhost:8088/api/v1/configs/ | jq -r
[
  {
    "product_type": "vcenter",
    "name": "golden-axe.vcenter1.example.com",
    "host": "192.168.10.100",
    "user": "administrator@vsphere.local",
    "password": "VMware123!",
    "description": "This is test.",
    "_id": "6278c691be1147770f14eb07"
  },
  {
    "product_type": "nsxmgr",
    "name": "golden-axe.nsxt1.example.com",
    "host": "192.168.10.101",
    "user": "admin",
    "password": "VMware123!",
    "description": null,
    "_id": "78c82cbe1147770f14eb0862"
  }
]
```

### `GET /api/v1/configs/<id>`

指定した ID に対応するバックアップ対象（vCenter Server や NSX-T Manager）の接続情報を取得する

#### HTTP リクエスト

```
GET http://localhost:8088/api/v1/configs/61f7aca91152ddda2b9f08c1
```

#### パラメータ

- `id`: (required)バックアップ対象のID

#### リクエストボディ

なし

#### レスポンス

- 成功時のステータスコード: `200 OK`

```
$ curl -s -L -X GET http://localhost:8088/api/v1/configs/6278c82cbe1147770f14eb08 | jq -r
{
  "product_type": "nsxmgr",
  "name": "golden-axe.nsxt1.example.com",
  "host": "192.168.10.101",
  "user": "admin",
  "password": "VMware123!",
  "description": "This is test.",
  "_id": "6278c82cbe1147770f14eb08"
}
```

### `POST /api/v1/configs`

リクエストボディで指定したバックアップ対象（vCenter Server や NSX-T Manager）の接続情報を作成する

#### HTTP リクエスト

```
POST http://localhost:8088/api/v1/configs
```

#### パラメータ

なし

#### リクエストボディ

- `product_type`: (required)バックアップ対象の製品タイプ（`vcenter`, `nsxmgr`）
- `name`: (required)バックアップ対象の名前
- `host`: (required)バックアップ対象のIPアドレスまたはFQDN
- `user`: (required)バックアップ対象に接続するためのユーザ名
- `password`: (required)バックアップ対象に接続するためのパスワード
- `description`: (optional)バックアップ対象の説明文

例）
```
{
  "product_type": "vcenter",
  "name": "golden-axe.vcenter1.example.com",
  "host": "192.168.10.100",
  "user": "administrator@vsphere.local",
  "password": "VMware123!",
  "description": "This is test."
}
```

#### レスポンス

- 成功時のステータスコード: `201 CREATED`

```
$ curl -L -X POST -H "Content-type: application/json" http://localhost:8088/api/v1/configs/ -d@- <<EOF
{
  "product_type": "vcenter",
  "name": "golden-axe.vcenter2.example.com",
  "host": "192.168.11.100",
  "user": "administrator@vsphere.local",
  "password": "VMware123!",
  "description": "This is test."
}
EOF
{"name":"golden-axe.vcenter2.example.com","product_type":"vcenter","host":"192.168.11.100","user":"administrator@vsphere.local","password":"VMware123!","description":"This is test.","_id":"6315c36bfa40d4da88b99d53"}
```

### `PUT /api/v1/configs/<id>`

指定した ID のバックアップ対象（vCenter Server や NSX-T Manager）の接続情報を更新する

#### HTTP リクエスト

```
PUT http://localhost:8088/api/v1/configs/61f7aca91152ddda2b9f08c1
```

#### パラメータ

- `id`: (required)バックアップ対象のID

#### リクエストボディ

- `product_type`: (required)バックアップ対象の製品タイプ（`vcenter`, `nsxmgr`）
- `name`: (required)バックアップ対象の名前
- `host`: (required)バックアップ対象のIPアドレスまたはFQDN
- `user`: (required)バックアップ対象に接続するためのユーザ名
- `password`: (required)バックアップ対象に接続するためのパスワード
- `description`: (optional)バックアップ対象の説明文

例）
```
{
  "product_type": "vcenter",
  "name": "golden-axe.vcenter3.example.com",
  "host": "192.168.10.100",
  "user": "administrator@vsphere.local",
  "password": "VMware123!",
  "description": "This was test."
}
```

#### レスポンス

- 成功時のステータスコード: `204 NO CONTENT`

```
$ curl -L -X PUT -H "Content-type: application/json" http://localhost:8088/api/v1/configs/6315c36bfa40d4da88b99d53 -d@- <<EOF
{
  "product_type": "vcenter",
  "name": "golden-axe.vcenter3.example.com",
  "host": "192.168.10.100",
  "user": "administrator@vsphere.local",
  "password": "VMware123!",
  "description": "This was test."
}
EOF
```


### `DELETE /api/v1/configs/<id>`

指定した ID に対応するバックアップ対象（vCenter Server や NSX-T Manager）の接続情報を削除

#### HTTPリクエスト

```
DELETE http://localhost:8088/api/v1/configs/61f7aca91152ddda2b9f08c1
```

#### パラメータ

- `id`: (required)バックアップ対象のID

#### リクエストボディ

なし

#### レスポンス

- 成功時のステータスコード: `204 NO CONTENT`

```
$ curl -L -X DELETE http://localhost:8000/api/v1/configs/6278c893be1147770f14eb09
```

## Artifact

バックアップジョブとバックアップデータに関するリソース

### `GET /api/v1/artifacts`

すべてのバックアップジョブ実行結果の一覧を取得する

#### HTTP リクエスト

```
GET http://localhost:8000/api/v1/artifacts
```

#### パラメータ

なし

#### リクエストボディ

なし

#### レスポンス

- 成功時のステータスコード: `200 OK`

```
$ curl -s -L -X GET http://localhost:8000/api/v1/artifacts | jq -r
[
  {
    "product_type": "vcenter",
    "name": "golden-axe.vcenter1.example.com",
    "timestamp": "2022-01-02T03:04:56Z",
    "product_version": "7.0.2.00500",
    "status": "succeeded",
    "size": "2.0G",
    "config_id": "6278c691be1147770f14eb07",
    "_id": "88d177f8a6899e2223f0c560"
  },
  {
    "product_type": "nsxmgr",
    "name": "golden-axe.nsxt1.example.com",
    "product_version": "XXXXXXX",
    "status": "error",
    "timestamp": "2022-03-04T05:06:07Z",
    "config_id": "78c82cbe1147770f14eb0862",
    "_id": "168ba018f8b2c78e4014eec3"
  },
  {
    "product_type": "vcenter",
    "name": "golden-axe.vcenter1.example.com",
    "product_version": "7.0.2.00500",
    "status": "in_progress",
    "config_id": "6278c691be1147770f14eb07",
    "_id": "836c4a6ccbfc179eacc90b93"
  }
]
```

### `GET /api/v1/artifacts/<id>`

バックアップジョブ実行状況の詳細を取得する

#### HTTP リクエスト

```
GET http://localhost:8000/api/v1/artifacts/88d177f8a6899e2223f0c560
```

#### パラメータ

- `id`: (required)バックアップジョブのID

#### リクエストボディ

なし

#### レスポンス

- 成功時のステータスコード: `200 OK`

# TODO: メッセージ内の URL の修正
```
$ curl -s -L -X GET http://localhost:8000/api/v1/artifacts/88d177f8a6899e2223f0c560 | jq -r .
{
  "product_type": "vcenter",
  "name": "golden-axe.vcenter1.example.com",
  "product_version": "7.0.2.00500",
  "status": "succeeded",
  "timestamp": "2022-01-02T03:04:56Z",
  "size": "2.0G",
  "messages": "Backup artifact has been saved at vCenter/sn_vc01.h2o-37-231.h2o.example.com/M_7.0.2.00500_20220102-030456_OJ2W4X3CPFPS65TNO4WWEYLDNN2XALLTMNZGS4DUOMXXMY3FNZ2GK4RPMJQWG23VOAXHG2A=",
  "artifact_credentials": {
    "location": "sftp://10.78.119.95:2222/backup/vCenter/sn_vc01.h2o-37-231.h2o.example.com/M_7.0.2.00500_20220102-030456_OJ2W4X3CPFPS65TNO4WWEYLDNN2XALLTMNZGS4DUOMXXMY3FNZ2GK4RPMJQWG23VOAXHG2A=",
    "user": "axe",
    "password": "6cdf1a61cb36e7c7"
  },
  "config_id": "6278c691be1147770f14eb07",
  "_id": "88d177f8a6899e2223f0c560"
}
```

```
$ curl -s -L -X GET http://localhost:8000/api/v1/artifacts/168ba018f8b2c78e4014eec3 | jq -r .
{
  "product_type": "nsxmgr",
  "name": "golden-axe.nsxt1.example.com",
  "product_version": "XXXXXXX",
  "status": "error",
  "timestamp": "2022-03-04T05:06:07Z",
  "messages": "API authentication failed.",
  "config_id": "78c82cbe1147770f14eb0862",
  "_id": "78c82cbe1147770f14eb0862"
}
```

```
$ curl -s -L -X GET http://localhost:8000/api/v1/artifacts/836c4a6ccbfc179eacc90b93 | jq -r .
{
  "product_type": "vcenter",
  "name": "golden-axe.vcenter1.example.com",
  "product_version": "7.0.2.00500",
  "status": "in_progress",
  "percentage": "18",
  "messages": "Backup data transfer is in progress.",
  "config_id": "6278c691be1147770f14eb07",
  "_id": "836c4a6ccbfc179eacc90b93"
}
```

### `POST /api/v1/artifacts`

リクエストボディで指定したバックアップ対象（vCenter Server や NSX-T Manager）のバックアップを即時開始する

#### HTTP リクエスト

```
POST http://localhost:8000/api/v1/artifacts
```

#### パラメータ

なし

#### リクエストボディ

- `config_id`: (required)バックアップ対象のID

例）
```
{
  "config_id": "61f7aca91152ddda2b9f08c1"
}
```

#### レスポンス

- 成功時のステータスコード: `201 CREATED`
  - レスポンスボディにバックアップジョブのIDを含む

```
$ curl -L -X POST -H "Content-type: application/json" http://localhost:8000/api/v1/artifacts -d@- <<EOF
{
  "config_id": "61f7aca91152ddda2b9f08c1"
}
EOF
{"name":"golden-axe.vcenter2.example.com","product_type":"vcenter","status":"starting","config_id": "61f7aca91152ddda2b9f08c1","_id":"6278c893be1147770f14eb09"}
```

### `DELETE /api/v1/artifacts/<id>`

バックアップデータを含めてバックアップジョブを削除する

#### HTTP リクエスト

```
DELETE http://localhost:8000/api/v1/artifacts/6278c691be1147770f14eb07
```

#### パラメータ

- `id`: (required)バックアップジョブのID

#### リクエストボディ

なし

#### レスポンス

- 成功時のステータスコード: `204 NO CONTENT`

```
$ curl -L -X DELETE http://localhost:8000/api/v1/artifacts/6278c893be1147770f14eb09
```

- 削除対象のバックアップが存在しない時のステータスコード: `404 NOT FOUND`
- 削除対象のバックアップが削除可能な状態ではない時のステータスコード: `409 CONFLICT`
