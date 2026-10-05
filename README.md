# Nano4 + Qwen MTP skills for Codex

兩個可分享的操作 skill，不包含帳號憑證、模型權重或訓練程式。

- **nano4-workflow**：Nano4 SSH / Push MFA、Slurm、部署、監控與結果取回。
- **qwen-sglang-mtp**：Qwen 原生 MTP 的 SGLang / Uni-Agent / verl 設定、
  context / 顯存限制與吞吐量驗證，另附唯讀的 rollout 摘要工具。

## 安裝

先取得 repository，再閱讀 `skills/` 與 `install.sh` 內容：

```bash
git clone https://github.com/Amiannn/skills.git
cd skills
```

確認內容後執行（解壓 ZIP 後也可使用同一指令）：

```bash
bash install.sh
```

需要 Bash 及 Python 3。預設安裝到 `~/.agents/skills`，不需 sudo、不會連線
Nano4、不會提交 GPU 作業、不會安裝模型套件。若同名 skill 已存在會停止，
不覆寫既有內容。可以指定其他支援的 discovery 目錄：

```bash
bash install.sh /path/to/skills
```

若 Codex 未顯示新 skill，重新開啟 Codex。
安裝位置與探索行為參考 [OpenAI Docs](https://learn.chatgpt.com/docs/build-skills)。

## 使用

在 Codex 中輸入：

```text
用 $nano4-workflow 幫我登入 Nano4，用 Push 讓我在手機核准。
用 $nano4-workflow 幫我檢查這個專案，準備一個單卡 smoke test，先不要提交。
用 $qwen-sglang-mtp 檢查我的 Qwen 與 SGLang 版本，規劃 MTP4 測試。
```

伙伴需要自行提供自己的 Nano4 使用者名稱、授權的計費 account、實驗專案
與資料位置。帳號與 account 名稱不是密碼，但不要直接沿用別人的計費設定。
密碼與 OTP 不要寫進 repository 或 skill。Push 仍需要本人核准。

設定非機密的連線變數時，將 YOUR_* 改成自己的值：

```bash
export NANO4_USER='YOUR_CLUSTER_USER'
export NANO4_LOGIN="${NANO4_USER}@nano4.nchc.org.tw"
export NANO4_ACCOUNT='YOUR_AUTHORIZED_PROJECT'
export NANO4_SSH_SOCKET="${TMPDIR:-/tmp}/nano4-${USER}-${NANO4_USER}.sock"
```

`skills/nano4-workflow/references/local-site.md` 是新使用者的接手指引，不含
原作者的帳號、共享 socket 或工作站路徑。

## 這個套件的範圍

- skill 是操作知識，不會自動取得 Nano4 權限或複製實驗 pipeline。
- Book Agent / Uni-Agent 的專案啟動腳本與 patches **不在本套件內**。
  要重現原實驗，還需取得對應專案；skill 會指出應檢查的檔案與版本。
- `summarize_run.py` 可獨立執行，但只支援文件中說明的 Book Agent artifact 格式：

```bash
python3 skills/qwen-sglang-mtp/scripts/summarize_run.py /path/to/downloaded/run
```

- MTP 效能數字是歷史實驗，不保證換模型、硬體或版本後仍有相同加速。
- 安裝是 copy，不是 symlink，也不會自動更新。更新前比較差異並備份既有
  skill，避免覆蓋自己的設定。

## GitHub 分享

Repository：<https://github.com/Amiannn/skills>。
伙伴取得 repo 後執行上面的 `bash install.sh` 即可；ZIP 也使用相同方式。
這是公開分享版本，不包含原作者帳號、計費專案、憑證與工作站絕對路徑。

目前沒有替作者選擇開源 license；要公開發布為開源專案前，請由作者確認。
