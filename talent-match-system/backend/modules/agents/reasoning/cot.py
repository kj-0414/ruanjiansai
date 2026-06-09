"""
Chain-of-Thought (CoT) 推理框架
实现链式思考推理
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """推理类型"""
    DIRECT = "direct"
    CHAIN = "chain"
    TREE = "tree"
    SELF_CONSISTENT = "self_consistent"


@dataclass
class ThoughtStep:
    """思考步骤"""
    step_id: int
    thinking: str
    reasoning_type: ReasoningType = ReasoningType.CHAIN
    evidence: Optional[List[str]] = None
    conclusion: Optional[str] = None
    confidence: float = 0.0
    children: List['ThoughtStep'] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "step_id": self.step_id,
            "thinking": self.thinking,
            "reasoning_type": self.reasoning_type.value,
            "evidence": self.evidence or [],
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "children": [c.to_dict() for c in self.children],
            "timestamp": self.timestamp
        }


class ChainOfThought:
    """
    链式思考推理器
    支持多种推理策略
    """

    def __init__(
        self,
        llm_client=None,
        reasoning_type: ReasoningType = ReasoningType.CHAIN
    ):
        self.llm_client = llm_client
        self.reasoning_type = reasoning_type
        self.thought_chain: List[ThoughtStep] = []
        self.logger = logger
        self.step_counter = 0

    def _create_cot_prompt(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """创建CoT提示"""
        reasoning_instruction = {
            ReasoningType.DIRECT: "Provide a direct answer.",
            ReasoningType.CHAIN: "Think step by step, explaining your reasoning.",
            ReasoningType.TREE: "Explore multiple reasoning paths and branches.",
            ReasoningType.SELF_CONSISTENT: "Think through the problem multiple ways and check for consistency."
        }

        instruction = reasoning_instruction.get(
            self.reasoning_type,
            "Think step by step."
        )

        prompt = f"""You are a HR assistant helping with resume-job matching.

Task: {question}

{instruction}

Context:
{self._format_context(context)}

Provide your reasoning step by step:
"""

        return prompt

    def _format_context(self, context: Dict[str, Any]) -> str:
        """格式化上下文"""
        parts = []

        if "resume" in context:
            parts.append(f"Resume: {context['resume']}")

        if "job" in context:
            parts.append(f"Job Requirements: {context['job']}")

        if "skills" in context:
            parts.append(f"Skills: {', '.join(context['skills'])}")

        if "experience" in context:
            parts.append(f"Experience: {context['experience']}")

        return "\n".join(parts) if parts else "No additional context."

    async def reason(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行链式推理

        Args:
            question: 问题
            context: 上下文

        Returns:
            推理结果
        """
        self.thought_chain = []
        self.step_counter = 0

        self.logger.info(f"Starting CoT reasoning: {question}")

        if self.reasoning_type == ReasoningType.TREE:
            return await self._tree_reasoning(question, context)
        elif self.reasoning_type == ReasoningType.SELF_CONSISTENT:
            return await self._self_consistent_reasoning(question, context)
        else:
            return await self._chain_reasoning(question, context)

    async def _chain_reasoning(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """链式推理"""
        prompt = self._create_cot_prompt(question, context)

        if self.llm_client:
            try:
                response = await self._call_llm(prompt)
                steps = self._parse_chain_response(response)

                for step_data in steps:
                    self.step_counter += 1
                    step = ThoughtStep(
                        step_id=self.step_counter,
                        thinking=step_data.get("thinking", ""),
                        reasoning_type=self.reasoning_type,
                        evidence=step_data.get("evidence", []),
                        conclusion=step_data.get("conclusion"),
                        confidence=step_data.get("confidence", 0.5)
                    )
                    self.thought_chain.append(step)

            except Exception as e:
                self.logger.error(f"Chain reasoning failed: {e}")

        answer = self._extract_final_answer()

        return {
            "question": question,
            "answer": answer,
            "reasoning_chain": [s.to_dict() for s in self.thought_chain],
            "confidence": self._calculate_overall_confidence()
        }

    async def _tree_reasoning(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """树状推理（多路径探索）"""
        root = ThoughtStep(
            step_id=0,
            thinking=f"Initial question: {question}",
            reasoning_type=ReasoningType.TREE
        )

        branches = [
            "Based on technical skills",
            "Based on experience level",
            "Based on job fit"
        ]

        for i, branch in enumerate(branches):
            self.step_counter += 1
            branch_step = ThoughtStep(
                step_id=self.step_counter,
                thinking=branch,
                reasoning_type=ReasoningType.TREE,
                confidence=0.6 + i * 0.1
            )

            prompt = f"{question}\n\nReasoning path: {branch}"
            if self.llm_client:
                try:
                    response = await self._call_llm(prompt)
                    branch_step.conclusion = response
                except:
                    pass

            root.children.append(branch_step)

        self.thought_chain.append(root)

        answer = self._aggregate_branches(root)

        return {
            "question": question,
            "answer": answer,
            "reasoning_tree": root.to_dict(),
            "branches_explored": len(branches),
            "confidence": self._calculate_overall_confidence()
        }

    async def _self_consistent_reasoning(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """自洽推理（多角度思考）"""
        paths = []

        for i in range(3):
            self.step_counter += 1
            path_prompt = f"{question}\n\nApproach {i+1}: Think differently about this problem."

            step = ThoughtStep(
                step_id=self.step_counter,
                thinking=f"Approach {i+1}",
                reasoning_type=ReasoningType.SELF_CONSISTENT,
                confidence=0.7
            )

            if self.llm_client:
                try:
                    response = await self._call_llm(path_prompt)
                    step.conclusion = response
                    paths.append(response)
                except:
                    pass

            self.thought_chain.append(step)

        answer = self._find_common_answer(paths)

        return {
            "question": question,
            "answer": answer,
            "reasoning_paths": [s.to_dict() for s in self.thought_chain],
            "path_count": len(paths),
            "confidence": self._calculate_overall_confidence()
        }

    async def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        if self.llm_client:
            response = self.llm_client.chat(prompt)
            return response if isinstance(response, str) else str(response)
        return ""

    def _parse_chain_response(self, response: str) -> List[Dict]:
        """解析链式响应"""
        steps = []
        current_step = {"thinking": "", "evidence": [], "confidence": 0.5}

        lines = response.split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith('Step') or line.startswith('首先') or line.startswith('然后'):
                if current_step["thinking"]:
                    steps.append(current_step)
                current_step = {"thinking": line, "evidence": [], "confidence": 0.5}

            elif line.startswith('-') or line.startswith('•'):
                current_step["evidence"].append(line[1:].strip())

        if current_step["thinking"]:
            steps.append(current_step)

        return steps if steps else [{"thinking": response, "evidence": [], "confidence": 0.5}]

    def _extract_final_answer(self) -> str:
        """提取最终答案"""
        if not self.thought_chain:
            return ""

        for step in reversed(self.thought_chain):
            if step.conclusion:
                return step.conclusion

        if self.thought_chain:
            return self.thought_chain[-1].thinking

        return ""

    def _aggregate_branches(self, root: ThoughtStep) -> str:
        """聚合多分支结果"""
        conclusions = []

        def collect_conclusions(step):
            if step.conclusion:
                conclusions.append(step.conclusion)
            for child in step.children:
                collect_conclusions(child)

        collect_conclusions(root)

        if conclusions:
            return f"Multiple approaches considered. Key insights: {conclusions[0]}"

        return "Analysis complete."

    def _find_common_answer(self, paths: List[str]) -> str:
        """寻找共同答案"""
        if not paths:
            return "No consistent answer found."

        if len(paths) == 1:
            return paths[0]

        common_words = set(paths[0].split())
        for path in paths[1:]:
            common_words &= set(path.split())

        if common_words:
            return f"Common answer across {len(paths)} approaches: {' '.join(list(common_words)[:10])}"

        return f"Multiple perspectives considered. Primary recommendation: {paths[0][:200]}"

    def _calculate_overall_confidence(self) -> float:
        """计算整体置信度"""
        if not self.thought_chain:
            return 0.0

        confidences = [step.confidence for step in self.thought_chain]
        return sum(confidences) / len(confidences) if confidences else 0.0

    def get_reasoning_chain(self) -> List[Dict]:
        """获取推理链"""
        return [s.to_dict() for s in self.thought_chain]

    def reset(self):
        """重置"""
        self.thought_chain = []
        self.step_counter = 0
