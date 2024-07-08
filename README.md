# Golden Axe

Golden Axe とは、VMware 製品のバックアップを取得するためのツールです。

> [!CAUTION]
> 本ツールは、VMware by Broadcom によって公式にサポートされない点にご注意ください。

## 対応製品

- vCenter Server
- NSX Manager

## 準備

本ツールを使用するために、以下のツールをインストールした Linux マシンを用意します。

- docker

また、バックアップデータを SFTP サーバに保存するため、別途 SFTP サーバも準備しておきます。

## インストール方法

1. 本リポジトリをクローンします。

    ```
    git clone https://github.com/vmw-golden-axe/axe-integration.git
    ```

2. リポジトリのルートに移動し、コンテナイメージをビルドします。

    ```
    cd axe-integration
    docker-compose build
    ```

3. バックアップデータを保存する`docker-compose.yaml` の以下の環境変数を設定します。

    - `EXTERNAL_HOST`: SFTP サーバの IP アドレス
    - `SFTP_PORT`: SFTP サービスのポート番号
    - `SFTP_USER`: SFTP サービスのユーザ名
    - `SFTP_PASSWORD`: SFTP サービスのパスワード
    - `SFTP_PATH`: バックアップデータを保存するディレクトリパス

4. 本ツールを起動します。

    ```
    docker-compose up -d
    ```


## 使い方

1. `http://<ツールを起動したサーバの IP アドレス>:8088` にアクセスします。
2. `Backup` タブをクリックします
3. `ADD A BACKUP TARGET` ボタンをクリックすると、バックアップ対象を設定するためのウィンドウがポップアップされるので、以下の情報を入力した後、`OK` をクリックします。

    - `Product Type`: バックアップ対象となる製品（`vcenter` または `nsxmgr`）
    - `Appliance Name`: バックアップ対象の名前
    - `Target Host`: バックアップ対象の IP アドレスまたは FQDN
    - `Username`: バックアップ対象に API でアクセスするためのユーザ名
    - `Password`: バックアップ対象に API でアクセスするためのパスワード
    - `Description`: 説明文

4. `Backup Targets` に表示されているバックアップ対象のリストから、バックアップを実行したい対象を1つ選択します。
5. `Target:` 行に手順4で選択したバックアップ対象が表示されていることを確認して、`ADD A BACKUP JOB` をクリックしてバックアップを開始します。
