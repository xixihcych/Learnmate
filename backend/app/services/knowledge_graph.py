"""
AI知识图谱模块
从文本中抽取实体和关系，构建知识图谱

流程：
1. 文本 → 使用 Gemini API 抽取实体关系
2. 生成三元组 (entity1, relation, entity2)
3. 构建 networkx 图结构
4. 使用 pyvis 生成可视化网页
"""
import json
import re
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import networkx as nx
from pyvis.network import Network

import os


def _use_deepseek() -> bool:
    return os.getenv("USE_DEEPSEEK", "false").strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_llm_service():
    """按环境变量选择 LLM 服务（避免启动时固定选错）。"""
    if _use_deepseek():
        from app.services.deepseek_service import get_deepseek_service

        return get_deepseek_service()
    else:
        from app.services.gemini_service import get_gemini_service
        return get_gemini_service()


class KnowledgeGraph:
    """知识图谱类"""
    
    def __init__(self):
        """初始化知识图谱"""
        self.graph = nx.MultiDiGraph()  # 使用有向多重图
        self.triples: List[Tuple[str, str, str]] = []  # 存储三元组
        self.entity_notes: Dict[str, List[Dict]] = defaultdict(list)  # 实体关联的笔记
        self.llm_service = None  # 懒加载：用到时再初始化
    
    def extract_entities_and_relations(self, text: str) -> List[Dict]:
        """
        使用LLM API（Gemini或DeepSeek）从文本中抽取实体和关系
        
        Args:
            text: 输入文本
        
        Returns:
            三元组列表，格式: [{"entity1": "...", "relation": "...", "entity2": "..."}, ...]
        """
        if not self.llm_service:
            # 懒加载初始化，避免启动时环境变量尚未加载导致选错服务
            self.llm_service = _get_llm_service()
        
        # 构建抽取提示词
        prompt = f"""请从以下文本中抽取知识实体和它们之间的关系。

要求：
1. 识别文本中的主要实体（概念、人物、地点、事件等）
2. 识别实体之间的关系（如：属于、包含、导致、位于等）
3. 以三元组形式输出：(实体1, 关系, 实体2)

文本内容：
{text}

请以JSON数组格式输出，每个元素包含：
{{
    "entity1": "实体1名称",
    "relation": "关系类型",
    "entity2": "实体2名称",
    "confidence": 0.9
}}

只输出JSON数组，不要其他文字说明。如果文本中没有明确的实体关系，返回空数组[]。"""
        
        try:
            # 调用LLM API（Gemini或DeepSeek）
            if _use_deepseek():
                # DeepSeek API（直接调用抽取方法）
                triples = self.llm_service.extract_entities_and_relations(text)
                return triples
            else:
                # Gemini API（使用generate_content）
                response = self.llm_service.model.generate_content(prompt)
                
                # 提取JSON内容
                response_text = response.text.strip()
                
                # 清理响应文本，提取JSON部分
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    # 尝试直接解析
                    json_str = response_text
                
                # 解析JSON
                try:
                    triples = json.loads(json_str)
                    if not isinstance(triples, list):
                        triples = []
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试手动提取
                    triples = self._parse_triples_from_text(response_text)
                
                return triples
        
        except Exception as e:
            print(f"抽取实体和关系失败: {e}")
            return []
    
    def _parse_triples_from_text(self, text: str) -> List[Dict]:
        """
        从文本中手动解析三元组（备用方法）
        
        Args:
            text: 包含三元组的文本
        
        Returns:
            三元组列表
        """
        triples = []
        
        # 尝试匹配各种格式的三元组
        patterns = [
            r'\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\)',  # ("实体1", "关系", "实体2")
            r'\{[^}]*"entity1"[^}]*"([^"]+)"[^}]*"relation"[^}]*"([^"]+)"[^}]*"entity2"[^}]*"([^"]+)"[^}]*\}',  # JSON格式
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:
                    triples.append({
                        "entity1": match[0].strip(),
                        "relation": match[1].strip(),
                        "entity2": match[2].strip(),
                        "confidence": 0.8
                    })
        
        return triples
    
    def add_triples(self, triples: List[Dict], source_text: str = "", source_id: Optional[int] = None):
        """
        添加三元组到知识图谱
        
        Args:
            triples: 三元组列表
            source_text: 来源文本（用于笔记）
            source_id: 来源文档ID
        """
        for triple in triples:
            entity1 = triple.get("entity1", "").strip()
            relation = triple.get("relation", "").strip()
            entity2 = triple.get("entity2", "").strip()
            confidence = triple.get("confidence", 0.8)
            
            if not entity1 or not relation or not entity2:
                continue
            
            # 添加到图
            self.graph.add_edge(entity1, entity2, relation=relation, confidence=confidence)
            
            # 存储三元组
            self.triples.append((entity1, relation, entity2))
            
            # 关联笔记
            if source_text:
                note = {
                    "text": source_text[:200] + "..." if len(source_text) > 200 else source_text,
                    "source_id": source_id,
                    "triple": (entity1, relation, entity2)
                }
                self.entity_notes[entity1].append(note)
                self.entity_notes[entity2].append(note)
    
    def process_text(self, text: str, source_id: Optional[int] = None) -> Dict:
        """
        处理文本，抽取实体关系并添加到知识图谱
        
        Args:
            text: 输入文本
            source_id: 来源文档ID
        
        Returns:
            处理结果统计
        """
        # 抽取实体和关系
        triples = self.extract_entities_and_relations(text)
        
        # 添加到知识图谱
        self.add_triples(triples, source_text=text, source_id=source_id)
        
        return {
            "triples_count": len(triples),
            "entities_count": len(set([t.get("entity1") for t in triples] + [t.get("entity2") for t in triples])),
            "relations_count": len(set([t.get("relation") for t in triples]))
        }
    
    def get_entity_notes(self, entity: str) -> List[Dict]:
        """
        获取实体的相关笔记
        
        Args:
            entity: 实体名称
        
        Returns:
            笔记列表
        """
        return self.entity_notes.get(entity, [])
    
    def visualize(self, output_path: str = "knowledge_graph.html", height: str = "800px", width: str = "100%") -> str:
        """
        使用pyvis生成知识图谱可视化网页
        
        Args:
            output_path: 输出文件路径
            height: 画布高度
            width: 画布宽度
        
        Returns:
            生成的HTML文件路径
        """
        # 创建pyvis网络
        net = Network(
            height=height,
            width=width,
            directed=True,
            notebook=False
        )
        
        # 设置物理引擎
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "stabilization": {"enabled": true, "iterations": 100},
            "barnesHut": {
              "gravitationalConstant": -2000,
              "centralGravity": 0.1,
              "springLength": 200,
              "springConstant": 0.05
            }
          }
        }
        """)
        
        # 添加节点和边
        if self.graph.number_of_nodes() == 0:
            # 如果没有节点，添加提示
            net.add_node("empty", label="知识图谱为空", color="#ff6b6b")
        else:
            # 统计实体出现次数（用于节点大小）
            entity_counts = defaultdict(int)
            for entity1, entity2 in self.graph.edges():
                entity_counts[entity1] += 1
                entity_counts[entity2] += 1
            
            # 获取关系类型（用于颜色）
            relation_types = set()
            for _, _, data in self.graph.edges(data=True):
                relation_types.add(data.get('relation', 'unknown'))
            
            # 为不同关系类型分配颜色
            relation_colors = {}
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
            for i, rel in enumerate(relation_types):
                relation_colors[rel] = colors[i % len(colors)]
            
            # 添加节点
            for entity in self.graph.nodes():
                count = entity_counts[entity]
                size = min(20 + count * 2, 50)  # 节点大小基于连接数
                
                net.add_node(
                    entity,
                    label=entity,
                    size=size,
                    color="#3498db",
                    title=f"{entity}\n连接数: {count}\n点击查看相关笔记"
                )
            
            # 添加边
            for entity1, entity2, data in self.graph.edges(data=True):
                relation = data.get('relation', '')
                confidence = data.get('confidence', 0.8)
                
                # 边的宽度基于置信度
                width = max(1, int(confidence * 5))
                
                # 边的颜色基于关系类型
                color = relation_colors.get(relation, '#95a5a6')
                
                net.add_edge(
                    entity1,
                    entity2,
                    label=relation,
                    width=width,
                    color=color,
                    title=f"{entity1} --{relation}--> {entity2}\n置信度: {confidence:.2f}"
                )
        
        # 生成HTML
        net.save_graph(output_path)
        
        return output_path
    
    def get_statistics(self) -> Dict:
        """
        获取知识图谱统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "nodes_count": self.graph.number_of_nodes(),
            "edges_count": self.graph.number_of_edges(),
            "triples_count": len(self.triples),
            "entities_count": len(set([t[0] for t in self.triples] + [t[2] for t in self.triples])),
            "relations_count": len(set([t[1] for t in self.triples])),
            "notes_count": sum(len(notes) for notes in self.entity_notes.values())
        }
    
    def get_entity_info(self, entity: str) -> Dict:
        """
        获取实体的详细信息
        
        Args:
            entity: 实体名称
        
        Returns:
            实体信息字典
        """
        if entity not in self.graph:
            return {"error": "实体不存在"}
        
        # 获取连接的实体
        predecessors = list(self.graph.predecessors(entity))
        successors = list(self.graph.successors(entity))
        
        # 获取相关关系
        incoming_relations = []
        for pred in predecessors:
            for _, _, data in self.graph.edges(pred, entity, data=True):
                incoming_relations.append({
                    "from": pred,
                    "relation": data.get('relation', ''),
                    "confidence": data.get('confidence', 0.8)
                })
        
        outgoing_relations = []
        for succ in successors:
            for _, _, data in self.graph.edges(entity, succ, data=True):
                outgoing_relations.append({
                    "to": succ,
                    "relation": data.get('relation', ''),
                    "confidence": data.get('confidence', 0.8)
                })
        
        return {
            "entity": entity,
            "incoming_relations": incoming_relations,
            "outgoing_relations": outgoing_relations,
            "notes": self.get_entity_notes(entity),
            "degree": self.graph.degree(entity)
        }
    
    def export_triples(self, format: str = "json") -> str:
        """
        导出三元组
        
        Args:
            format: 导出格式 ("json" 或 "csv")
        
        Returns:
            导出内容
        """
        if format == "json":
            triples_data = [
                {
                    "entity1": t[0],
                    "relation": t[1],
                    "entity2": t[2]
                }
                for t in self.triples
            ]
            return json.dumps(triples_data, ensure_ascii=False, indent=2)
        
        elif format == "csv":
            lines = ["entity1,relation,entity2"]
            for t in self.triples:
                lines.append(f"{t[0]},{t[1]},{t[2]}")
            return "\n".join(lines)
        
        else:
            raise ValueError(f"不支持的格式: {format}")


# 全局知识图谱实例（按用户隔离）
_knowledge_graph_map: Dict[str, KnowledgeGraph] = {}


def get_knowledge_graph(user_key: Optional[str] = None) -> KnowledgeGraph:
    """
    获取知识图谱实例（按 user_key 隔离）
    
    Returns:
        KnowledgeGraph实例
    """
    key = str(user_key or "default")
    if key not in _knowledge_graph_map:
        _knowledge_graph_map[key] = KnowledgeGraph()
    return _knowledge_graph_map[key]

