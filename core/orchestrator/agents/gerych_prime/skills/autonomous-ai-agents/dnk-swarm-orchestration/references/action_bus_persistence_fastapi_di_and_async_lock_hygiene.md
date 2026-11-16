# Action Bus Persistence, FastAPI Dependency Injection & Async Lock Hygiene

## 1. Async Event Loop Lock Trap in Pytest-Asyncio
When building stateful components (Action Buses, Task Queues, Schedulers) in Python:
- An `asyncio.Lock()` instantiated in `__init__` or at module level binds permanently to `asyncio.get_running_loop()`.
- In test runners like `pytest-asyncio` with function-scoped loops (or any environment where event loops are recreated), reusing a singleton object across tests causes `async with self._lock:` to attempt acquiring a lock attached to a closed/different event loop.
- **Symptom**: Tests pass individually (`pytest test_file.py -k test_b`), but hang indefinitely / timeout when run in sequence (`pytest test_file.py`).
- **Pattern**:
  ```python
  @property
  def _lock(self) -> asyncio.Lock:
      try:
          loop = asyncio.get_running_loop()
      except RuntimeError:
          return asyncio.Lock()
      if not hasattr(self, "_active_locks"):
          self._active_locks = {}
      if loop not in self._active_locks:
          self._active_locks[loop] = asyncio.Lock()
      return self._active_locks[loop]
  ```

## 2. From Global Singleton to FastAPI Dependency Injection
- Hardcoded global instances (`get_default_action_bus()`) block multi-tenancy and make unit testing brittle.
- **DI Solution**:
  ```python
  def get_action_bus(request: Request) -> AgentActionBus:
      if hasattr(request.app.state, "action_bus") and request.app.state.action_bus is not None:
          return request.app.state.action_bus
      return get_default_action_bus()

  @router.post("/dispatch")
  async def dispatch(
      request: ActionTaskCreateRequest,
      bus: AgentActionBus = Depends(get_action_bus),
  ): ...
  ```
- **Test Override**:
  ```python
  test_app.dependency_overrides[get_action_bus] = lambda: custom_isolated_bus
  ```

## 3. SQLite WAL Persistence Layer
- SQLite standard library (`sqlite3`) is synchronous. Wrapping DB calls in `asyncio.to_thread` guarantees zero event-loop blocking:
  ```python
  def _write_tx():
      with sqlite3.connect(self._db_path) as conn:
          conn.execute("PRAGMA journal_mode=WAL;")
          conn.execute("INSERT OR REPLACE INTO ...")
  await asyncio.to_thread(_write_tx)
  ```
- Persist:
  1. `action_tasks`: Initial dispatch request and parameters.
  2. `action_results`: Final execution output, stdout/stderr, execution time, and error messages.
  3. `action_events`: Immutable audit trail for replays and dashboard monitoring.

## 4. Non-Blocking Event Subscriber Broadcast
- Avoid awaiting subscriber callbacks sequentially inside `dispatch_task()`. A slow subscriber (e.g. external webhook or LLM hook) would degrade bus throughput.
- **Pattern**:
  ```python
  for sub in list(self._subscribers):
      try:
          res = sub(event)
          if asyncio.iscoroutine(res):
              asyncio.create_task(res)
      except Exception as err:
          logger.warning(f"Subscriber error: {err}")
  ```
