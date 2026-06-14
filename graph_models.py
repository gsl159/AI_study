# graph_models.py
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    """独立的图节点：表达知识实体"""
    id: str = Field(description="全局唯一实体ID，例如: 'mysql', 'linux'")
    type: str = Field(description="实体类型，例如: 'COMPONENT', 'OS', 'NETWORK'")
    name: str = Field(description="实体展示名称")

class GraphEdge(BaseModel):
    """独立的图有向边：表达实体间的拓扑依赖"""
    source_id: str = Field(description="源节点ID（主依赖方）")
    target_id: str = Field(description="目标节点ID（被依赖方）")
    relation: str = Field(description="关系类型，例如: 'depends_on', 'requires', 'manages'")
