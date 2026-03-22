# 向量模型目录（不随仓库提交）

本目录用于放置 **Sentence Transformers** 等嵌入模型，体积较大，请本地下载或运行脚本获取。

## 推荐模型

与后端 `.env.example` 中说明一致，可使用：

- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

将模型文件夹放到本目录下，例如：

```
models/paraphrase-multilingual-MiniLM-L12-v2/
```

然后在 `backend/.env` 中设置：

```env
EMBEDDING_MODEL_PATH=models/paraphrase-multilingual-MiniLM-L12-v2
```

（路径相对于 **项目根目录** `learnmate-github/`，与后端启动时工作目录一致即可。）

## 可选脚本

若仓库中提供了 `scripts/download_embedding_model.sh`，可在项目根目录执行以自动下载到 `models/`。
