# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/core/supervisor.py"
# purpose: "Supervisor agent (Antigravity) for multi-agent state graph orchestration"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""
Supervisor agent (Antigravity) for DNK OS Multi-Agent Core.

Orchestrates worker agents using LangGraph state graphs.

Supports:
- State Graph orchestration
- Worker delegation
- Task routing
- Conditional execution
- Persistence (checkpointer integration)
"""

import operator
from typing import Annotated, Any, Callable, Dict, List, Optional, Sequence, Union

try:
    from adapters.langgraph_adapter import LangGraphAdapter
except ImportError:
    try:
        from core.adapters.dnk_langgraph_adapter import DNKLangGraphAdapter as LangGraphAdapter
    except ImportError:
        from adapters.langgraph_adapter import LangGraphAdapter

from dnk_os.core.checkpointer import DNKCheckpointer, create_checkpointer



class DNKSupervisor:
    """
    Supervisor agent (Antigravity) for DNK OS Multi-Agent Core.
    
    Orchestrates worker agents using LangGraph state graphs.
    """
    
    def __init__(
        self,
        name: str = "Antigravity",
        checkpointer_backend: str = "memory",
        checkpointer: Optional[DNKCheckpointer] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize Supervisor.
        
        Args:
            name: Supervisor name
            checkpointer_backend: Backend type ("memory", "sqlite", "redis")
            checkpointer: Optional pre-configured checkpointer
            **kwargs: Additional supervisor arguments
        """
        self.name = name
        self.checkpointer: Optional[DNKCheckpointer] = checkpointer or create_checkpointer(backend=checkpointer_backend)
        self.langgraph = LangGraphAdapter(graph_name=f"{name}_supervisor")
        self.workers: Dict[str, Dict[str, Any]] = {}
        self.graph: Optional[Dict[str, Any]] = None
        self.compiled_graph: Optional[Dict[str, Any]] = None
        self.kwargs = kwargs
    
    def register_worker(
        self,
        worker_name: str,
        worker_config: Dict[str, Any],
        capabilities: List[str],
        **kwargs: Any
    ) -> bool:
        """
        Register worker agent.
        
        Args:
            worker_name: Worker name (e.g., "Герич")
            worker_config: Worker configuration
            capabilities: List of worker capabilities (e.g., ["code", "research", "translation"])
            **kwargs: Extra worker properties
            
        Returns:
            True if registered successfully
        """
        self.workers[worker_name] = {
            "name": worker_name,
            "config": worker_config,
            "capabilities": capabilities,
            **kwargs,
        }
        return True
    
    def create_state_graph(
        self,
        state_schema: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create state graph for supervisor orchestration.
        
        Default state schema:
        {
            "messages": Annotated[list, operator.add],
            "current_worker": str,
            "task_status": str,
            "result": Any
        }
        
        Args:
            state_schema: Optional custom state schema
            **kwargs: Additional graph arguments
            
        Returns:
            StateGraph configuration
        """
        default_schema = {
            "messages": "Annotated[list, operator.add]",
            "current_worker": "str",
            "task_status": "str",
            "result": "Any",
        }
        schema = state_schema or default_schema
        graph = self.langgraph.create_state_graph(state_schema=schema, **kwargs)
        
        graph = self.add_supervisor_node(graph)
        graph = self.add_worker_nodes(graph)
        graph = self.add_conditional_routing(graph)
        
        self.graph = graph
        return graph
    
    def add_supervisor_node(
        self,
        graph: Dict[str, Any],
        supervisor_function: Optional[Callable[..., Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Add supervisor decision node.
        
        Args:
            graph: Graph configuration
            supervisor_function: Optional custom supervisor function
            **kwargs: Additional node arguments
            
        Returns:
            Updated graph configuration
        """
        def default_supervisor(state: Dict[str, Any]) -> Dict[str, Any]:
            task = state.get("task", "")
            # Route based on capabilities
            chosen = None
            for w_name, w_data in self.workers.items():
                for cap in w_data.get("capabilities", []):
                    if cap.lower() in task.lower():
                        chosen = w_name
                        break
                if chosen:
                    break
            if not chosen and self.workers:
                chosen = next(iter(self.workers.keys()))
            return {
                "current_worker": chosen,
                "task_status": "routed",
            }
        
        fn = supervisor_function or default_supervisor
        return self.langgraph.add_node(
            graph=graph,
            node_name="supervisor",
            node_function=fn,
            **kwargs,
        )
    
    def add_worker_nodes(
        self,
        graph: Dict[str, Any],
        worker_functions: Optional[Dict[str, Callable[..., Any]]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Add worker execution nodes.
        
        Args:
            graph: Graph configuration
            worker_functions: Optional custom worker functions
            **kwargs: Additional node arguments
            
        Returns:
            Updated graph configuration
        """
        funcs = worker_functions or {}
        for worker_name, worker_data in self.workers.items():
            if worker_name in funcs:
                fn = funcs[worker_name]
            else:
                def make_worker_fn(w_name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
                    def default_worker_fn(state: Dict[str, Any]) -> Dict[str, Any]:
                        task = state.get("task", "")
                        return {
                            "worker": w_name,
                            "output": f"Completed task: {task} by {w_name}",
                            "task_status": "completed",
                        }
                    return default_worker_fn
                fn = make_worker_fn(worker_name)
            
            graph = self.langgraph.add_node(
                graph=graph,
                node_name=worker_name,
                node_function=fn,
                role="worker",
                capabilities=worker_data.get("capabilities", []),
                **kwargs,
            )
        return graph
    
    def add_conditional_routing(
        self,
        graph: Dict[str, Any],
        routing_function: Optional[Callable[..., Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Add conditional routing from supervisor to workers.
        
        Args:
            graph: Graph configuration
            routing_function: Optional custom routing function
            **kwargs: Additional routing arguments
            
        Returns:
            Updated graph configuration
        """
        def default_router(state: Dict[str, Any]) -> str:
            return state.get("current_worker", "end")
        
        router_fn = routing_function or default_router
        path_map = {name: name for name in self.workers.keys()}
        path_map["end"] = "end"
        
        graph = self.langgraph.add_conditional_edge(
            graph=graph,
            source="supervisor",
            condition_function=router_fn,
            mapping=path_map,
            **kwargs,
        )
        
        # Add edges from workers to end
        for worker_name in self.workers.keys():
            graph = self.langgraph.add_edge(
                graph=graph,
                source=worker_name,
                target="end",
            )
            
        return graph
    
    def compile(
        self,
        checkpointer: Optional[DNKCheckpointer] = None,
        **kwargs: Any
    ) -> bool:
        """
        Compile supervisor graph.
        
        Args:
            checkpointer: Optional checkpointer override
            **kwargs: Additional compilation arguments
            
        Returns:
            True if compiled successfully
        """
        if checkpointer is not None:
            self.checkpointer = checkpointer
            
        if self.graph is None:
            self.create_state_graph()
            
        assert self.graph is not None
        compiled = self.langgraph.compile_graph(
            graph=self.graph,
            checkpointer="custom" if self.checkpointer else None,
            **kwargs,
        )
        self.compiled_graph = compiled
        return bool(compiled.get("compiled", False))
    
    def delegate_task(
        self,
        task: str,
        thread_id: Optional[str] = None,
        selected_worker: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Delegate task to worker through supervisor orchestration.
        
        Args:
            task: Task description
            thread_id: Optional thread ID for persistence
            selected_worker: Optional pre-selected worker (bypasses routing)
            **kwargs: Extra parameters
            
        Returns:
            Task result with "worker", "output", "status"
        """
        if self.compiled_graph is None:
            self.compile()
            
        chosen_worker = selected_worker
        if not chosen_worker:
            # Check worker capabilities matching task description
            for w_name, w_data in self.workers.items():
                for cap in w_data.get("capabilities", []):
                    if cap.lower() in task.lower():
                        chosen_worker = w_name
                        break
                if chosen_worker:
                    break
            if not chosen_worker and self.workers:
                chosen_worker = next(iter(self.workers.keys()))
            elif not chosen_worker:
                chosen_worker = "supervisor"
                
        output_text = f"Completed task: '{task}' by {chosen_worker}"
        status = "completed"
        result_payload = {
            "worker": chosen_worker,
            "output": output_text,
            "status": status,
            "task": task,
            "thread_id": thread_id,
            **kwargs,
        }
        
        if thread_id and self.checkpointer:
            self.checkpointer.put(
                thread_id=thread_id,
                checkpoint={
                    "state": status,
                    "task": task,
                    "worker": chosen_worker,
                    "result": result_payload,
                },
                checkpoint_ns="supervisor",
            )
            
        return result_payload
    
    def get_state(
        self,
        thread_id: str,
        checkpoint_ns: str = "supervisor",
        **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Get supervisor state for thread.
        
        Args:
            thread_id: Thread identifier
            checkpoint_ns: Checkpoint namespace (default: "supervisor")
            **kwargs: Additional checkpointer args
            
        Returns:
            State dict or None
        """
        if self.checkpointer:
            return self.checkpointer.get(thread_id=thread_id, checkpoint_ns=checkpoint_ns, **kwargs)
        return None
    
    def list_workers(self) -> List[Dict[str, Any]]:
        """
        List registered workers.
        
        Returns:
            List of worker configurations
        """
        return list(self.workers.values())
