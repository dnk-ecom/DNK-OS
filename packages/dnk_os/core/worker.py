# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/core/worker.py"
# purpose: "Worker agent (Герич) for multi-adapter task execution"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""
Worker Agent (Герич) Module for DNK OS.

This module provides the DNKWorker agent responsible for executing tasks
delegated by the Supervisor (Antigravity) using all 5 core adapters:
1. TransformersAdapter (text generation, summarization, etc.)
2. LlamaIndexAdapter (RAG queries & knowledge base management)
3. CrewAIAdapter (multi-agent crew orchestration)
4. AutoGenAdapter (multi-agent conversations & group chats)
5. LangGraphAdapter (state graph workflow execution)
"""

from typing import Optional, List, Dict, Any, Union, Callable

try:
    from adapters.transformers_adapter import TransformersAdapter
    from adapters.llamaindex_adapter import LlamaIndexAdapter
    from adapters.crewai_adapter import CrewAIAdapter
    from adapters.autogen_adapter import AutoGenAdapter
    from adapters.langgraph_adapter import LangGraphAdapter
except ImportError:
    from adapters.transformers_adapter import TransformersAdapter
    from adapters.llamaindex_adapter import LlamaIndexAdapter
    from adapters.crewai_adapter import CrewAIAdapter
    from adapters.autogen_adapter import AutoGenAdapter
    from adapters.langgraph_adapter import LangGraphAdapter



class DNKWorker:
    """
    Worker agent (Герич) for DNK OS Multi-Agent Core.
    
    Executes tasks delegated by Supervisor using all 5 adapters.
    
    Supports:
    - Text generation (transformers)
    - RAG queries (llama_index)
    - Crew orchestration (crewAI)
    - Multi-agent conversations (autogen)
    - State graph execution (langgraph)
    """
    
    def __init__(
        self,
        name: str = "Герич",
        capabilities: Optional[List[str]] = None,
        transformers_adapter: Optional[TransformersAdapter] = None,
        llamaindex_adapter: Optional[LlamaIndexAdapter] = None,
        crewai_adapter: Optional[CrewAIAdapter] = None,
        autogen_adapter: Optional[AutoGenAdapter] = None,
        langgraph_adapter: Optional[LangGraphAdapter] = None,
        **kwargs: Any
    ):
        """
        Initialize Worker.
        
        Args:
            name: Worker name
            capabilities: List of capabilities (e.g., ["code", "research", "translation", "rag", "orchestration"])
            transformers_adapter: Optional custom TransformersAdapter instance
            llamaindex_adapter: Optional custom LlamaIndexAdapter instance
            crewai_adapter: Optional custom CrewAIAdapter instance
            autogen_adapter: Optional custom AutoGenAdapter instance
            langgraph_adapter: Optional custom LangGraphAdapter instance
            **kwargs: Additional worker arguments
        """
        self.name = name
        self.capabilities = capabilities or ["code", "research", "translation"]
        
        # Initialize adapters (with dependency injection support for testing)
        self.transformers = transformers_adapter or TransformersAdapter(model_name="gpt2", task="text-generation")
        self.llamaindex = llamaindex_adapter or LlamaIndexAdapter(vector_store_type="memory", llm_model="gpt2")
        self.crewai = crewai_adapter or CrewAIAdapter(crew_name=f"{name}_crew")
        self.autogen = autogen_adapter or AutoGenAdapter()
        self.langgraph = langgraph_adapter or LangGraphAdapter(graph_name=f"{name}_graph")
    
    def execute_task(
        self,
        task: str,
        task_type: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute task using appropriate adapter.
        
        Args:
            task: Task description
            task_type: Optional task type ("generation", "rag", "crew", "conversation", "graph")
                       If None, auto-detect from task content
            **kwargs: Extra parameters passed to the specific execution method
            
        Returns:
            Task result with "output", "status", "metadata"
        """
        if not task_type:
            task_lower = task.lower()
            if any(k in task_lower for k in ["rag", "search", "retrieve", "knowledge", "capital", "find"]):
                resolved_type = "rag"
            elif any(k in task_lower for k in ["crew", "orchestrat", "team"]):
                resolved_type = "crew"
            elif any(k in task_lower for k in ["conversation", "chat", "discuss", "debate"]):
                resolved_type = "conversation"
            elif any(k in task_lower for k in ["graph", "state", "flow", "workflow"]):
                resolved_type = "graph"
            else:
                resolved_type = "generation"
        else:
            resolved_type = task_type.lower()
        
        if resolved_type in ["rag", "search"]:
            return self.execute_rag(query=task, **kwargs)
        elif resolved_type in ["crew", "orchestration"]:
            return self.execute_crew(task_description=task, **kwargs)
        elif resolved_type in ["conversation", "chat"]:
            return self.execute_conversation(topic=task, **kwargs)
        elif resolved_type in ["graph", "state_graph", "workflow"]:
            graph_config = kwargs.pop("graph_config", {"type": "sequential", "nodes": ["node_a", "node_b"]})
            input_state = kwargs.pop("input_state", {"messages": [task]})
            return self.execute_graph(graph_config=graph_config, input_state=input_state, **kwargs)
        else:
            # Default to text generation
            return self.execute_generation(prompt=task, **kwargs)
    
    def execute_generation(
        self,
        prompt: str,
        max_tokens: int = 256,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute text generation task (transformers).
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            **kwargs: Extra arguments for transformers generator
            
        Returns:
            Result with "output", "tokens_used", "status", "metadata"
        """
        gen_output = self.transformers.generate(prompt=prompt, max_new_tokens=max_tokens, **kwargs)
        output_text = gen_output if isinstance(gen_output, str) else str(gen_output)
        tokens_used = len(output_text.split())
        
        return {
            "output": output_text,
            "tokens_used": tokens_used,
            "status": "completed",
            "metadata": {"raw": gen_output}
        }
    
    def execute_rag(
        self,
        query: str,
        documents: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute RAG query (llama_index).
        
        Args:
            query: Query text
            documents: Optional documents to index before querying
            **kwargs: Extra arguments for LlamaIndex query
            
        Returns:
            Result with "answer", "sources", "confidence", "output", "status"
        """
        if documents:
            self.load_knowledge_base(documents=documents)
            
        rag_result = self.llamaindex.rag_query(query=query, **kwargs)
        answer = rag_result.get("answer", "")
        sources = rag_result.get("sources", [])
        confidence = rag_result.get("confidence", 1.0)
        
        return {
            "output": answer,
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "status": "completed",
            "metadata": rag_result
        }
    
    def execute_crew(
        self,
        task_description: str,
        agents: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute crew orchestration (crewAI).
        
        Args:
            task_description: Task description
            agents: Optional custom agents list
            **kwargs: Extra arguments for crew assembly & execution
            
        Returns:
            Result with "output", "crew_status", "status", "metadata"
        """
        crew_agents = agents
        if not crew_agents:
            worker_agent = self.crewai.create_agent(
                name=self.name,
                role="Senior Engineer",
                goal=f"Execute tasks related to {task_description}",
                backstory=f"{self.name} is a high-performance worker agent."
            )
            crew_agents = [worker_agent]
            
        primary_agent = crew_agents[0]
        crew_task = self.crewai.create_task(
            description=task_description,
            expected_output=f"Detailed execution outcome for {task_description}",
            agent=primary_agent
        )
        
        crew = self.crewai.assemble_crew(
            agents=crew_agents,
            tasks=[crew_task],
            process=kwargs.get("process", "sequential")
        )
        
        execution_result = self.crewai.execute_crew(crew=crew)
        output_data = execution_result.get("output", "")
        crew_status = execution_result.get("status", "completed")
        
        return {
            "output": output_data,
            "crew_status": crew_status,
            "status": "completed",
            "metadata": execution_result
        }
    
    def execute_conversation(
        self,
        topic: str,
        participants: Optional[int] = 2,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute multi-agent conversation (autogen).
        
        Args:
            topic: Conversation topic
            participants: Number of participants (default: 2)
            **kwargs: Extra arguments for AutoGen conversation
            
        Returns:
            Result with "output", "summary", "chat_history", "status"
        """
        num_participants = participants if participants is not None else 2
        
        if num_participants <= 2:
            user_proxy = self.autogen.create_user_proxy_agent(
                name="User_Proxy",
                human_input_mode="NEVER"
            )
            assistant = self.autogen.create_assistant_agent(
                name=f"{self.name}_Assistant",
                system_message=f"You are {self.name}, an expert assistant."
            )
            chat_result = self.autogen.initiate_two_agent_chat(
                sender=user_proxy,
                recipient=assistant,
                message=topic,
                max_turns=kwargs.get("max_turns", 5)
            )
        else:
            agent_list = [
                self.autogen.create_assistant_agent(
                    name=f"Agent_{i+1}",
                    system_message=f"You are Agent {i+1} participating in {topic}."
                )
                for i in range(num_participants)
            ]
            groupchat = self.autogen.create_group_chat(
                agents=agent_list,
                max_round=kwargs.get("max_round", 5)
            )
            chat_result = self.autogen.run_group_chat(
                group_chat=groupchat,
                message=topic
            )
            
        summary = chat_result.get("summary", f"Conversation on topic: {topic}")
        chat_history = chat_result.get("chat_history", [])
        
        return {
            "output": summary,
            "summary": summary,
            "chat_history": chat_history,
            "status": "completed",
            "metadata": chat_result
        }
    
    def execute_graph(
        self,
        graph_config: Dict[str, Any],
        input_state: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute state graph (langgraph).
        
        Args:
            graph_config: Graph configuration with nodes, edges
            input_state: Input state dictionary
            **kwargs: Extra arguments for LangGraph invocation
            
        Returns:
            Result with "output", "state_snapshots", "status"
        """
        graph = self.langgraph.create_state_graph(state_schema=graph_config.get("schema", {}))
        nodes = graph_config.get("nodes", ["node_a", "node_b"])
        
        for node_name in nodes:
            def make_node_fn(n_name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
                return lambda state: {**state, f"visited_{n_name}": True}
            graph = self.langgraph.add_node(
                graph=graph, 
                node_name=node_name, 
                node_function=make_node_fn(node_name)
            )
        
        # Chain edges sequentially
        for i in range(len(nodes) - 1):
            graph = self.langgraph.add_edge(graph=graph, source=nodes[i], target=nodes[i+1])
            
        compiled = self.langgraph.compile_graph(graph=graph)
        entry_point = nodes[0] if nodes else "node_a"
        invoke_result = self.langgraph.invoke(
            compiled_graph=compiled,
            input_state=input_state,
            entry_point=entry_point
        )
        
        final_state = invoke_result.get("final_state", input_state)
        history = invoke_result.get("state_history", [input_state, final_state])
        
        return {
            "output": final_state,
            "state_snapshots": history,
            "status": "completed",
            "metadata": invoke_result
        }
    
    def load_knowledge_base(
        self,
        documents: List[str],
        **kwargs: Any
    ) -> int:
        """
        Load documents into RAG knowledge base.
        
        Args:
            documents: List of document texts
            **kwargs: Extra arguments for document indexing
            
        Returns:
            Number of documents loaded
        """
        self.llamaindex.load_documents(documents=documents)
        self.llamaindex.index_documents(documents=documents, **kwargs)
        return len(documents)
    
    def get_capabilities(self) -> List[str]:
        """
        Get worker capabilities.
        
        Returns:
            List of capability strings
        """
        return list(self.capabilities)
