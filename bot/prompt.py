"""
Модуль модели данных Prompt.
Только структура данных - никакой бизнес-логики, никакого I/O.
"""


class Prompt:
    """
    Модель данных для промпта.
    
    Содержит три компонента:
    - role: роль/персона AI
    - task: задание для выполнения
    - answer: формат ответа
    """
    
    TEMPLATE = "role: {role}\ntask: {task}\nanswer: {answer}"
    
    def __init__(self, role: str = "", task: str = "", answer: str = ""):
        """
        Инициализация промпта.
        
        Args:
            role: Описание роли AI
            task: Описание задачи
            answer: Описание формата ответа
        """
        self._role = role
        self._task = task
        self._answer = answer
    
    @property
    def role(self) -> str:
        return self._role
    
    @role.setter
    def role(self, value: str) -> None:
        self._validate(value, "role")
        self._role = value
    
    @property
    def task(self) -> str:
        return self._task
    
    @task.setter
    def task(self, value: str) -> None:
        self._validate(value, "task")
        self._task = value
    
    @property
    def answer(self) -> str:
        return self._answer
    
    @answer.setter
    def answer(self, value: str) -> None:
        self._validate(value, "answer")
        self._answer = value
    
    def _validate(self, value: str, field_name: str) -> None:
        """Валидация значения поля."""
        if not isinstance(value, str):
            raise TypeError(f"{field_name} должен быть строкой")
        if len(value) < 3:
            raise ValueError(f"{field_name} должен содержать минимум 3 символа")
    
    def is_complete(self) -> bool:
        """Проверяет, заполнены ли все поля промпта."""
        return bool(self._role and self._task and self._answer)
    
    def build(self) -> str:
        """
        Собирает финальный промпт из компонентов.
        
        Returns:
            str: Готовый промпт для отправки в LLM
            
        Raises:
            ValueError: Если не все поля заполнены
        """
        if not self.is_complete():
            missing = []
            if not self._role:
                missing.append("role")
            if not self._task:
                missing.append("task")
            if not self._answer:
                missing.append("answer")
            raise ValueError(f"Не заполнены поля: {', '.join(missing)}")
        
        return self.TEMPLATE.format(
            role=self._role,
            task=self._task,
            answer=self._answer
        )
    
    # Алиас для обратной совместимости
    def prompt(self) -> str:
        """Алиас для build() - обратная совместимость."""
        return self.build()
    
    def with_params(self, **kwargs) -> "Prompt":
        """
        Создаёт новый Prompt с подставленными параметрами.
        
        Args:
            **kwargs: Параметры для подстановки в шаблон
            
        Returns:
            Prompt: Новый экземпляр с подставленными параметрами
        """
        new_role = self._role.format(**kwargs) if self._role else ""
        new_task = self._task.format(**kwargs) if self._task else ""
        new_answer = self._answer.format(**kwargs) if self._answer else ""
        return Prompt(role=new_role, task=new_task, answer=new_answer)
    
    def __repr__(self) -> str:
        return f"Prompt(role='{self._role[:30]}...', task='{self._task[:30]}...', answer='{self._answer[:30]}...')"
