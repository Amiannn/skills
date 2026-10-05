# Nano4 + Qwen MTP skills for Codex and Claude Code

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

確認內容後依使用的工具安裝（解壓 ZIP 後也可使用同一指令）。

### Codex

```bash
bash install.sh
```

預設安裝到 `~/.agents/skills`，也可明確指定 `--target codex`。
若 Codex 未顯示新 skill，重新開啟 Codex。
安裝位置與探索行為參考 [OpenAI Docs](https://learn.chatgpt.com/docs/build-skills)。

### Claude Code

```bash
bash install.sh --target claude
```

安裝到 `~/.claude/skills`，適用本機 Claude Code 的各個專案。
如只想安裝到某個專案：

```bash
bash install.sh --target claude /path/to/project/.claude/skills
```

在該專案重新開啟 Claude Code，輸入 `/` 尋找 `nano4-workflow` 與
`qwen-sglang-mtp`。Claude Code 支援共用的 `SKILL.md` 格式與相對路徑的
參考文件，因此兩個客戶端使用同一份操作指引，不另維護容易分歧的副本。
Claude 安裝時省略僅供 Codex UI 使用的 `agents/openai.yaml`。
格式、安裝位置與呼叫方式參考 [Claude Code 官方文件](https://code.claude.com/docs/en/skills)。

這裡的 Claude 版本指 **Claude Code 本機終端**，不是把套件上傳到
claude.ai 聊天介面。執行 Nano4 工作仍需要終端工具、SSH 與網路存取權限；
本套件不會繞過 Claude Code 的工具權限或替你開啟自動核准。

### 安裝安全與相依套件

需要 Bash 及 Python 3。不需 sudo、不會連線 Nano4、不會提交 GPU 作業、
不會安裝模型套件。若同名 skill 已存在會停止，不覆寫既有內容。
原本的自訂安裝目錄語法仍可使用（預設為 Codex）：

```bash
bash install.sh /path/to/skills
```

## 使用

在 Codex 中輸入：

```text
用 $nano4-workflow 幫我登入 Nano4，用 Push 讓我在手機核准。
用 $nano4-workflow 幫我檢查這個專案，準備一個單卡 smoke test，先不要提交。
用 $qwen-sglang-mtp 檢查我的 Qwen 與 SGLang 版本，規劃 MTP4 測試。
```

在 Claude Code 中輸入（每次一行）：

```text
/nano4-workflow 幫我登入 Nano4，用 Push 讓我在手機核准。
/nano4-workflow 幫我檢查這個專案，準備一個單卡 smoke test，先不要提交。
/qwen-sglang-mtp 檢查我的 Qwen 與 SGLang 版本，規劃 MTP4 測試。
```

也可以用自然語言描述需求，由 Claude Code 判斷是否載入 skill。

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
伙伴取得 repo 後依客戶端執行 `bash install.sh` 或
`bash install.sh --target claude`；ZIP 也使用相同方式。
這是公開分享版本，不包含原作者帳號、計費專案、憑證與工作站絕對路徑。

目前沒有替作者選擇開源 license；要公開發布為開源專案前，請由作者確認。

## 安裝測試

```bash
python3 -m unittest discover -s tests -v
```

測試使用暫存 HOME，檢查兩種安裝目錄、共用內容與防覆寫行為，不會登入
Nano4 或呼叫模型。這不代表已在 Claude Code 中實測遠端登入或 GPU 任務。
