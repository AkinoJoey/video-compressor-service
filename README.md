# Video Compressor Service
ユーザーが動画をサーバーにアップロードして、選択したオプションに応じて動画を変換できるクライアントサーバ分散型アプリケーションです。
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/0cb78dc1-52d3-4f24-b72a-672c69ce78ed" />
</p>

## 概要

ユーザーはGUIを介して動画ファイルを選択し、変換オプションを指定します。<br>
サーバーとクライアントはTCPソケットを使用して通信し、独自のプロトコルを介して動画変換に必要なデータの送受信を行います。<br>
サーバー側ではマルチメディアファイルの変換に[FFMPEGライブラリ](https://ffmpeg.org/about.html)を使用しています。
<br>
<br>
動画変換が完了すると、サーバーからクライアントに通知が送信され、クライアント側ではダウンロードページが表示されます。<br>
ユーザーはダウンロードボタンをクリックして変換後の動画をダウンロードできます。また、☓ボタンを押してダウンロードをキャンセルすることも可能です。<br>
ダウンロードを選択した場合、サーバーは変換された動画をクライアントに送信し、ダウンロードされた動画はユーザーのダウンロードフォルダに保存されます。

## 作成の経緯
クライアントサーバアプリケーションを作成していく過程で、サーバ操作の基本を習得したいと思いこのアプリケーションを作成しました。<br>
また、プロトコルの基本概念を理解し、低レベルのネットワーキングをアプリケーションに実装するスキルを向上させることを目指しました。

## 使用技術
- Client
  - Python
  - Tkinter
  - Threading

- Server
  - Python
  - asyncio
  - subprocess

## 期間
2023年4月14日から約1か月間の開発期間を要しました。

## こだわった点
### 非同期処理の活用
サーバーサイドではasyncioライブラリを使用して、非同期処理を実装し、複数のクライアントと同時に通信できるようにしました<br>
動画の受信中や変換中にキャンセル処理を受け付けて、キャンセルの要望が合った場合はその時点で動画の受信や変換をストップできるようにしました。<br>

### 動画を削除するタイミング
変換後の動画をサーバーからすぐに削除することで、ストレージの圧迫を防ぎました。<br>
ただし、変換前の動画はクライアントとの接続が終了した後に削除されるように設定しました。これにより、同じ動画を連続して別の方法で変換できるようになります。

### GUIの分離
クライアント側ではTkinterを使用してGUIを構築し、ビジネスロジックとUI表示を分離させ、可読性と拡張性を向上させました。

## これからの改善点、拡張案
### Serverクラスの細分化
Serverクラスではサーバーの起動やクライアントとの接続処理以外にも、動画処理も担当しています。<br>
単一責任の原則に従って設計をするために、動画処理の振る舞いのみを担当するクラスを別で用意するべきだなと思いました。

## デモ
![demo](https://github.com/AkinoJoey/video-compressor-service/assets/124570638/3bbbe40f-04ba-40b9-9aa2-0944ddc0754c)

## 使用方法
1. リポジトリをクローンする
```
git clone https://github.com/AkinoJoey/video-compressor-service.git
```
2. serverを起動
```
python server.py
```
3. clientを起動。GUIが表示されます
```
python client.py
```
4. 「選択」をクリックして変換したい動画ファイルを選択します。動画を選択すると、「選択」ボタンの下にファイル名が表示されます
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/8340e06e-bbb9-4c91-becc-2af1de59f27b" />
</p>

5. 変換したい内容を以下の6つの中から選択。動画ファイルを選択する前に変換のメニューを押すとアラートが表示されます
- 圧縮
- 解像度
- 縦横比
- To Audio
- To GIF
- To WEBM

<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/a5dd4419-cc8d-4b0c-b83c-3d7caaedd100" />
</p>

6. 変換に関するいずれかのボタンをクリックすると、別のウィンドウが開いて変換内容の詳細を入力できます。<br>希望の変換方法を入力し、startボタンを押すと、動画にサーバーがアップロードされ変換が始まります。
- 圧縮を選択した場合、3段階で圧縮レベルを選択できます
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/2367b849-07e8-42e6-9957-baf576ca7cc1" />
</p>
  
- 解像度を選択した場合、6つの項目から選択できます。カスタムを選択すると、希望の解像度を入力できます。
  
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/05234fa7-3a4b-4bf6-84ea-cdfea1ee579c" />
</p>

<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/cc30fbe1-0579-4a51-989a-be61234b4582" />
</p>

- 縦横比を選択した場合、希望の縦横比を入力します

<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/f1e78531-e30b-4fa6-be6a-cbf32559e355" />
</p>

- To GIFまたはTo WEBMを選択した場合、GIF化、WEBM化する動画の時間の範囲を入力します。
  
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/391a7a81-f838-49ee-b186-8e80109e51aa" />
</p>

- To Audioを選択した場合、動画全体がmp3化されるので、startボタンのみが表示されます
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/45ba5b51-3f7a-4d22-8416-c44154174c32" />
</p>

7. 動画の変換中はプログレスバーが表示されます。<br>変換を中止したい場合は、☓ボタンを押して「変換を中止してもよろしいですか？」のウィンドウで「Yes」を選択します。
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/bb46a8da-e001-40e9-bd39-7f6944586001" />
</p>
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/1922e0c2-1191-41b5-a49e-3054d023b078" />
</p>

8. 変換が完了したらDownloadボタンが表示されます。ボタンをクリックするとダウンロードが開始されます。<br>変換中と同様にプログレスバーのウィンドウで☓ボタンを押してダウンロードを中止することも可能です。
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/c4c77b5a-5674-414e-a73c-06f2335831d2" />
</p>

<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/8ae40cb2-27db-4d48-b747-eda35606e4bf" />
</p>

10. ダウンロードが完了すると、以下のウィンドウが表示されます。ダウンロードフォルダで変換後の動画を確認できます。
<p align="center">
  <img src="https://github.com/AkinoJoey/video-compressor-service/assets/124570638/f4c6aed3-a6c3-40da-b89f-a535c2e2dd2c" />
</p>


