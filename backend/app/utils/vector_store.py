"""
FAISS向量数据库工具
"""
import numpy as np
import pickle
import os
from typing import List, Optional, Tuple
import faiss
from pathlib import Path

# 避免 transformers 因 TensorFlow/Keras 版本（如 Keras 3）自动导入 TF 分支导致报错。
# 本项目的 sentence-transformers 默认走 PyTorch 路线，这里显式禁用 TF 集成更稳。
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("警告: sentence-transformers未安装，请运行 pip install sentence-transformers")
    SentenceTransformer = None


class VectorStore:
    """FAISS向量存储类"""
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        初始化向量存储
        
        Args:
            model_name: 用于生成embeddings的模型名称
        """
        project_root = Path(__file__).resolve().parents[3]  # .../Learnmate
        env_model_path = os.getenv("EMBEDDING_MODEL_PATH", "").strip()

        # 优先使用本地离线模型路径（避免启动/重建时联网下载导致卡死）
        if env_model_path:
            candidate = Path(env_model_path)
            if not candidate.is_absolute():
                candidate = project_root / env_model_path
            if candidate.exists():
                self.model_name = str(candidate)
            else:
                self.model_name = model_name
        else:
            cached_dir = project_root / "models" / model_name
            self.model_name = str(cached_dir) if cached_dir.exists() else model_name

        self.encoder = None
        self.index = None
        self.dimension = 384  # 默认维度
        self.metadata = []  # 存储文档元数据
        self._encoder_initialized = False
        self.device = os.getenv("EMBEDDING_DEVICE")  # cuda / cpu / auto(None)
        
        # 延迟初始化编码器（首次使用时才加载）
    
    def _ensure_encoder(self):
        """确保编码器已初始化，如果未初始化则尝试加载"""
        if self.encoder is not None:
            return True
        
        if SentenceTransformer is None:
            raise ValueError("sentence-transformers未安装，请运行: pip install sentence-transformers")
        
        if not self._encoder_initialized:
            try:
                print(f"正在加载模型: {self.model_name}...")
                # 设备选择：默认优先 GPU（如可用），也可通过环境变量覆盖：
                # - EMBEDDING_DEVICE=cuda / cpu
                # - 不设置则自动：cuda 可用就用 cuda，否则 cpu
                device = (self.device or "").strip().lower()
                if device not in {"cuda", "cpu"}:
                    try:
                        import torch

                        device = "cuda" if torch.cuda.is_available() else "cpu"
                    except Exception:
                        device = "cpu"

                # 关闭 low_cpu_mem_usage，避免某些组合下出现 “Cannot copy out of meta tensor” 报错
                self.encoder = SentenceTransformer(
                    self.model_name,
                    device=device,
                    model_kwargs={"low_cpu_mem_usage": False},
                )
                self.dimension = self.encoder.get_sentence_embedding_dimension()
                self._encoder_initialized = True
                print(f"模型加载成功，向量维度: {self.dimension}，device: {device}")
                return True
            except Exception as e:
                self._encoder_initialized = True  # 标记为已尝试，避免重复尝试
                error_msg = f"模型加载失败: {str(e)}。请检查网络连接或手动下载模型。"
                print(error_msg)
                raise ValueError(error_msg)
        
        return False
    
    def initialize_index(self, dimension: Optional[int] = None):
        """初始化FAISS索引"""
        if dimension is None:
            dimension = self.dimension
        
        # 使用L2距离的索引
        self.index = faiss.IndexFlatL2(dimension)
        self.dimension = dimension
    
    def add_documents(self, texts: List[str], metadata: List[dict]):
        """
        添加文档到向量数据库
        
        Args:
            texts: 文本列表
            metadata: 元数据列表（每个文本对应的元数据）
        """
        # 确保编码器已初始化
        self._ensure_encoder()
        
        if self.index is None:
            self.initialize_index()
        
        # 生成embeddings
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # 添加到索引
        self.index.add(embeddings)
        
        # 保存元数据
        self.metadata.extend(metadata)
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            top_k: 返回前k个结果
        
        Returns:
            [(metadata, score), ...] 结果列表
        """
        # 如果索引未初始化（知识库为空），返回空列表
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # 尝试初始化编码器（如果还未初始化）
        try:
            self._ensure_encoder()
        except ValueError:
            # 如果编码器初始化失败，返回空列表
            return []
        
        # 如果编码器仍未初始化，返回空列表
        if self.encoder is None:
            return []
        
        # 生成查询向量
        query_embedding = self.encoder.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # 搜索
        distances, indices = self.index.search(query_embedding, top_k)
        
        # 组装结果
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(distance)))
        
        return results
    
    def save(self, filepath: str):
        """保存向量索引和元数据"""
        if self.index is None:
            raise ValueError("索引未初始化")
        
        # 保存FAISS索引
        faiss.write_index(self.index, filepath + '.index')
        
        # 保存元数据
        with open(filepath + '.meta', 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def load(self, filepath: str):
        """加载向量索引和元数据"""
        if not os.path.exists(filepath + '.index'):
            raise FileNotFoundError(f"索引文件不存在: {filepath}.index")
        
        # 加载FAISS索引
        self.index = faiss.read_index(filepath + '.index')
        self.dimension = self.index.d
        
        # 加载元数据
        with open(filepath + '.meta', 'rb') as f:
            self.metadata = pickle.load(f)
        
        # 重新加载编码器
        if SentenceTransformer:
            self.encoder = SentenceTransformer(self.model_name)


# 全局向量存储实例
vector_store = VectorStore()

